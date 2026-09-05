import streamlit as st
import pandas as pd

from api_client import analyze_batch


st.title("📦 Batch Document Analysis")

st.caption(
    "Upload multiple PDF or TXT documents and analyze them in one operation."
)

uploaded_files = st.file_uploader(
    "Upload documents",
    type=["pdf", "txt"],
    accept_multiple_files=True,
)

if not uploaded_files:
    st.info("Upload one or more documents to begin.")
    st.stop()


st.write(f"**{len(uploaded_files)} file(s) selected**")

with st.expander("Selected files"):
    for file in uploaded_files:
        st.write(f"📄 {file.name}")


if st.button(
    "🚀 Analyze All Documents",
    type="primary",
    width="stretch",
):
    with st.spinner("Running batch analysis..."):
        try:
            result = analyze_batch(uploaded_files)
            st.session_state["batch_result"] = result
        except Exception as e:
            st.error(f"Batch analysis failed: {e}")
            st.stop()


if "batch_result" not in st.session_state:
    st.info("Click 'Analyze All Documents' to start processing.")
    st.stop()


result = st.session_state["batch_result"]

total = result.get("total_files", 0)
successful = result.get("successful", 0)
failed = result.get("failed", 0)


st.divider()

# -------------------------
# Summary metrics
# -------------------------

col1, col2, col3 = st.columns(3)

with col1:
    st.metric("Total Files", total)

with col2:
    st.metric("Successful", successful)

with col3:
    st.metric("Failed", failed)


st.divider()

# -------------------------
# Results
# -------------------------

st.subheader("📋 Processing Results")

results = result.get("results", [])

if results:
    rows = []

    for item in results:
        rows.append({
            "Filename": item.get("filename", ""),
            "Status": item.get("status", ""),
            "Category": item.get("category", ""),
            "Risk Score": item.get("risk", {}).get(
                "risk_score",
                item.get("risk_score", "")
            ),
            "Priority": item.get("risk", {}).get(
                "priority",
                item.get("priority", "")
            ),
            "Anomaly": item.get("anomaly", {}).get(
                "is_anomaly",
                item.get("is_anomaly", "")
            ),
            "Message": item.get("message", ""),
        })

    df = pd.DataFrame(rows)

    st.dataframe(
        df,
        width="stretch",
        hide_index=True,
    )

else:
    st.warning("No results returned.")