"""Download a safe numerical subset of the PhiUSIIL dataset."""

from pathlib import Path

from ucimlrepo import fetch_ucirepo


DATASET_ID = 967

PROJECT_ROOT = Path(__file__).resolve().parents[1]
OUTPUT_FILE = (
    PROJECT_ROOT / "data" / "raw" / "phiusiil_safe_features.csv"
)

SAFE_FEATURES = [
    "URLLength",
    "DomainLength",
    "IsDomainIP",
    "TLDLength",
    "NoOfSubDomain",
    "HasObfuscation",
    "NoOfObfuscatedChar",
    "ObfuscationRatio",
    "NoOfLettersInURL",
    "LetterRatioInURL",
    "NoOfDegitsInURL",
    "DegitRatioInURL",
    "NoOfEqualsInURL",
    "NoOfQMarkInURL",
    "NoOfAmpersandInURL",
    "NoOfOtherSpecialCharsInURL",
    "SpacialCharRatioInURL",
    "IsHTTPS",
]


def main():
    """Download the dataset and save only safe URL-based features."""

    print("Downloading the PhiUSIIL dataset from UCI...")

    dataset = fetch_ucirepo(id=DATASET_ID)
    features = dataset.data.features
    targets = dataset.data.targets

    missing_columns = [
        column for column in SAFE_FEATURES
        if column not in features.columns
    ]

    if missing_columns:
        raise ValueError(
            f"Dataset is missing expected columns: {missing_columns}"
        )

    if "label" not in targets.columns:
        raise ValueError("The dataset does not contain the label column.")

    safe_data = features[SAFE_FEATURES].copy()

    # In the original dataset:
    # 0 means phishing and 1 means legitimate.
    # We convert it so 1 means phishing.
    safe_data["is_phishing"] = (
        targets["label"].astype(int) == 0
    ).astype(int)

    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    safe_data.to_csv(OUTPUT_FILE, index=False)

    counts = safe_data["is_phishing"].value_counts()

    print(f"Saved {len(safe_data):,} rows.")
    print(f"Saved {len(safe_data.columns)} columns.")
    print(f"Legitimate records: {counts.get(0, 0):,}")
    print(f"Phishing records: {counts.get(1, 0):,}")
    print(f"File location: {OUTPUT_FILE}")


if __name__ == "__main__":
    main()