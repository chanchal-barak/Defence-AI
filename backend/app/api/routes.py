from pathlib import Path
from tempfile import NamedTemporaryFile
from typing_extensions import Annotated
from sqlalchemy.orm import Session
from fastapi import Depends

from backend.app.database.database import get_db
from backend.app.database.models import DocumentAnalysis
from fastapi import APIRouter, File, UploadFile, HTTPException
from fastapi.responses import Response
from backend.app.services.report_service import (
    generate_json_report,
    generate_csv_report,
    generate_pdf_report,
)
from backend.app.services.document_service import process_document


router = APIRouter(
    prefix="/api",
    tags=["documents"]
)

ALLOWED = {".pdf", ".txt"}


@router.post("/analyze")
async def analyze_document(
    file: UploadFile = File(...)
):

    suffix = Path(
        file.filename or ""
    ).suffix.lower()

    if suffix not in ALLOWED:

        raise HTTPException(
            status_code=400,
            detail="Only PDF and TXT files are supported."
        )

    content = await file.read()

    if not content:

        raise HTTPException(
            status_code=400,
            detail="Empty file."
        )

    with NamedTemporaryFile(
        delete=False,
        suffix=suffix
    ) as tmp:

        tmp.write(content)
        path = tmp.name

    try:

        return process_document(
            path,
            suffix,
            file.filename or "unknown"
        )

    finally:

        Path(path).unlink(
            missing_ok=True
        )

@router.post("/analyze/batch")
async def analyze_batch(
    files: Annotated[list[UploadFile], File(...)]
):

    if not files:
        raise HTTPException(
            status_code=400,
            detail="No files uploaded."
        )

    results = []

    for file in files:

        suffix = Path(
            file.filename or ""
        ).suffix.lower()

        if suffix not in ALLOWED:

            results.append({
                "filename": file.filename,
                "status": "error",
                "message": (
                    "Only PDF and TXT files are supported."
                )
            })

            continue

        content = await file.read()

        if not content:

            results.append({
                "filename": file.filename,
                "status": "error",
                "message": "Empty file."
            })

            continue

        with NamedTemporaryFile(
            delete=False,
            suffix=suffix
        ) as tmp:

            tmp.write(content)
            path = tmp.name

        try:

            result = process_document(
                path,
                suffix,
                file.filename or "unknown"
            )

            results.append({
                "filename": file.filename,
                **result
            })

        except Exception as e:

            results.append({
                "filename": file.filename,
                "status": "error",
                "message": str(e)
            })

        finally:

            Path(path).unlink(
                missing_ok=True
            )

    successful = sum(
        1
        for result in results
        if result.get("status") == "success"
    )

    failed = len(results) - successful

    return {
        "status": "completed",
        "total_files": len(files),
        "successful": successful,
        "failed": failed,
        "results": results
    }


@router.get("/documents")
def get_documents(
    category: str | None = None,
    priority: str | None = None,
    anomaly: bool | None = None,
    location: str | None = None,
    search: str | None = None,
    min_risk: int | None = None,
    db: Session = Depends(get_db),
):

    query = db.query(DocumentAnalysis)

    # -----------------------------------------
    # Category filter
    # -----------------------------------------

    if category:

        query = query.filter(
            DocumentAnalysis.category == category
        )

    # -----------------------------------------
    # Priority filter
    # -----------------------------------------

    if priority:

        query = query.filter(
            DocumentAnalysis.priority == priority.upper()
        )

    # -----------------------------------------
    # Anomaly filter
    # -----------------------------------------

    if anomaly is not None:

        query = query.filter(
            DocumentAnalysis.is_anomaly == anomaly
        )

    # -----------------------------------------
    # Location filter
    # -----------------------------------------

    if location:

        query = query.filter(
            DocumentAnalysis.locations.ilike(
                f"%{location}%"
            )
        )

    # -----------------------------------------
    # Text / filename search
    # -----------------------------------------

    if search:

        search_pattern = f"%{search}%"

        query = query.filter(
            (
                DocumentAnalysis.filename.ilike(
                    search_pattern
                )
            )
            |
            (
                DocumentAnalysis.text_preview.ilike(
                    search_pattern
                )
            )
            |
            (
                DocumentAnalysis.locations.ilike(
                    search_pattern
                )
            )
            |
            (
                DocumentAnalysis.quantities.ilike(
                    search_pattern
                )
            )
        )

    # -----------------------------------------
    # Minimum risk
    # -----------------------------------------

    if min_risk is not None:

        query = query.filter(
            DocumentAnalysis.risk_score >= min_risk
        )

    # -----------------------------------------
    # Newest first
    # -----------------------------------------

    documents = (
        query
        .order_by(
            DocumentAnalysis.created_at.desc()
        )
        .all()
    )

    # -----------------------------------------
    # Response
    # -----------------------------------------

    return [
        {
            "id": document.id,
            "filename": document.filename,
            "category": document.category,
            "classification_confidence": (
                document.classification_confidence
            ),
            "risk_score": document.risk_score,
            "priority": document.priority,
            "is_anomaly": document.is_anomaly,
            "anomaly_score": document.anomaly_score,
            "locations": document.locations,
            "quantities": document.quantities,
            "word_count": document.word_count,
            "created_at": (
                document.created_at.isoformat()
            ),
        }
        for document in documents
    ]

@router.get("/documents/{document_id}")
def get_document(
    document_id: int,
    db: Session = Depends(get_db)
):

    document = (
        db.query(DocumentAnalysis)
        .filter(
            DocumentAnalysis.id == document_id
        )
        .first()
    )

    if not document:

        raise HTTPException(
            status_code=404,
            detail="Document not found."
        )

    return {
        "id": document.id,
        "filename": document.filename,
        "category": document.category,
        "classification_confidence": (
            document.classification_confidence
        ),
        "risk_score": document.risk_score,
        "priority": document.priority,
        "is_anomaly": document.is_anomaly,
        "anomaly_score": document.anomaly_score,
        "locations": document.locations,
        "quantities": document.quantities,
        "word_count": document.word_count,
        "text_preview": document.text_preview,
        "created_at": document.created_at.isoformat(),
    }

@router.get("/documents/{document_id}/report/json")
def download_json_report(
    document_id: int,
    db: Session = Depends(get_db),
):
    document = (
        db.query(DocumentAnalysis)
        .filter(DocumentAnalysis.id == document_id)
        .first()
    )

    if not document:
        raise HTTPException(
            status_code=404,
            detail="Document not found."
        )

    report = generate_json_report(document)

    return Response(
        content=report,
        media_type="application/json",
        headers={
            "Content-Disposition":
                f'attachment; filename="{document.filename}_report.json"'
        },
    )


@router.get("/documents/{document_id}/report/csv")
def download_csv_report(
    document_id: int,
    db: Session = Depends(get_db),
):
    document = (
        db.query(DocumentAnalysis)
        .filter(DocumentAnalysis.id == document_id)
        .first()
    )

    if not document:
        raise HTTPException(
            status_code=404,
            detail="Document not found."
        )

    report = generate_csv_report(document)

    return Response(
        content=report,
        media_type="text/csv",
        headers={
            "Content-Disposition":
                f'attachment; filename="{document.filename}_report.csv"'
        },
    )

@router.get("/documents/{document_id}/report/pdf")
def download_pdf_report(
    document_id: int,
    db: Session = Depends(get_db),
):
    document = (
        db.query(DocumentAnalysis)
        .filter(DocumentAnalysis.id == document_id)
        .first()
    )

    if not document:
        raise HTTPException(
            status_code=404,
            detail="Document not found."
        )

    report = generate_pdf_report(document)

    return Response(
        content=report,
        media_type="application/pdf",
        headers={
            "Content-Disposition":
                f'attachment; filename="{document.filename}_report.pdf"'
        },
    )