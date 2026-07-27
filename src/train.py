"""Train and evaluate the PhishGuard AI baseline model."""

import json
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score,
    balanced_accuracy_score,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
    roc_auc_score,
)
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import FunctionTransformer

from src.features import canonicalize_urls_for_model


PROJECT_ROOT = Path(__file__).resolve().parents[1]

DATA_FILE = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "phiusiil_clean_urls.csv"
)

MODEL_FILE = (
    PROJECT_ROOT
    / "models"
    / "phishguard_pipeline.joblib"
)

METRICS_FILE = PROJECT_ROOT / "reports" / "metrics.json"
EVALUATION_FILE = PROJECT_ROOT / "reports" / "evaluation.md"

URL_COLUMN = "URL"
TARGET_COLUMN = "is_phishing"

RANDOM_STATE = 42
TEST_SIZE = 0.20
MAX_TRAINING_ROWS = 60_000


def build_pipeline():
    """Create the text-processing and classification pipeline."""

    return Pipeline(
    steps=[
        (
            "canonicalize_url",
            FunctionTransformer(
                canonicalize_urls_for_model,
                validate=False,
            ),
        ),
        (
            "tfidf",
                TfidfVectorizer(
                    analyzer="char",
                    ngram_range=(3, 5),
                    lowercase=True,
                    min_df=2,
                    max_features=30_000,
                    sublinear_tf=True,
                    dtype=np.float32,
                ),
            ),
            (
                "classifier",
                LogisticRegression(
                    solver="saga",
                    max_iter=300,
                    tol=1e-3,
                    random_state=RANDOM_STATE,
                ),
            ),
        ]
    )


def main():
    """Load data, train the model, evaluate it, and save results."""

    if not DATA_FILE.exists():
        raise FileNotFoundError(
            "Clean dataset not found. "
            "Run scripts/preprocess_data.py first."
        )

    print("Loading the clean dataset...")
    data = pd.read_csv(DATA_FILE)

    required_columns = {URL_COLUMN, TARGET_COLUMN}

    if not required_columns.issubset(data.columns):
        raise ValueError(
            f"Required columns are missing: {required_columns}"
        )

    data = data[[URL_COLUMN, TARGET_COLUMN]].dropna().copy()
    data[URL_COLUMN] = data[URL_COLUMN].astype(str)
    data[TARGET_COLUMN] = data[TARGET_COLUMN].astype(int)

    print(f"Available clean records: {len(data):,}")

    train_data, test_data = train_test_split(
        data,
        test_size=TEST_SIZE,
        random_state=RANDOM_STATE,
        stratify=data[TARGET_COLUMN],
    )

    if len(train_data) > MAX_TRAINING_ROWS:
        train_data, _ = train_test_split(
            train_data,
            train_size=MAX_TRAINING_ROWS,
            random_state=RANDOM_STATE,
            stratify=train_data[TARGET_COLUMN],
        )

    x_train = train_data[URL_COLUMN]
    y_train = train_data[TARGET_COLUMN]

    x_test = test_data[URL_COLUMN]
    y_test = test_data[TARGET_COLUMN]

    print(f"Training records used: {len(x_train):,}")
    print(f"Testing records used: {len(x_test):,}")
    print("Building TF-IDF character features...")
    print("Training Logistic Regression...")

    pipeline = build_pipeline()
    pipeline.fit(x_train, y_train)

    predictions = pipeline.predict(x_test)
    phishing_scores = pipeline.predict_proba(x_test)[:, 1]

    tn, fp, fn, tp = confusion_matrix(
        y_test,
        predictions,
        labels=[0, 1],
    ).ravel()

    metrics = {
        "available_clean_records": int(len(data)),
        "training_records": int(len(x_train)),
        "testing_records": int(len(x_test)),
        "majority_baseline_accuracy": float(
            y_test.value_counts(normalize=True).max()
        ),
        "accuracy": float(
            accuracy_score(y_test, predictions)
        ),
        "balanced_accuracy": float(
            balanced_accuracy_score(y_test, predictions)
        ),
        "precision_phishing": float(
            precision_score(
                y_test,
                predictions,
                zero_division=0,
            )
        ),
        "recall_phishing": float(
            recall_score(
                y_test,
                predictions,
                zero_division=0,
            )
        ),
        "f1_phishing": float(
            f1_score(
                y_test,
                predictions,
                zero_division=0,
            )
        ),
        "roc_auc": float(
            roc_auc_score(y_test, phishing_scores)
        ),
        "true_negatives": int(tn),
        "false_positives": int(fp),
        "false_negatives": int(fn),
        "true_positives": int(tp),
    }

    MODEL_FILE.parent.mkdir(parents=True, exist_ok=True)
    METRICS_FILE.parent.mkdir(parents=True, exist_ok=True)

    joblib.dump(
        pipeline,
        MODEL_FILE,
        compress=3,
    )

    with METRICS_FILE.open("w", encoding="utf-8") as file:
        json.dump(metrics, file, indent=2)

    evaluation_text = f"""# Model Evaluation

## Dataset Split

- Available clean records: {metrics["available_clean_records"]:,}
- Training records used: {metrics["training_records"]:,}
- Testing records used: {metrics["testing_records"]:,}
- Positive class: phishing

## Metrics

| Metric | Result |
|---|---:|
| Majority baseline accuracy | {metrics["majority_baseline_accuracy"]:.4f} |
| Accuracy | {metrics["accuracy"]:.4f} |
| Balanced accuracy | {metrics["balanced_accuracy"]:.4f} |
| Phishing precision | {metrics["precision_phishing"]:.4f} |
| Phishing recall | {metrics["recall_phishing"]:.4f} |
| Phishing F1 score | {metrics["f1_phishing"]:.4f} |
| ROC AUC | {metrics["roc_auc"]:.4f} |

## Confusion Matrix

| Actual / Predicted | Legitimate | Phishing |
|---|---:|---:|
| Legitimate | {metrics["true_negatives"]:,} | {metrics["false_positives"]:,} |
| Phishing | {metrics["false_negatives"]:,} | {metrics["true_positives"]:,} |

## Current Limitations

- This is the first baseline model.
- The evaluation uses a random stratified split.
- Similar domains may exist in both training and testing data.
- A future robustness test should separate records by domain.
- The prediction score should not be treated as a security guarantee.
"""

    EVALUATION_FILE.write_text(
        evaluation_text,
        encoding="utf-8",
    )

    print("Training complete.")
    print(f"Accuracy: {metrics['accuracy']:.4f}")
    print(
        f"Phishing precision: "
        f"{metrics['precision_phishing']:.4f}"
    )
    print(
        f"Phishing recall: "
        f"{metrics['recall_phishing']:.4f}"
    )
    print(
        f"Phishing F1: "
        f"{metrics['f1_phishing']:.4f}"
    )
    print(f"ROC AUC: {metrics['roc_auc']:.4f}")
    print(f"False positives: {metrics['false_positives']:,}")
    print(f"False negatives: {metrics['false_negatives']:,}")
    print(f"Model saved to: {MODEL_FILE}")
    print(f"Evaluation saved to: {EVALUATION_FILE}")


if __name__ == "__main__":
    main()