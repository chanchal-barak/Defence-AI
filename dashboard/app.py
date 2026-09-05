import streamlit as st
import pandas as pd
import plotly.express as px


from api_client import (
    analyze_document,
    analyze_batch,
    get_documents,
    get_document,
    get_json_report,
    get_csv_report,
    get_pdf_report,
)

st.set_page_config(
    page_title="DefenceDoc AI",
    page_icon="🛡️",
    layout="wide",
)


# --------------------------------------------------
# Sidebar
# --------------------------------------------------

st.sidebar.title("🛡️ DefenceDoc AI")

st.sidebar.caption("Document Intelligence Platform")

st.sidebar.divider()

st.sidebar.markdown(
    """
    **Modules**

    📄 Single Analysis  
    📦 Batch Analysis  
    📚 Document History  
    📊 Analytics
    """
)

st.sidebar.divider()

st.sidebar.caption(
    "Public / unclassified document analysis"
)


# --------------------------------------------------
# Hero
# --------------------------------------------------

st.title("🛡️ DefenceDoc AI")

st.subheader(
    "AI-Powered Document Intelligence Platform"
)

st.write(
    """
    DefenceDoc AI automatically analyzes documents to identify their
    category, assess operational risk, detect anomalous documents,
    and extract important information using NLP and machine learning.
    """
)

st.divider()


# --------------------------------------------------
# Demo statistics
# --------------------------------------------------

st.subheader("🚀 Demo Workspace")

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        "Documents",
        "192",
        help="Synthetic documents included in the demonstration dataset."
    )

with col2:
    st.metric(
        "Categories",
        "6",
        help="Document categories supported by the trained classifier."
    )

with col3:
    st.metric(
        "CV Macro-F1",
        "98%",
        help="5-fold stratified cross-validation result on the synthetic dataset."
    )

with col4:
    st.metric(
        "Analysis Pipeline",
        "5 Stages",
    )


st.divider()


# --------------------------------------------------
# Pipeline
# --------------------------------------------------

st.subheader("🔬 Analysis Pipeline")

pipeline = [
    ("1️⃣", "Text Extraction", "PDF/TXT extraction with OCR fallback"),
    ("2️⃣", "NLP Extraction", "Locations, quantities and entities"),
    ("3️⃣", "Classification", "TF-IDF + Linear SVM"),
    ("4️⃣", "Risk Assessment", "Risk score, priority and indicators"),
    ("5️⃣", "Anomaly Detection", "Isolation Forest based detection"),
]

for icon, title, description in pipeline:
    col1, col2, col3 = st.columns([1, 2, 6])

    with col1:
        st.markdown(f"### {icon}")

    with col2:
        st.markdown(f"**{title}**")

    with col3:
        st.write(description)


st.divider()


# --------------------------------------------------
# Features
# --------------------------------------------------

st.subheader("⚙️ What the System Provides")

col1, col2 = st.columns(2)

with col1:
    st.markdown(
        """
        ### 🧠 Machine Learning

        - TF-IDF text representation
        - Linear SVM classification
        - Classification confidence
        - Multi-class document categorization
        - Cross-validation evaluation
        """
    )

with col2:
    st.markdown(
        """
        ### 🚨 Intelligence & Risk

        - Risk scoring
        - Priority assignment
        - Anomaly detection
        - Risk indicators
        - NLP entity extraction
        """
    )


col1, col2 = st.columns(2)

with col1:
    st.markdown(
        """
        ### 📦 Processing

        - Single document analysis
        - Batch document processing
        - SQLite persistence
        - Search and filtering
        """
    )

with col2:
    st.markdown(
        """
        ### 📊 Reporting

        - Interactive analytics
        - Historical analysis
        - JSON reports
        - CSV reports
        - PDF reports
        """
    )


st.divider()


# --------------------------------------------------
# Technology stack
# --------------------------------------------------

st.subheader("🛠️ Technology Stack")

st.markdown(
    """
    **Frontend:** Streamlit · Plotly

    **Backend:** FastAPI · Python · SQLAlchemy · SQLite

    **AI / ML:** scikit-learn · spaCy · TF-IDF · Linear SVM · Isolation Forest

    **Document Processing:** PDF/TXT extraction · OCR fallback

    **Reporting:** JSON · CSV · PDF
    """
)


st.divider()


# --------------------------------------------------
# Demo disclaimer
# --------------------------------------------------

st.caption(
    "Demo results are based on a synthetic dataset and are intended "
    "to demonstrate the system architecture and capabilities."
)

st.info(
    "👈 Use the navigation menu to explore the analysis, "
    "history and analytics modules."
)


# -----------------------------------------
# Sidebar
# -----------------------------------------

with st.sidebar:

    st.header("Document Analysis")

    mode = st.radio(
        "Analysis Mode",
        ["Single Document", "Batch Documents"]
    )

    if mode == "Single Document":

        uploaded_file = st.file_uploader(
            "Upload a document",
            type=["pdf", "txt"]
        )

        analyze_button = st.button(
            "Analyze Document",
            type="primary",
            use_container_width=True
        )

        batch_files = None

    else:

        uploaded_file = None

        batch_files = st.file_uploader(
            "Upload documents",
            type=["pdf", "txt"],
            accept_multiple_files=True
        )

        analyze_button = st.button(
            "Analyze Batch",
            type="primary",
            use_container_width=True
        )


# -----------------------------------------
# Empty state
# -----------------------------------------

if mode == "Single Document" and not uploaded_file:

    st.info(
        "Upload a PDF or TXT document "
        "to begin analysis."
    )

    st.stop()

if mode == "Batch Documents" and not batch_files:

    st.info(
        "Upload multiple PDF or TXT documents "
        "to begin batch analysis."
    )

    st.stop()


# -----------------------------------------
# Analyze
# -----------------------------------------

if mode == "Batch Documents":

    batch_result = st.session_state.get(
        "batch_result"
    )

    if not batch_result:

        st.info(
            "Click 'Analyze Batch' to process the documents."
        )

        st.stop()

    st.header("📦 Batch Analysis Results")

    b1, b2, b3 = st.columns(3)

    with b1:
        st.metric(
            "Total Files",
            batch_result.get("total_files", 0)
        )

    with b2:
        st.metric(
            "Successful",
            batch_result.get("successful", 0)
        )

    with b3:
        st.metric(
            "Failed",
            batch_result.get("failed", 0)
        )

    results = batch_result.get("results", [])

    if results:

        batch_df = pd.DataFrame(results)

        st.subheader("Processing Results")

        st.dataframe(
            batch_df,
            use_container_width=True,
            hide_index=True
        )

    st.stop()

if analyze_button:

    with st.spinner(
        "Running DefenceDoc AI pipeline..."
    ):

        try:

            result = analyze_document(
                uploaded_file
            )

            st.session_state[
                "analysis_result"
            ] = result

        except Exception as e:

            st.error(
                f"Analysis failed: {e}"
            )

            st.stop()


if "analysis_result" not in st.session_state:

    st.info(
        "Click 'Analyze Document' to process "
        "the uploaded document."
    )

    st.stop()


result = st.session_state[
    "analysis_result"
]


# =========================================
# TOP METRICS
# =========================================

classification = result.get(
    "classification",
    {}
)

anomaly = result.get(
    "anomaly",
    {}

)

extraction = result.get(
    "extraction",
    {}
)


col1, col2, col3, col4 = st.columns(4)


with col1:

    st.metric(
        "Category",
        classification.get(
            "category",
            "Unknown"
        )
    )


with col2:

    confidence = classification.get(
        "confidence",
        0
    )

    st.metric(
        "Confidence",
        f"{confidence * 100:.1f}%"
    )


with col3:

    status = anomaly.get(
        "status",
        "unknown"
    )

    st.metric(
        "Anomaly",
        status.upper()
    )


with col4:

    st.metric(
        "Words",
        extraction.get(
            "word_count",
            0
        )
    )


st.divider()


# =========================================
# CLASSIFICATION
# =========================================

st.header("Document Classification")


scores = classification.get(
    "scores",
    {}
)


if scores:

    score_df = pd.DataFrame(
        {
            "Category": list(
                scores.keys()
            ),
            "Probability": list(
                scores.values()
            )
        }
    )

    score_df = score_df.sort_values(
        "Probability",
        ascending=True
    )

    fig = px.bar(
        score_df,
        x="Probability",
        y="Category",
        orientation="h",
        title="Classification Probabilities"
    )

    fig.update_xaxes(
        tickformat=".0%"
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

# =========================================
# RISK ASSESSMENT
# =========================================

st.header("Risk Assessment")

risk = result.get(
    "risk",
    {}
)

risk_score = risk.get(
    "risk_score",
    0
)

priority = risk.get(
    "priority",
    "UNKNOWN"
)

r1, r2 = st.columns(2)

with r1:

    st.metric(
        "Risk Score",
        f"{risk_score}/100"
    )

with r2:

    st.metric(
        "Priority",
        priority
    )


# -----------------------------------------
# Risk explanation
# -----------------------------------------

reasons = risk.get(
    "reasons",
    []
)

if reasons:

    st.subheader("Risk Factors")

    for reason in reasons:

        st.write(
            f"⚠️ {reason}"
        )


# -----------------------------------------
# Detected indicators
# -----------------------------------------

high_risk = risk.get(
    "high_risk_indicators",
    []
)

operational = risk.get(
    "operational_indicators",
    []
)


if high_risk:

    st.write(
        "**High-risk indicators:** "
        + ", ".join(high_risk)
    )


if operational:

    st.write(
        "**Operational indicators:** "
        + ", ".join(operational)
    )


# =========================================
# ANOMALY
# =========================================

st.header("Anomaly Detection")


if anomaly.get("is_anomaly"):

    st.error(
        f"Potential anomaly detected. "
        f"Score: {anomaly.get('anomaly_score', 0):.4f}"
    )

else:

    st.success(
        f"No anomaly detected. "
        f"Score: {anomaly.get('anomaly_score', 0):.4f}"
    )


features = anomaly.get(
    "features",
    {}
)


if features:

    feature_df = pd.DataFrame(
        {
            "Feature": list(
                features.keys()
            ),
            "Value": list(
                features.values()
            )
        }
    )

    st.dataframe(
        feature_df,
        use_container_width=True,
        hide_index=True
    )


# =========================================
# EXTRACTION
# =========================================

st.header("Document Extraction")


e1, e2, e3 = st.columns(3)


with e1:

    st.metric(
        "Characters",
        extraction.get(
            "character_count",
            0
        )
    )


with e2:

    st.metric(
        "Words",
        extraction.get(
            "word_count",
            0
        )
    )


with e3:

    st.metric(
        "Pages",
        extraction.get(
            "pages",
            1
        )
    )


# =========================================
# ENTITIES
# =========================================

st.header("Named Entities")


entities = result.get(
    "entities",
    {}
)


for entity_type, values in entities.items():

    if values:

        st.subheader(
            entity_type.capitalize()
        )

        st.write(
            ", ".join(values)
        )

    else:

        st.write(
            f"**{entity_type.capitalize()}:** None detected"
        )


# =========================================
# DOCUMENT TEXT
# =========================================

st.header("Extracted Text")

with st.expander(
    "View extracted document text"
):

    st.text(
        result.get(
            "text_preview",
            ""
        )
    )

# =========================================
# DOCUMENT HISTORY
# =========================================

st.divider()

st.header("Document History")

st.caption(
    "Search and filter previously analyzed documents."
)


# -----------------------------------------
# Load available documents
# -----------------------------------------

try:

    all_documents = get_documents()

except Exception as e:

    st.error(
        f"Could not load document history: {e}"
    )

    all_documents = []


# -----------------------------------------
# Filter options
# -----------------------------------------

if all_documents:

    categories = sorted(
        set(
            document["category"]
            for document in all_documents
            if document.get("category")
        )
    )

    priorities = sorted(
        set(
            document["priority"]
            for document in all_documents
            if document.get("priority")
        )
    )

    locations = sorted(
        set(
            location.strip()
            for document in all_documents
            for location in document.get(
                "locations",
                ""
            ).split(",")
            if location.strip()
        )
    )

else:

    categories = []
    priorities = []
    locations = []


# -----------------------------------------
# Search and filters
# -----------------------------------------

f1, f2, f3 = st.columns(3)


with f1:

    search = st.text_input(
        "Search",
        placeholder="Filename, text, location..."
    )


with f2:

    category = st.selectbox(
        "Category",
        ["All"] + categories
    )


with f3:

    priority = st.selectbox(
        "Priority",
        ["All"] + priorities
    )


f4, f5, f6 = st.columns(3)


with f4:

    location = st.selectbox(
        "Location",
        ["All"] + locations
    )


with f5:

    anomaly_filter = st.selectbox(
        "Anomaly",
        [
            "All",
            "Anomalous only",
            "Normal only"
        ]
    )


with f6:

    min_risk = st.number_input(
        "Minimum Risk Score",
        min_value=0,
        max_value=100,
        value=0,
        step=5
    )


# -----------------------------------------
# Apply filters
# -----------------------------------------

selected_category = (
    None
    if category == "All"
    else category
)

selected_priority = (
    None
    if priority == "All"
    else priority
)

selected_location = (
    None
    if location == "All"
    else location
)

if anomaly_filter == "Anomalous only":

    selected_anomaly = True

elif anomaly_filter == "Normal only":

    selected_anomaly = False

else:

    selected_anomaly = None


try:

    documents = get_documents(
        category=selected_category,
        priority=selected_priority,
        anomaly=selected_anomaly,
        location=selected_location,
        search=search.strip() or None,
        min_risk=(
            min_risk
            if min_risk > 0
            else None
        )
    )

except Exception as e:

    st.error(
        f"Could not apply filters: {e}"
    )

    documents = []


# -----------------------------------------
# Results
# -----------------------------------------

st.subheader(
    f"Results ({len(documents)})"
)


if not documents:

    st.info(
        "No documents match the selected filters."
    )

else:

    history_df = pd.DataFrame(
        documents
    )

    history_df = history_df.rename(
        columns={
            "id": "ID",
            "filename": "Document",
            "category": "Category",
            "classification_confidence": "Confidence",
            "risk_score": "Risk",
            "priority": "Priority",
            "is_anomaly": "Anomaly",
            "locations": "Locations",
            "quantities": "Quantities",
            "word_count": "Words",
            "created_at": "Analyzed At"
        }
    )

    history_df[
        "Confidence"
    ] = (
        history_df["Confidence"] * 100
    ).round(1)

    history_df = history_df[
        [
            "ID",
            "Document",
            "Category",
            "Confidence",
            "Risk",
            "Priority",
            "Anomaly",
            "Locations",
            "Quantities",
            "Words",
            "Analyzed At"
        ]
    ]

    st.dataframe(
        history_df,
        use_container_width=True,
        hide_index=True
    )

# =========================================
# DOCUMENT DETAIL
# =========================================

if documents:

    st.divider()

    st.header("Document Details")

    document_options = {
        f"{document['id']} — {document['filename']}":
        document["id"]
        for document in documents
    }

    selected_document = st.selectbox(
        "Select a document",
        list(document_options.keys())
    )

    selected_id = document_options[
        selected_document
    ]

    try:

        detail = get_document(
            selected_id
        )

    except Exception as e:

        st.error(
            f"Could not load document details: {e}"
        )

    else:

        d1, d2, d3, d4 = st.columns(4)

        with d1:

            st.metric(
                "Category",
                detail["category"]
            )

        with d2:

            st.metric(
                "Risk",
                f"{detail['risk_score']}/100"
            )

        with d3:

            st.metric(
                "Priority",
                detail["priority"]
            )

        with d4:

            st.metric(
                "Anomaly",
                "YES"
                if detail["is_anomaly"]
                else "NO"
            )

        st.subheader("Document Metadata")

        metadata = pd.DataFrame(
            [
                {
                    "Field": "Filename",
                    "Value": detail["filename"]
                },
                {
                    "Field": "Classification Confidence",
                    "Value": (
                        f"{detail['classification_confidence'] * 100:.1f}%"
                    )
                },
                {
                    "Field": "Anomaly Score",
                    "Value": detail["anomaly_score"]
                },
                {
                    "Field": "Locations",
                    "Value": detail["locations"] or "None"
                },
                {
                    "Field": "Quantities",
                    "Value": detail["quantities"] or "None"
                },
                {
                    "Field": "Word Count",
                    "Value": detail["word_count"]
                },
                {
                    "Field": "Analyzed At",
                    "Value": detail["created_at"]
                },
            ]
        )
        metadata["Value"] = metadata["Value"].astype(str)

        st.dataframe(
            metadata,
            use_container_width=True,
            hide_index=True
        )

        st.subheader("Extracted Text")

        with st.expander(
            "View stored document text"
        ):

            st.text(
                detail["text_preview"]
            )

# =========================================
# ANALYTICS DASHBOARD
# =========================================

st.divider()

st.header("📊 Intelligence Analytics")

try:

    analytics_documents = get_documents()

except Exception as e:

    st.error(
        f"Could not load analytics data: {e}"
    )

    analytics_documents = []


if not analytics_documents:

    st.info(
        "No analyzed documents available for analytics."
    )

else:

    analytics_df = pd.DataFrame(
        analytics_documents
    )

    # -----------------------------------------
    # Prepare data
    # -----------------------------------------

    analytics_df["risk_score"] = pd.to_numeric(
        analytics_df["risk_score"],
        errors="coerce"
    ).fillna(0)

    analytics_df["is_anomaly"] = (
        analytics_df["is_anomaly"]
        .astype(bool)
    )

    # =========================================
    # TOP METRICS
    # =========================================

    total_documents = len(
        analytics_df
    )

    high_risk_documents = len(
        analytics_df[
            analytics_df["risk_score"] >= 60
        ]
    )

    anomaly_documents = int(
        analytics_df["is_anomaly"].sum()
    )

    average_risk = analytics_df[
        "risk_score"
    ].mean()

    a1, a2, a3, a4 = st.columns(4)

    with a1:

        st.metric(
            "Total Documents",
            total_documents
        )

    with a2:

        st.metric(
            "High Risk",
            high_risk_documents
        )

    with a3:

        st.metric(
            "Anomalies",
            anomaly_documents
        )

    with a4:

        st.metric(
            "Average Risk",
            f"{average_risk:.1f}/100"
        )

    st.divider()

    # =========================================
    # CATEGORY DISTRIBUTION
    # =========================================

    c1, c2 = st.columns(2)

    with c1:

        category_counts = (
            analytics_df[
                "category"
            ]
            .value_counts()
            .reset_index()
        )

        category_counts.columns = [
            "Category",
            "Documents"
        ]

        fig_category = px.pie(
            category_counts,
            names="Category",
            values="Documents",
            title="Documents by Category"
        )

        st.plotly_chart(
            fig_category,
            use_container_width=True
        )

    # =========================================
    # PRIORITY DISTRIBUTION
    # =========================================

    with c2:

        priority_counts = (
            analytics_df[
                "priority"
            ]
            .value_counts()
            .reset_index()
        )

        priority_counts.columns = [
            "Priority",
            "Documents"
        ]

        fig_priority = px.bar(
            priority_counts,
            x="Priority",
            y="Documents",
            title="Documents by Priority"
        )

        st.plotly_chart(
            fig_priority,
            use_container_width=True
        )

    # =========================================
    # RISK DISTRIBUTION
    # =========================================

    st.subheader("Risk Distribution")

    fig_risk = px.histogram(
        analytics_df,
        x="risk_score",
        nbins=10,
        title="Distribution of Risk Scores"
    )

    fig_risk.update_xaxes(
        title="Risk Score"
    )

    fig_risk.update_yaxes(
        title="Documents"
    )

    st.plotly_chart(
        fig_risk,
        use_container_width=True
    )

    # =========================================
    # ANOMALY ANALYSIS
    # =========================================

    anomaly_counts = pd.DataFrame(
        {
            "Status": [
                "Normal",
                "Anomalous"
            ],
            "Documents": [
                total_documents
                - anomaly_documents,
                anomaly_documents
            ]
        }
    )

    fig_anomaly = px.pie(
        anomaly_counts,
        names="Status",
        values="Documents",
        title="Anomaly Detection Overview"
    )

    st.plotly_chart(
        fig_anomaly,
        use_container_width=True
    )

    # =========================================
    # RISK BY CATEGORY
    # =========================================

    risk_by_category = (
        analytics_df
        .groupby("category")[
            "risk_score"
        ]
        .mean()
        .reset_index()
    )

    risk_by_category[
        "risk_score"
    ] = risk_by_category[
        "risk_score"
    ].round(1)

    fig_risk_category = px.bar(
        risk_by_category,
        x="category",
        y="risk_score",
        title="Average Risk by Category"
    )

    fig_risk_category.update_yaxes(
        title="Average Risk Score"
    )

    fig_risk_category.update_xaxes(
        title="Category"
    )

    st.plotly_chart(
        fig_risk_category,
        use_container_width=True
    )
    # =========================================
    # TIME SERIES ANALYTICS
    # =========================================

    st.divider()

    st.subheader("Time-Based Intelligence")

    analytics_df["created_at"] = pd.to_datetime(
        analytics_df["created_at"],
        errors="coerce"
    )

    analytics_df = analytics_df.dropna(
        subset=["created_at"]
    )

    if not analytics_df.empty:

        # -----------------------------------------
        # Documents analyzed over time
        # -----------------------------------------

        documents_over_time = (
            analytics_df
            .set_index("created_at")
            .resample("D")
            .size()
            .reset_index(name="Documents")
        )

        fig_volume = px.line(
            documents_over_time,
            x="created_at",
            y="Documents",
            markers=True,
            title="Documents Analyzed Over Time"
        )

        fig_volume.update_xaxes(
            title="Date"
        )

        fig_volume.update_yaxes(
            title="Documents"
        )

        st.plotly_chart(
            fig_volume,
            use_container_width=True
        )

        # -----------------------------------------
        # Average risk over time
        # -----------------------------------------

        risk_over_time = (
            analytics_df
            .set_index("created_at")
            .resample("D")["risk_score"]
            .mean()
            .reset_index()
        )

        fig_risk_time = px.line(
            risk_over_time,
            x="created_at",
            y="risk_score",
            markers=True,
            title="Average Risk Over Time"
        )

        fig_risk_time.update_yaxes(
            title="Average Risk Score"
        )

        st.plotly_chart(
            fig_risk_time,
            use_container_width=True
        )

        # -----------------------------------------
        # Anomalies over time
        # -----------------------------------------

        anomaly_over_time = (
            analytics_df
            .assign(
                anomaly_count=
                analytics_df["is_anomaly"].astype(int)
            )
            .set_index("created_at")
            .resample("D")["anomaly_count"]
            .sum()
            .reset_index()
        )

        fig_anomaly_time = px.line(
            anomaly_over_time,
            x="created_at",
            y="anomaly_count",
            markers=True,
            title="Anomalies Detected Over Time"
        )

        fig_anomaly_time.update_yaxes(
            title="Anomalies"
        )

        st.plotly_chart(
            fig_anomaly_time,
            use_container_width=True
        )

st.subheader("📄 Reports")

col1, col2, col3 = st.columns(3)

try:
    with col1:
        json_data = get_json_report(selected_id)

        st.download_button(
            "Download JSON",
            data=json_data,
            file_name=f"document_{selected_id}_report.json",
            mime="application/json",
        )

    with col2:
        csv_data = get_csv_report(selected_id)

        st.download_button(
            "Download CSV",
            data=csv_data,
            file_name=f"document_{selected_id}_report.csv",
            mime="text/csv",
        )

    with col3:
        pdf_data = get_pdf_report(selected_id)

        st.download_button(
            "Download PDF",
            data=pdf_data,
            file_name=f"document_{selected_id}_report.pdf",
            mime="application/pdf",
        )

except Exception as e:
    st.error(f"Unable to generate report: {e}")