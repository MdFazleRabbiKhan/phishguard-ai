"""Evaluate PhishGuard using a hostname-separated data split."""

import json
from pathlib import Path
from urllib.parse import urlsplit

import pandas as pd
from sklearn.metrics import (
    accuracy_score,
    balanced_accuracy_score,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
    roc_auc_score,
)
from sklearn.model_selection import (
    StratifiedGroupKFold,
    train_test_split,
)

from src.train import (
    DATA_FILE,
    MAX_TRAINING_ROWS,
    RANDOM_STATE,
    TARGET_COLUMN,
    URL_COLUMN,
    build_pipeline,
)


PROJECT_ROOT = Path(__file__).resolve().parents[1]

METRICS_FILE = (
    PROJECT_ROOT
    / "reports"
    / "domain_holdout_metrics.json"
)

EVALUATION_FILE = (
    PROJECT_ROOT
    / "reports"
    / "domain_holdout_evaluation.md"
)


def extract_hostname(url_text):
    """Extract a hostname locally without connecting to the URL."""

    text = str(url_text).strip()

    if "://" not in text:
        text = f"http://{text}"

    try:
        hostname = urlsplit(text).hostname
    except ValueError:
        hostname = None

    if hostname:
        return hostname.lower().rstrip(".")

    # Keep invalid URLs separated using their complete text.
    return f"invalid:{text.lower()}"


def main():
    """Train and test using non-overlapping hostnames."""

    if not DATA_FILE.exists():
        raise FileNotFoundError(
            "Clean dataset not found. "
            "Run scripts/preprocess_data.py first."
        )

    print("Loading the clean dataset...")
    data = pd.read_csv(DATA_FILE)

    data = (
        data[[URL_COLUMN, TARGET_COLUMN]]
        .dropna()
        .reset_index(drop=True)
    )

    data[URL_COLUMN] = data[URL_COLUMN].astype(str)
    data[TARGET_COLUMN] = data[TARGET_COLUMN].astype(int)

    print("Extracting hostnames locally...")
    hostnames = data[URL_COLUMN].map(extract_hostname)

    print(f"Available records: {len(data):,}")
    print(f"Unique hostnames: {hostnames.nunique():,}")

    splitter = StratifiedGroupKFold(
        n_splits=5,
        shuffle=True,
        random_state=RANDOM_STATE,
    )

    train_index, test_index = next(
        splitter.split(
            data[URL_COLUMN],
            data[TARGET_COLUMN],
            groups=hostnames,
        )
    )

    train_data = data.iloc[train_index].copy()
    test_data = data.iloc[test_index].copy()

    if len(train_data) > MAX_TRAINING_ROWS:
        train_data, _ = train_test_split(
            train_data,
            train_size=MAX_TRAINING_ROWS,
            random_state=RANDOM_STATE,
            stratify=train_data[TARGET_COLUMN],
        )

    train_hostnames = set(
        train_data[URL_COLUMN].map(extract_hostname)
    )

    test_hostnames = set(
        test_data[URL_COLUMN].map(extract_hostname)
    )

    overlapping_hostnames = (
        train_hostnames.intersection(test_hostnames)
    )

    if overlapping_hostnames:
        raise ValueError(
            "Hostname leakage detected between training and testing."
        )

    x_train = train_data[URL_COLUMN]
    y_train = train_data[TARGET_COLUMN]

    x_test = test_data[URL_COLUMN]
    y_test = test_data[TARGET_COLUMN]

    print(f"Training records used: {len(x_train):,}")
    print(f"Testing records used: {len(x_test):,}")
    print(f"Training hostnames: {len(train_hostnames):,}")
    print(f"Testing hostnames: {len(test_hostnames):,}")
    print("Overlapping hostnames: 0")
    print("Training domain-separated model...")

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
        "training_records": int(len(x_train)),
        "testing_records": int(len(x_test)),
        "training_hostnames": int(len(train_hostnames)),
        "testing_hostnames": int(len(test_hostnames)),
        "overlapping_hostnames": 0,
        "training_phishing_rate": float(y_train.mean()),
        "testing_phishing_rate": float(y_test.mean()),
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

    METRICS_FILE.parent.mkdir(parents=True, exist_ok=True)

    with METRICS_FILE.open("w", encoding="utf-8") as file:
        json.dump(metrics, file, indent=2)

    evaluation_text = f"""# Domain-Separated Evaluation

## Purpose

This evaluation prevents the same hostname from appearing in both
training and testing data. It provides a harder test on unseen websites.

## Dataset Split

- Training records: {metrics["training_records"]:,}
- Testing records: {metrics["testing_records"]:,}
- Training hostnames: {metrics["training_hostnames"]:,}
- Testing hostnames: {metrics["testing_hostnames"]:,}
- Overlapping hostnames: {metrics["overlapping_hostnames"]}
- Training phishing rate: {metrics["training_phishing_rate"]:.4f}
- Testing phishing rate: {metrics["testing_phishing_rate"]:.4f}

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

## Interpretation

This test is more realistic than a normal random split because test
hostnames are not present in the training data. Results may still vary
on new phishing campaigns and real-world data.
"""

    EVALUATION_FILE.write_text(
        evaluation_text,
        encoding="utf-8",
    )

    print("Domain-separated evaluation complete.")
    print(f"Accuracy: {metrics['accuracy']:.4f}")
    print(
        f"Balanced accuracy: "
        f"{metrics['balanced_accuracy']:.4f}"
    )
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
    print(f"Report saved to: {EVALUATION_FILE}")


if __name__ == "__main__":
    main()