import csv
import io
import json
from reportlab.lib.pagesizes import A4
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
)
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch

def build_report_data(document) -> dict:
    return {
        "document": {
            "id": document.id,
            "filename": document.filename,
            "created_at": document.created_at.isoformat(),
        },
        "classification": {
            "category": document.category,
            "confidence": document.classification_confidence,
        },
        "risk": {
            "risk_score": document.risk_score,
            "priority": document.priority,
        },
        "anomaly": {
            "is_anomaly": document.is_anomaly,
            "anomaly_score": document.anomaly_score,
        },
        "extraction": {
            "locations": document.locations,
            "quantities": document.quantities,
            "word_count": document.word_count,
        },
        "text": {
            "preview": document.text_preview,
        },
    }


def generate_json_report(document) -> str:
    return json.dumps(
        build_report_data(document),
        indent=4,
        ensure_ascii=False,
    )


def generate_csv_report(document) -> str:
    data = build_report_data(document)
    output = io.StringIO()
    writer = csv.writer(output)

    writer.writerow(["Field", "Value"])

    rows = [
        ("Document ID", data["document"]["id"]),
        ("Filename", data["document"]["filename"]),
        ("Created At", data["document"]["created_at"]),
        ("Category", data["classification"]["category"]),
        ("Classification Confidence", data["classification"]["confidence"]),
        ("Risk Score", data["risk"]["risk_score"]),
        ("Priority", data["risk"]["priority"]),
        ("Is Anomaly", data["anomaly"]["is_anomaly"]),
        ("Anomaly Score", data["anomaly"]["anomaly_score"]),
        ("Locations", data["extraction"]["locations"]),
        ("Quantities", data["extraction"]["quantities"]),
        ("Word Count", data["extraction"]["word_count"]),
    ]

    writer.writerows(rows)

    return output.getvalue()

def generate_pdf_report(document) -> bytes:
    data = build_report_data(document)

    output = io.BytesIO()

    pdf = SimpleDocTemplate(
        output,
        pagesize=A4,
        rightMargin=40,
        leftMargin=40,
        topMargin=40,
        bottomMargin=40,
    )

    styles = getSampleStyleSheet()
    story = []

    story.append(
        Paragraph(
            "DefenceDoc AI — Document Analysis Report",
            styles["Title"],
        )
    )

    story.append(Spacer(1, 20))

    rows = [
        ["Field", "Value"],
        ["Filename", data["document"]["filename"]],
        ["Category", data["classification"]["category"]],
        ["Confidence", str(data["classification"]["confidence"])],
        ["Risk Score", str(data["risk"]["risk_score"])],
        ["Priority", data["risk"]["priority"]],
        ["Anomaly", str(data["anomaly"]["is_anomaly"])],
        ["Anomaly Score", str(data["anomaly"]["anomaly_score"])],
        ["Locations", str(data["extraction"]["locations"])],
        ["Quantities", str(data["extraction"]["quantities"])],
        ["Word Count", str(data["extraction"]["word_count"])],
    ]

    table = Table(rows, colWidths=[2 * inch, 4 * inch])

    table.setStyle(
        TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.grey),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.black),
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ("PADDING", (0, 0), (-1, -1), 6),
        ])
    )

    story.append(table)
    story.append(Spacer(1, 20))

    story.append(
        Paragraph("Extracted Text", styles["Heading2"])
    )

    text = data["text"]["preview"].replace(
        "&", "&amp;"
    ).replace(
        "<", "&lt;"
    ).replace(
        ">", "&gt;"
    )

    story.append(
        Paragraph(
            text.replace("\n", "<br/>"),
            styles["BodyText"],
        )
    )

    pdf.build(story)

    return output.getvalue()