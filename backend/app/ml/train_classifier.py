from pathlib import Path
import json

import pandas as pd
import joblib

from sklearn.model_selection import (
    train_test_split,
    StratifiedKFold,
    cross_validate
)

from sklearn.feature_extraction.text import TfidfVectorizer

from sklearn.linear_model import LogisticRegression
from sklearn.svm import LinearSVC
from sklearn.naive_bayes import MultinomialNB

from sklearn.pipeline import Pipeline

from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix
)


DATA_PATH = Path(
    "data/labels/document_labels.csv"
)

DOCUMENT_DIR = Path(
    "data/raw/documents"
)

MODEL_DIR = Path("models")

EVALUATION_DIR = Path(
    "data/evaluation"
)


MODEL_DIR.mkdir(
    parents=True,
    exist_ok=True
)

EVALUATION_DIR.mkdir(
    parents=True,
    exist_ok=True
)


# =========================================
# LOAD DATASET
# =========================================

def load_dataset():

    if not DATA_PATH.exists():

        raise FileNotFoundError(
            f"Label file not found: {DATA_PATH}"
        )

    df = pd.read_csv(
        DATA_PATH
    )

    texts = []
    labels = []

    for _, row in df.iterrows():

        path = (
            DOCUMENT_DIR /
            row["filename"]
        )

        if not path.exists():

            raise FileNotFoundError(
                f"Document not found: {path}"
            )

        text = path.read_text(
            encoding="utf-8"
        )

        texts.append(text)
        labels.append(
            row["category"]
        )

    return texts, labels


# =========================================
# BUILD MODEL
# =========================================

def build_model(classifier):

    return Pipeline([

        (
            "tfidf",

            TfidfVectorizer(
                lowercase=True,
                stop_words="english",
                ngram_range=(1, 2),
                max_features=5000
            )
        ),

        (
            "classifier",
            classifier
        )
    ])


# =========================================
# MODEL DEFINITIONS
# =========================================

def get_models():

    return {

        "Logistic Regression":
            LogisticRegression(
                max_iter=1000
            ),

        "Linear SVM":
            LinearSVC(
                max_iter=5000
            ),

        "Multinomial Naive Bayes":
            MultinomialNB()
    }


# =========================================
# MODEL COMPARISON
# =========================================

def compare_models(
    texts,
    labels
):

    print(
        "\n========================================="
    )

    print(
        "MODEL COMPARISON"
    )

    print(
        "========================================="
    )

    cv = StratifiedKFold(
        n_splits=5,
        shuffle=True,
        random_state=42
    )

    models = get_models()

    results = {}

    for name, classifier in models.items():

        print(
            f"\nEvaluating: {name}"
        )

        model = build_model(
            classifier
        )

        scores = cross_validate(
            model,
            texts,
            labels,
            cv=cv,
            scoring=[
                "accuracy",
                "precision_macro",
                "recall_macro",
                "f1_macro"
            ],
            return_train_score=False
        )

        accuracy = scores[
            "test_accuracy"
        ]

        precision = scores[
            "test_precision_macro"
        ]

        recall = scores[
            "test_recall_macro"
        ]

        f1 = scores[
            "test_f1_macro"
        ]

        results[name] = {

            "accuracy": {
                "mean": float(
                    accuracy.mean()
                ),
                "std": float(
                    accuracy.std()
                ),
                "folds": [
                    float(x)
                    for x in accuracy
                ]
            },

            "precision_macro": {
                "mean": float(
                    precision.mean()
                ),
                "std": float(
                    precision.std()
                ),
                "folds": [
                    float(x)
                    for x in precision
                ]
            },

            "recall_macro": {
                "mean": float(
                    recall.mean()
                ),
                "std": float(
                    recall.std()
                ),
                "folds": [
                    float(x)
                    for x in recall
                ]
            },

            "f1_macro": {
                "mean": float(
                    f1.mean()
                ),
                "std": float(
                    f1.std()
                ),
                "folds": [
                    float(x)
                    for x in f1
                ]
            }
        }

        print(
            f"Accuracy : "
            f"{accuracy.mean():.4f} "
            f"+/- "
            f"{accuracy.std():.4f}"
        )

        print(
            f"Precision: "
            f"{precision.mean():.4f} "
            f"+/- "
            f"{precision.std():.4f}"
        )

        print(
            f"Recall   : "
            f"{recall.mean():.4f} "
            f"+/- "
            f"{recall.std():.4f}"
        )

        print(
            f"F1       : "
            f"{f1.mean():.4f} "
            f"+/- "
            f"{f1.std():.4f}"
        )

    return results


# =========================================
# SELECT BEST MODEL
# =========================================

def select_best_model(
    results
):

    best_model = max(
        results,
        key=lambda name:
        results[name][
            "f1_macro"
        ]["mean"]
    )

    return best_model


# =========================================
# FINAL TRAINING
# =========================================

def train_final_model(
    model_name,
    texts,
    labels
):

    models = get_models()

    classifier = models[
        model_name
    ]

    model = build_model(
        classifier
    )

    print(
        f"\nTraining final model: "
        f"{model_name}"
    )

    model.fit(
        texts,
        labels
    )

    model_path = (
        MODEL_DIR /
        "document_classifier.joblib"
    )

    joblib.dump(
        model,
        model_path
    )

    print(
        f"Model saved to: "
        f"{model_path}"
    )

    return model


# =========================================
# HOLDOUT EVALUATION
# =========================================

def evaluate_holdout(
    model_name,
    texts,
    labels
):

    X_train, X_test, y_train, y_test = (
        train_test_split(
            texts,
            labels,
            test_size=0.2,
            random_state=42,
            stratify=labels
        )
    )

    holdout_model = build_model(
        get_models()[model_name]
    )

    holdout_model.fit(
        X_train,
        y_train
    )

    predictions = (
        holdout_model.predict(
            X_test
        )
    )

    accuracy = accuracy_score(
        y_test,
        predictions
    )

    report = classification_report(
        y_test,
        predictions,
        output_dict=True,
        zero_division=0
    )

    matrix = confusion_matrix(
        y_test,
        predictions
    )

    print(
        f"\nHoldout Accuracy: "
        f"{accuracy:.4f}"
    )

    print(
        "\nClassification Report:"
    )

    print(
        classification_report(
            y_test,
            predictions,
            zero_division=0
        )
    )

    print(
        "\nConfusion Matrix:"
    )

    print(matrix)

    return {
        "accuracy": float(accuracy),
        "classification_report": report,
        "confusion_matrix": matrix.tolist(),
        "train_size": len(X_train),
        "test_size": len(X_test)
    }


# =========================================
# MAIN TRAINING PIPELINE
# =========================================

def train():

    print(
        "Loading dataset..."
    )

    texts, labels = load_dataset()

    print(
        f"Total documents: "
        f"{len(texts)}"
    )

    print(
        "\nClass distribution:"
    )

    print(
        pd.Series(labels).value_counts()
    )

    # -------------------------------------
    # Compare models
    # -------------------------------------

    comparison = compare_models(
        texts,
        labels
    )

    # -------------------------------------
    # Select best
    # -------------------------------------

    best_model = select_best_model(
        comparison
    )

    print(
        f"\nBest model: "
        f"{best_model}"
    )

    # -------------------------------------
    # Train final model
    # -------------------------------------

    final_model = train_final_model(
        best_model,
        texts,
        labels
    )

    # -------------------------------------
    # Holdout evaluation
    # -------------------------------------

    

    holdout = evaluate_holdout(
        best_model,
        texts,
        labels
    )

    # -------------------------------------
    # Save evaluation
    # -------------------------------------

    evaluation = {

        "dataset": {
            "total_documents":
                len(texts),

            "classes":
                sorted(
                    set(labels)
                )
        },

        "configuration": {

            "cv_folds": 5,

            "test_size": 0.2,

            "random_state": 42,

            "vectorizer": "TF-IDF",

            "ngram_range": [1, 2],

            "max_features": 5000
        },

        "model_comparison":
            comparison,

        "selected_model":
            best_model,

        "holdout":
            holdout
    }

    evaluation_path = (
        EVALUATION_DIR /
        "model_comparison.json"
    )

    with evaluation_path.open(
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            evaluation,
            file,
            indent=4
        )

    print(
        f"\nEvaluation saved to: "
        f"{evaluation_path}"
    )


if __name__ == "__main__":

    train()