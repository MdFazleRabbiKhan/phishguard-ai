"""Compare decision thresholds using hostname-separated validation data."""

import json
from pathlib import Path
from urllib.parse import urlsplit

import pandas as pd
from sklearn.metrics import (
    balanced_accuracy_score,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
)
from sklearn.model_selection import (
    StratifiedGroupKFold,
    train_test_split,
)

from src.features import (
    canonicalize_url_for_model,
    canonicalize_urls_for_model,
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

OUTPUT_FILE = (
    PROJECT_ROOT
    / "reports"
    / "experiments"
    / "threshold_comparison.json"
)

THRESHOLDS = [
    0.20,
    0.25,
    0.30,
    0.35,
    0.40,
    0.45,
    0.50,
    0.55,
    0.60,
]


def hostname_group(value: str) -> str:
    """Return a normalized hostname for separating the data."""

    model_text = canonicalize_url_for_model(str(value))

    try:
        hostname = urlsplit(
            f"http://{model_text}"
        ).hostname
    except ValueError:
        hostname = None

    return (
        hostname or f"invalid:{model_text}"
    ).lower().rstrip(".")


def main() -> None:
    """Train on development data and compare validation thresholds."""

    print("Loading clean dataset...")

    data = pd.read_csv(DATA_FILE)[
        [URL_COLUMN, TARGET_COLUMN]
    ].dropna()

    data = data.reset_index(drop=True)
    data[URL_COLUMN] = data[URL_COLUMN].astype(str)
    data[TARGET_COLUMN] = data[TARGET_COLUMN].astype(int)

    groups = data[URL_COLUMN].map(hostname_group)

    # Create an outer test set but do not use it.
    outer_splitter = StratifiedGroupKFold(
        n_splits=5,
        shuffle=True,
        random_state=RANDOM_STATE,
    )

    development_index, _ = next(
        outer_splitter.split(
            data[URL_COLUMN],
            data[TARGET_COLUMN],
            groups=groups,
        )
    )

    development = data.iloc[
        development_index
    ].reset_index(drop=True)

    development_groups = development[
        URL_COLUMN
    ].map(hostname_group)

    # Split development data into training and validation data.
    inner_splitter = StratifiedGroupKFold(
        n_splits=5,
        shuffle=True,
        random_state=RANDOM_STATE + 1,
    )

    train_index, validation_index = next(
        inner_splitter.split(
            development[URL_COLUMN],
            development[TARGET_COLUMN],
            groups=development_groups,
        )
    )

    training = development.iloc[train_index].copy()
    validation = development.iloc[
        validation_index
    ].copy()

    if len(training) > MAX_TRAINING_ROWS:
        training, _ = train_test_split(
            training,
            train_size=MAX_TRAINING_ROWS,
            stratify=training[TARGET_COLUMN],
            random_state=RANDOM_STATE,
        )

    training_groups = set(
        training[URL_COLUMN].map(hostname_group)
    )
    validation_groups = set(
        validation[URL_COLUMN].map(hostname_group)
    )

    overlap = training_groups & validation_groups

    if overlap:
        raise RuntimeError(
            "Training and validation hostnames overlap."
        )

    x_train = canonicalize_urls_for_model(
        training[URL_COLUMN].tolist()
    )
    y_train = training[TARGET_COLUMN]

    x_validation = canonicalize_urls_for_model(
        validation[URL_COLUMN].tolist()
    )
    y_validation = validation[TARGET_COLUMN]

    print(f"Training records: {len(training):,}")
    print(f"Validation records: {len(validation):,}")
    print(f"Overlapping hostnames: {len(overlap)}")
    print("Training validation model...")

    model = build_pipeline()
    model.fit(x_train, y_train)

    phishing_class_index = list(
        model.classes_
    ).index(1)

    probabilities = model.predict_proba(
        x_validation
    )[:, phishing_class_index]

    results = []

    print()
    print(
        f"{'Threshold':>9} "
        f"{'Precision':>10} "
        f"{'Recall':>8} "
        f"{'F1':>8} "
        f"{'Bal Acc':>8} "
        f"{'FP':>7} "
        f"{'FN':>7}"
    )
    print("-" * 73)

    for threshold in THRESHOLDS:
        predictions = (
            probabilities >= threshold
        ).astype(int)

        tn, fp, fn, tp = confusion_matrix(
            y_validation,
            predictions,
            labels=[0, 1],
        ).ravel()

        row = {
            "threshold": threshold,
            "precision_phishing": precision_score(
                y_validation,
                predictions,
                zero_division=0,
            ),
            "recall_phishing": recall_score(
                y_validation,
                predictions,
                zero_division=0,
            ),
            "f1_phishing": f1_score(
                y_validation,
                predictions,
                zero_division=0,
            ),
            "balanced_accuracy": balanced_accuracy_score(
                y_validation,
                predictions,
            ),
            "true_negatives": int(tn),
            "false_positives": int(fp),
            "false_negatives": int(fn),
            "true_positives": int(tp),
        }

        results.append(row)

        print(
            f"{threshold:>9.2f} "
            f"{row['precision_phishing']:>10.4f} "
            f"{row['recall_phishing']:>8.4f} "
            f"{row['f1_phishing']:>8.4f} "
            f"{row['balanced_accuracy']:>8.4f} "
            f"{fp:>7,} "
            f"{fn:>7,}"
        )

    report = {
        "purpose": (
            "Compare thresholds using hostname-separated "
            "validation data. The final hostname holdout "
            "was not used for threshold selection."
        ),
        "training_records": len(training),
        "validation_records": len(validation),
        "overlapping_hostnames": len(overlap),
        "threshold_results": results,
    }

    OUTPUT_FILE.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    OUTPUT_FILE.write_text(
        json.dumps(report, indent=2) + "\n",
        encoding="utf-8",
    )

    print()
    print(f"Report saved to: {OUTPUT_FILE}")


if __name__ == "__main__":
    main()