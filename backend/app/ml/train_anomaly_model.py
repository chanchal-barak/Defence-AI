from pathlib import Path

import pandas as pd
import joblib

from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline


DATA_PATH = Path(
    "data/processed/anomaly_features.csv"
)

MODEL_PATH = Path(
    "models/anomaly_detector.joblib"
)


FEATURE_COLUMNS = [
    "character_count",
    "word_count",
    "numeric_count",
    "personnel_count",
    "response_time",
    "sentence_count",
    "uppercase_count",
    "unique_word_count",
]


def train():

    print("Loading anomaly dataset...")

    df = pd.read_csv(
        DATA_PATH
    )

    X = df[FEATURE_COLUMNS]

    print(
        f"Documents: {len(X)}"
    )

    print(
        f"Features: {len(FEATURE_COLUMNS)}"
    )

    pipeline = Pipeline([
        (
            "scaler",
            StandardScaler()
        ),

        (
            "isolation_forest",
            IsolationForest(
                n_estimators=200,
                contamination=0.10,
                random_state=42
            )
        )
    ])

    print("\nTraining Isolation Forest...")

    pipeline.fit(X)

    predictions = pipeline.predict(X)

    scores = pipeline[
        "isolation_forest"
    ].decision_function(
        pipeline["scaler"].transform(X)
    )

    df["anomaly_prediction"] = predictions

    df["anomaly_score"] = scores

    df["is_anomaly"] = (
        predictions == -1
    )

    MODEL_PATH.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    joblib.dump(
        pipeline,
        MODEL_PATH
    )

    output_path = Path(
        "data/processed/anomaly_results.csv"
    )

    df.to_csv(
        output_path,
        index=False
    )

    print(
        f"\nModel saved to: {MODEL_PATH}"
    )

    print(
        f"Results saved to: {output_path}"
    )

    print("\nAnomaly summary:")

    print(
        df["is_anomaly"].value_counts()
    )

    print("\nMost anomalous documents:")

    print(
        df.sort_values(
            "anomaly_score"
        )[
            [
                "filename",
                "category",
                "anomaly_score",
                "is_anomaly"
            ]
        ].head(10)
    )


if __name__ == "__main__":
    train()