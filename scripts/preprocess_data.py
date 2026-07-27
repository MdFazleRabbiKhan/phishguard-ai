"""Validate and clean URL text without visiting any website."""

from pathlib import Path

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[1]

INPUT_FILE = (
    PROJECT_ROOT / "data" / "raw" / "phiusiil_urls.csv"
)

OUTPUT_FILE = (
    PROJECT_ROOT / "data" / "processed" / "phiusiil_clean_urls.csv"
)

URL_COLUMN = "URL"
TARGET_COLUMN = "is_phishing"
MIN_URL_LENGTH = 4
MAX_URL_LENGTH = 2048


def main():
    """Clean URL text and save a training-ready dataset."""

    if not INPUT_FILE.exists():
        raise FileNotFoundError(
            "Dataset not found. Run scripts/download_data.py first."
        )

    print("Loading URL dataset...")
    data = pd.read_csv(INPUT_FILE)

    required_columns = {URL_COLUMN, TARGET_COLUMN}

    if not required_columns.issubset(data.columns):
        raise ValueError(
            f"Required columns are missing: {required_columns}"
        )

    data = data[[URL_COLUMN, TARGET_COLUMN]].copy()
    original_rows = len(data)

    missing_rows = int(data.isna().any(axis=1).sum())
    data = data.dropna(subset=[URL_COLUMN, TARGET_COLUMN])

    data[URL_COLUMN] = data[URL_COLUMN].astype(str).str.strip()
    empty_rows = int(data[URL_COLUMN].eq("").sum())
    data = data.loc[data[URL_COLUMN].ne("")].copy()

    url_lengths = data[URL_COLUMN].str.len()
    invalid_length_mask = ~url_lengths.between(
        MIN_URL_LENGTH,
        MAX_URL_LENGTH,
    )

    invalid_length_rows = int(invalid_length_mask.sum())
    data = data.loc[~invalid_length_mask].copy()

    data[TARGET_COLUMN] = data[TARGET_COLUMN].astype(int)
    valid_labels = set(data[TARGET_COLUMN].unique())

    if not valid_labels.issubset({0, 1}):
        raise ValueError(
            f"Unexpected target values: {valid_labels}"
        )

    exact_duplicates = int(
        data.duplicated(
            subset=[URL_COLUMN, TARGET_COLUMN]
        ).sum()
    )

    # Detect the same URL having two different labels.
    conflicting_mask = (
        data.groupby(
            URL_COLUMN,
            sort=False,
        )[TARGET_COLUMN]
        .transform("nunique")
        .gt(1)
    )

    conflicting_rows = int(conflicting_mask.sum())

    clean_data = (
        data.loc[~conflicting_mask]
        .drop_duplicates(subset=[URL_COLUMN])
        .reset_index(drop=True)
    )

    if clean_data.empty:
        raise ValueError("No usable records remain after cleaning.")

    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    clean_data.to_csv(OUTPUT_FILE, index=False)

    total_removed = original_rows - len(clean_data)
    counts = clean_data[TARGET_COLUMN].value_counts()

    print(f"Original rows: {original_rows:,}")
    print(f"Rows with missing values: {missing_rows:,}")
    print(f"Empty URL rows: {empty_rows:,}")
    print(f"Invalid-length rows: {invalid_length_rows:,}")
    print(f"Exact duplicate URLs: {exact_duplicates:,}")
    print(f"Conflicting-label rows: {conflicting_rows:,}")
    print(f"Total rows removed: {total_removed:,}")
    print(f"Final rows: {len(clean_data):,}")
    print(f"Legitimate records: {counts.get(0, 0):,}")
    print(f"Phishing records: {counts.get(1, 0):,}")
    print(f"Clean dataset saved to: {OUTPUT_FILE}")
    print("Security: URLs remained plain text and were never opened.")


if __name__ == "__main__":
    main()