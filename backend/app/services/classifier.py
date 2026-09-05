from pathlib import Path
import joblib
import numpy as np


MODEL_PATH = Path("models/document_classifier.joblib")

_model = None


def load_model():
    global _model

    if _model is None:

        if not MODEL_PATH.exists():
            raise FileNotFoundError(
                f"Model not found: {MODEL_PATH}. "
                "Train the classifier first."
            )

        _model = joblib.load(MODEL_PATH)

    return _model


def _get_scores(model, text: str):
    """
    Get normalized confidence-like scores for classifiers
    that may or may not support predict_proba().
    """

    # Logistic Regression / models with predict_proba()
    if hasattr(model, "predict_proba"):
        probabilities = model.predict_proba([text])[0]

    # Linear SVM
    elif hasattr(model, "decision_function"):
        decision_scores = model.decision_function([text])[0]

        # Convert decision scores into normalized scores
        exp_scores = np.exp(
            decision_scores - np.max(decision_scores)
        )

        probabilities = exp_scores / exp_scores.sum()

    else:
        raise RuntimeError(
            "The loaded classifier does not support "
            "predict_proba() or decision_function()."
        )

    classes = model.classes_

    scores = {
        str(class_name): round(float(score), 4)
        for class_name, score in zip(classes, probabilities)
    }

    confidence = max(scores.values())

    return scores, confidence


def classify_with_explanation(text: str) -> dict:

    model = load_model()

    prediction = model.predict([text])[0]

    scores, confidence = _get_scores(model, text)

    return {
        "category": str(prediction),
        "confidence": round(confidence, 4),
        "scores": scores,
        "model": "TF-IDF + Linear SVM",
        "features": {
            "vectorizer": "TF-IDF",
            "ngram_range": "(1, 2)",
            "max_features": 5000
        }
    }


def classify_text(text: str) -> dict:

    model = load_model()

    prediction = model.predict([text])[0]

    scores, confidence = _get_scores(model, text)

    return {
        "category": str(prediction),
        "confidence": round(confidence, 4),
        "scores": scores,
        "model": "TF-IDF + Linear SVM",
        "features": {
            "vectorizer": "TF-IDF",
            "ngram_range": "(1, 2)",
            "max_features": 5000
        }
    }