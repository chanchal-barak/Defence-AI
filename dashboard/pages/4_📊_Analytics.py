import streamlit as st
import pandas as pd
import plotly.express as px

from api_client import get_documents


st.title("📊 Analytics")

st.caption("Overview of document classification, risk and anomaly patterns.")


# -------------------------
# Load data
# -------------------------

try:
    documents = get_documents()
except Exception as e:
    st.error(f"Failed to load analytics data: {e}")
    st.stop()


if not documents:
    st.info("No analyzed documents available.")
    st.stop()


df = pd.DataFrame(documents)


# -------------------------
# Prepare data
# -------------------------

if "risk_score" in df.columns:
    df["risk_score"] = pd.to_numeric(
        df["risk_score"],
        errors="coerce"
    )

if "is_anomaly" in df.columns:
    df["is_anomaly"] = df["is_anomaly"].fillna(False).astype(bool)


# -------------------------
# KPI cards
# -------------------------

total_documents = len(df)

average_risk = (
    df["risk_score"].mean()
    if "risk_score" in df.columns
    else 0
)

anomalies = (
    int(df["is_anomaly"].sum())
    if "is_anomaly" in df.columns
    else 0
)

high_priority = (
    int(
        df["priority"]
        .isin(["HIGH", "CRITICAL"])
        .sum()
    )
    if "priority" in df.columns
    else 0
)


col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        "Total Documents",
        total_documents
    )

with col2:
    st.metric(
        "Average Risk",
        f"{average_risk:.1f}"
    )

with col3:
    st.metric(
        "Anomalies",
        anomalies
    )

with col4:
    st.metric(
        "High/Critical",
        high_priority
    )


st.divider()


# -------------------------
# Category distribution
# -------------------------

if "category" in df.columns:

    st.subheader("🧠 Document Categories")

    category_counts = (
        df["category"]
        .fillna("Unknown")
        .value_counts()
        .reset_index()
    )

    category_counts.columns = [
        "Category",
        "Count"
    ]

    fig = px.bar(
        category_counts,
        x="Category",
        y="Count",
        title="Documents by Category",
    )

    st.plotly_chart(
        fig,
        width="stretch"
    )


# -------------------------
# Priority distribution
# -------------------------

if "priority" in df.columns:

    st.subheader("🚨 Priority Distribution")

    priority_counts = (
        df["priority"]
        .fillna("Unknown")
        .value_counts()
        .reset_index()
    )

    priority_counts.columns = [
        "Priority",
        "Count"
    ]

    fig = px.pie(
        priority_counts,
        names="Priority",
        values="Count",
        title="Documents by Priority",
    )

    st.plotly_chart(
        fig,
        width="stretch"
    )


# -------------------------
# Risk distribution
# -------------------------

if "risk_score" in df.columns:

    st.subheader("📈 Risk Score Distribution")

    fig = px.histogram(
        df,
        x="risk_score",
        nbins=10,
        title="Risk Score Distribution",
    )

    fig.update_layout(
        xaxis_title="Risk Score",
        yaxis_title="Documents",
    )

    st.plotly_chart(
        fig,
        width="stretch"
    )


# -------------------------
# Anomaly analysis
# -------------------------

if "is_anomaly" in df.columns:

    st.subheader("🔍 Anomaly Analysis")

    anomaly_counts = (
        df["is_anomaly"]
        .map({
            True: "Anomaly",
            False: "Normal"
        })
        .value_counts()
        .reset_index()
    )

    anomaly_counts.columns = [
        "Status",
        "Count"
    ]

    fig = px.bar(
        anomaly_counts,
        x="Status",
        y="Count",
        title="Normal vs Anomalous Documents",
    )

    st.plotly_chart(
        fig,
        width="stretch"
    )


# -------------------------
# Recent documents
# -------------------------

st.subheader("📋 Recent Documents")

display_columns = [
    column
    for column in [
        "id",
        "filename",
        "category",
        "risk_score",
        "priority",
        "is_anomaly",
        "created_at",
    ]
    if column in df.columns
]

recent_df = df[display_columns].copy()

if "created_at" in recent_df.columns:
    recent_df = recent_df.sort_values(
        "created_at",
        ascending=False
    )

st.dataframe(
    recent_df.head(20),
    width="stretch",
    hide_index=True,
)