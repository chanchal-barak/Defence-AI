import streamlit as st
import pandas as pd
import plotly.express as px

from api_client import analyze_document


st.title("📄 Single Document Analysis")

uploaded_file = st.file_uploader(
    "Upload a PDF or TXT document",
    type=["pdf", "txt"]
)

if not uploaded_file:
    st.info("Upload a document to begin analysis.")
    st.stop()


if st.button(
    "Analyze Document",
    type="primary",
    use_container_width=True
):

    with st.spinner("Running DefenceDoc AI pipeline..."):

        try:
            result = analyze_document(uploaded_file)
            st.session_state["analysis_result"] = result

        except Exception as e:
            st.error(f"Analysis failed: {e}")
            st.stop()


if "analysis_result" not in st.session_state:
    st.info("Click 'Analyze Document' to process the document.")
    st.stop()


result = st.session_state["analysis_result"]

classification = result.get("classification", {})
anomaly = result.get("anomaly", {})
extraction = result.get("extraction", {})
risk = result.get("risk", {})


# =========================================
# TOP METRICS
# =========================================

st.divider()

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        "Category",
        classification.get("category", "Unknown")
    )

with col2:
    confidence = classification.get("confidence", 0)
    st.metric(
        "Confidence",
        f"{confidence * 100:.1f}%"
    )

with col3:
    st.metric(
        "Anomaly",
        anomaly.get("status", "unknown").upper()
    )

with col4:
    st.metric(
        "Words",
        extraction.get("word_count", 0)
    )


# =========================================
# CLASSIFICATION
# =========================================

st.header("Document Classification")

scores = classification.get("scores", {})

if scores:

    score_df = pd.DataFrame({
        "Category": list(scores.keys()),
        "Probability": list(scores.values())
    })

    score_df = score_df.sort_values(
        "Probability",
        ascending=True
    )

    fig = px.bar(
        score_df,
        x="Probability",
        y="Category",
        orientation="h",
        title="Classification Scores"
    )

    fig.update_xaxes(tickformat=".0%")

    st.plotly_chart(
        fig,
        use_container_width=True
    )


# =========================================
# RISK
# =========================================

st.header("Risk Assessment")

r1, r2 = st.columns(2)

with r1:
    st.metric(
        "Risk Score",
        f"{risk.get('risk_score', 0)}/100"
    )

with r2:
    st.metric(
        "Priority",
        risk.get("priority", "UNKNOWN")
    )


reasons = risk.get("reasons", [])

if reasons:

    st.subheader("Risk Factors")

    for reason in reasons:
        st.write(f"⚠️ {reason}")


high_risk = risk.get("high_risk_indicators", [])
operational = risk.get("operational_indicators", [])

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


features = anomaly.get("features", {})

if features:

    feature_df = pd.DataFrame({
        "Feature": list(features.keys()),
        "Value": list(features.values())
    })

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
        extraction.get("character_count", 0)
    )

with e2:
    st.metric(
        "Words",
        extraction.get("word_count", 0)
    )

with e3:
    st.metric(
        "Pages",
        extraction.get("pages", 1)
    )


# =========================================
# ENTITIES
# =========================================

st.header("Named Entities")

entities = result.get("entities", {})

for entity_type, values in entities.items():

    if values:

        st.subheader(entity_type.capitalize())

        st.write(", ".join(values))

    else:

        st.write(
            f"**{entity_type.capitalize()}:** None detected"
        )


# =========================================
# DOCUMENT TEXT
# =========================================

st.header("Extracted Text")

with st.expander("View extracted document text"):

    st.text(
        result.get("text_preview", "")
    )