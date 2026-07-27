"""Download URL text and labels from the PhiUSIIL dataset.

URLs are stored only as text. This script never visits any website.
"""

from pathlib import Path

from ucimlrepo import fetch_ucirepo


DATASET_ID = 967

PROJECT_ROOT = Path(__file__).resolve().parents[1]
OUTPUT_FILE = (
    PROJECT_ROOT / "data" / "raw" / "phiusiil_urls.csv"
)


def main():
    """Download only URL text and its phishing label."""

    print("Downloading the PhiUSIIL dataset from UCI...")

    dataset = fetch_ucirepo(id=DATASET_ID)
    features = dataset.data.features
    targets = dataset.data.targets

    if "URL" not in features.columns:
        raise ValueError("The dataset does not contain the URL column.")

    if "label" not in targets.columns:
        raise ValueError("The dataset does not contain the label column.")

    data = features[["URL"]].copy()

    # Original labels:
    # 0 = phishing and 1 = legitimate.
    # Our project uses 1 = phishing and 0 = legitimate.
    data["is_phishing"] = (
        targets["label"].astype(int) == 0
    ).astype(int)

    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    data.to_csv(OUTPUT_FILE, index=False)

    counts = data["is_phishing"].value_counts()

    print(f"Saved {len(data):,} rows.")
    print(f"Saved {len(data.columns)} columns.")
    print(f"Legitimate records: {counts.get(0, 0):,}")
    print(f"Phishing records: {counts.get(1, 0):,}")
    print(f"File location: {OUTPUT_FILE}")
    print("Security: No URL was opened or visited.")


if __name__ == "__main__":
    main()