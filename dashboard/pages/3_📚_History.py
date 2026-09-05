import streamlit as st
import pandas as pd

from api_client import (
    get_documents,
    get_document,
    get_json_report,
    get_csv_report,
    get_pdf_report,
)


st.title("📚 Document History")

st.caption("Search, filter and inspect previously analyzed documents.")


# -------------------------
# Filters
# -------------------------

st.subheader("🔎 Filters")

col1, col2, col3 = st.columns(3)

with col1:
    category = st.selectbox(
        "Category",
        [
            "All",
            "Emergency",
            "Logistics",
            "Personnel",
            "Infrastructure",
            "Operations",
            "Security",
        ],
    )

with col2:
    priority = st.selectbox(
        "Priority",
        [
            "All",
            "LOW",
            "MEDIUM",
            "HIGH",
            "CRITICAL",
        ],
    )

with col3:
    search = st.text_input(
        "Search",
        placeholder="Search filename or text...",
    )


col4, col5 = st.columns(2)

with col4:
    anomaly_filter = st.selectbox(
        "Anomaly",
        ["All", "Anomalies Only", "Normal Only"],
    )

with col5:
    min_risk = st.slider(
        "Minimum Risk Score",
        min_value=0,
        max_value=100,
        value=0,
    )


# -------------------------
# Load documents
# -------------------------

try:
    documents = get_documents(
        category=None if category == "All" else category,
        priority=None if priority == "All" else priority,
        anomaly=(
            None
            if anomaly_filter == "All"
            else anomaly_filter == "Anomalies Only"
        ),
        search=search or None,
        min_risk=min_risk if min_risk > 0 else None,
    )
except Exception as e:
    st.error(f"Failed to load document history: {e}")
    st.stop()


if not documents:
    st.info("No documents found.")
    st.stop()


# -------------------------
# Document table
# -------------------------

st.divider()

st.subheader(f"📄 Documents ({len(documents)})")

rows = []

for document in documents:
    rows.append({
        "ID": document.get("id"),
        "Filename": document.get("filename"),
        "Category": document.get("category"),
        "Risk Score": document.get("risk_score"),
        "Priority": document.get("priority"),
        "Anomaly": document.get("is_anomaly"),
        "Location": document.get("locations"),
        "Word Count": document.get("word_count"),
        "Created": document.get("created_at"),
    })

df = pd.DataFrame(rows)

st.dataframe(
    df,
    width="stretch",
    hide_index=True,
)


# -------------------------
# Document details
# -------------------------

st.divider()

st.subheader("🔍 Document Details")

document_ids = [
    document.get("id")
    for document in documents
    if document.get("id") is not None
]

selected_id = st.selectbox(
    "Select a document",
    document_ids,
)

if selected_id is not None:

    try:
        document = get_document(selected_id)
    except Exception as e:
        st.error(f"Failed to load document: {e}")
        st.stop()

    st.markdown(
        f"### 📄 {document.get('filename', 'Unknown')}"
    )

    # Metrics
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(
            "Category",
            document.get("category", "N/A"),
        )

    with col2:
        st.metric(
            "Risk Score",
            document.get("risk_score", "N/A"),
        )

    with col3:
        st.metric(
            "Priority",
            document.get("priority", "N/A"),
        )

    with col4:
        anomaly = document.get("is_anomaly", False)
        st.metric(
            "Anomaly",
            "Yes" if anomaly else "No",
        )

    # Classification
    st.markdown("#### 🧠 Classification")

    classification_data = {
        "Category": document.get("category"),
        "Confidence": document.get(
            "classification_confidence"
        ),
    }

    st.json(classification_data)

    # Extraction
    st.markdown("#### 📍 Extracted Information")

    col1, col2 = st.columns(2)

    with col1:
        st.write("**Locations**")
        st.write(document.get("locations", []))

    with col2:
        st.write("**Quantities**")
        st.write(document.get("quantities", []))

    # Text
    st.markdown("#### 📝 Text Preview")

    st.text_area(
        "Extracted text",
        document.get("text_preview", ""),
        height=300,
        disabled=True,
    )

    # Reports
    st.markdown("#### 📥 Download Reports")

    col1, col2, col3 = st.columns(3)

    try:
        with col1:
            json_report = get_json_report(selected_id)

            st.download_button(
                "⬇️ JSON",
                data=json_report,
                file_name=f"document_{selected_id}_report.json",
                mime="application/json",
                width="stretch",
            )

        with col2:
            csv_report = get_csv_report(selected_id)

            st.download_button(
                "⬇️ CSV",
                data=csv_report,
                file_name=f"document_{selected_id}_report.csv",
                mime="text/csv",
                width="stretch",
            )

        with col3:
            pdf_report = get_pdf_report(selected_id)

            st.download_button(
                "⬇️ PDF",
                data=pdf_report,
                file_name=f"document_{selected_id}_report.pdf",
                mime="application/pdf",
                width="stretch",
            )

    except Exception as e:
        st.error(f"Failed to generate reports: {e}")