from pathlib import Path
import re
import pandas as pd


DOCUMENT_DIR = Path("data/raw/documents")
LABEL_FILE = Path("data/labels/document_labels.csv")
OUTPUT_FILE = Path("data/processed/anomaly_features.csv")


def extract_features(text: str, filename: str, category: str):

    words = text.split()

    numbers = re.findall(r"\b\d+(?:\.\d+)?\b", text)

    personnel_match = re.search(
        r"(\d+)\s+personnel",
        text,
        re.IGNORECASE
    )

    time_match = re.search(
        r"(\d+)\s+minutes",
        text,
        re.IGNORECASE
    )

    personnel = (
        int(personnel_match.group(1))
        if personnel_match
        else 0
    )

    response_time = (
        int(time_match.group(1))
        if time_match
        else 0
    )

    return {
        "filename": filename,
        "category": category,

        "character_count": len(text),
        "word_count": len(words),

        "numeric_count": len(numbers),

        "personnel_count": personnel,

        "response_time": response_time,

        "sentence_count": len(
            re.findall(
                r"[.!?]+",
                text
            )
        ),

        "uppercase_count": sum(
            1 for c in text if c.isupper()
        ),

        "unique_word_count": len(
            set(word.lower() for word in words)
        ),
    }


def main():

    labels = pd.read_csv(
        LABEL_FILE
    )

    records = []

    for _, row in labels.iterrows():

        path = DOCUMENT_DIR / row["filename"]

        if not path.exists():
            continue

        text = path.read_text(
            encoding="utf-8",
            errors="ignore"
        )

        features = extract_features(
            text,
            row["filename"],
            row["category"]
        )

        records.append(features)

    df = pd.DataFrame(records)

    OUTPUT_FILE.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    df.to_csv(
        OUTPUT_FILE,
        index=False
    )

    print(
        f"Created anomaly dataset: {len(df)} documents"
    )

    print("\nFeature columns:")

    print(
        list(df.columns)
    )

    print("\nPreview:")

    print(
        df.head()
    )


if __name__ == "__main__":
    main()