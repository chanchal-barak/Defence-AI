import requests


API_URL = "http://127.0.0.1:8000"


def analyze_document(
    uploaded_file
):

    files = {
        "file": (
            uploaded_file.name,
            uploaded_file.getvalue(),
            uploaded_file.type
        )
    }

    response = requests.post(
        f"{API_URL}/api/analyze",
        files=files,
        timeout=120
    )

    response.raise_for_status()

    return response.json()

def analyze_batch(
    uploaded_files
):

    files = []

    for uploaded_file in uploaded_files:

        files.append(
            (
                "files",
                (
                    uploaded_file.name,
                    uploaded_file.getvalue(),
                    uploaded_file.type
                )
            )
        )

    response = requests.post(
        f"{API_URL}/api/analyze/batch",
        files=files,
        timeout=300
    )

    response.raise_for_status()

    return response.json()

def get_documents(
    category=None,
    priority=None,
    anomaly=None,
    location=None,
    search=None,
    min_risk=None
):

    params = {}

    if category:
        params["category"] = category

    if priority:
        params["priority"] = priority

    if anomaly is not None:
        params["anomaly"] = anomaly

    if location:
        params["location"] = location

    if search:
        params["search"] = search

    if min_risk is not None:
        params["min_risk"] = min_risk

    response = requests.get(
        f"{API_URL}/api/documents",
        params=params,
        timeout=30
    )

    response.raise_for_status()

    return response.json()

def get_document(
    document_id
):

    response = requests.get(
        f"{API_URL}/api/documents/{document_id}",
        timeout=30
    )

    response.raise_for_status()

    return response.json()

def get_json_report(document_id):
    response = requests.get(
        f"{API_URL}/api/documents/{document_id}/report/json",
        timeout=30
    )
    response.raise_for_status()
    return response.content


def get_csv_report(document_id):
    response = requests.get(
        f"{API_URL}/api/documents/{document_id}/report/csv",
        timeout=30
    )
    response.raise_for_status()
    return response.content


def get_pdf_report(document_id):
    response = requests.get(
        f"{API_URL}/api/documents/{document_id}/report/pdf",
        timeout=30
    )
    response.raise_for_status()
    return response.content