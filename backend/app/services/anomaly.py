from pathlib import Path

import joblib
import numpy as np


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


_model = None


def load_model():

    global _model

    if _model is None:

        if not MODEL_PATH.exists():

            raise FileNotFoundError(
                "Anomaly model not found. "
                "Train it first."
            )

        _model = joblib.load(
            MODEL_PATH
        )

    return _model


def extract_features(
    text: str,
    entities: dict
):

    import re

    words = text.split()

    numbers = re.findall(
        r"\b\d+(?:\.\d+)?\b",
        text
    )

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

    return [
        len(text),
        len(words),
        len(numbers),
        personnel,
        response_time,
        len(re.findall(r"[.!?]+", text)),
        sum(1 for c in text if c.isupper()),
        len(set(word.lower() for word in words)),
    ]


def detect_anomaly(
    text: str,
    entities: dict
):

    model = load_model()

    features = extract_features(
        text,
        entities
    )

    X = np.array(
        [features],
        dtype=float
    )

    prediction = model.predict(X)[0]

    score = model.decision_function(X)[0]

    return {
        "status": (
            "anomaly"
            if prediction == -1
            else "normal"
        ),

        "is_anomaly": bool(
            prediction == -1
        ),

        "anomaly_score": round(
            float(score),
            4
        ),

        "features": {
            column: value
            for column, value
            in zip(
                FEATURE_COLUMNS,
                features
            )
        },

        "model": "StandardScaler + Isolation Forest"
    }