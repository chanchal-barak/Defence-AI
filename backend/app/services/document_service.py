from backend.app.services.extractor import extract_text
from backend.app.services.nlp_service import extract_entities
from backend.app.services.classifier import classify_with_explanation
from backend.app.services.anomaly import detect_anomaly
from backend.app.services.risk_service import calculate_risk

from backend.app.database.database import SessionLocal
from backend.app.database.models import DocumentAnalysis


def process_document(
    path: str,
    suffix: str,
    filename: str = "unknown"
) -> dict:

    # ---------------------------------------------
    # 1. Extract text
    # ---------------------------------------------

    text, extraction_meta = extract_text(
        path,
        suffix
    )

    if not text.strip():

        return {
            "status": "error",
            "message": "No text could be extracted.",
            "extraction": extraction_meta,
        }

    # ---------------------------------------------
    # 2. Entity extraction
    # ---------------------------------------------

    entities = extract_entities(text)

    # ---------------------------------------------
    # 3. Classification
    # ---------------------------------------------

    classification = classify_with_explanation(
        text
    )

    # ---------------------------------------------
    # 4. Anomaly detection
    # ---------------------------------------------

    anomaly = detect_anomaly(
        text,
        entities
    )

    # ---------------------------------------------
    # 5. Risk assessment
    # ---------------------------------------------

    risk = calculate_risk(
        text=text,
        category=classification["category"],
        classification_confidence=classification["confidence"],
        is_anomaly=anomaly["is_anomaly"],
        anomaly_score=anomaly["anomaly_score"],
        entities=entities,
    )

    # ---------------------------------------------
    # 6. Save analysis
    # ---------------------------------------------

    db = SessionLocal()

    try:

        record = DocumentAnalysis(

            filename=filename,

            category=classification["category"],

            classification_confidence=(
                classification["confidence"]
            ),

            risk_score=risk["risk_score"],

            priority=risk["priority"],

            is_anomaly=anomaly["is_anomaly"],

            anomaly_score=anomaly["anomaly_score"],

            locations=", ".join(
                entities.get("locations", [])
            ),

            quantities=", ".join(
                entities.get("quantities", [])
            ),

            word_count=extraction_meta.get(
                "word_count",
                0
            ),

            text_preview=text[:3000],
        )

        db.add(record)

        db.commit()

        db.refresh(record)

    finally:

        db.close()

    # ---------------------------------------------
    # 7. Return analysis
    # ---------------------------------------------

    return {

        "status": "success",

        "text_preview": text[:3000],

        "extraction": extraction_meta,

        "entities": entities,

        "classification": classification,

        "anomaly": anomaly,

        "risk": risk,

        "document_id": record.id,
    }