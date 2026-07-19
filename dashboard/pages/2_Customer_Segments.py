"""
RetailPulse — Customer Segments page.

Shows the Day 3 K-Means segmentation (business-labeled) and DBSCAN outlier
cross-check, with a filterable per-customer table.
"""
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from utils.data_loader import get_customer_segments
from utils.theme import PLOTLY_TEMPLATE

st.set_page_config(page_title="RetailPulse | Customer Segments", page_icon="👥", layout="wide")
st.title("👥 Customer Segments")
st.caption("RFM analysis + K-Means clustering, cross-checked with DBSCAN outlier detection")

try:
    segments = get_customer_segments()
except FileNotFoundError as e:
    st.error(f"Missing data file: {e.filename}. Run notebook 03_segmentation.ipynb first.")
    st.stop()

# --- KPI row ---
col1, col2, col3, col4 = st.columns(4)
col1.metric("Total Customers", f"{len(segments):,}")
col2.metric("Segments Identified", f"{segments['Segment'].nunique()}")
col3.metric("Avg Customer Value", f"£{segments['Monetary'].mean():,.0f}")
n_outliers = (segments["Cluster_DBSCAN"] == -1).sum()
col4.metric("DBSCAN Outliers Flagged", f"{n_outliers:,}", help="Customers with unusual RFM patterns")

st.markdown("---")

left, right = st.columns([2, 1])

with left:
    st.subheader("Customer Segments: Recency vs Monetary")
    fig = px.scatter(
        segments, x="Recency", y="Monetary", color="Segment",
        hover_data=["CustomerID", "Frequency"], opacity=0.6,
        template=PLOTLY_TEMPLATE,
    )
    fig.update_layout(height=450, margin=dict(l=10, r=10, t=10, b=10))
    st.plotly_chart(fig, use_container_width=True)

with right:
    st.subheader("Segment Distribution")
    segment_counts = segments["Segment"].value_counts()
    fig2 = go.Figure(data=[go.Pie(labels=segment_counts.index, values=segment_counts.values, hole=0.4)])
    fig2.update_layout(template=PLOTLY_TEMPLATE, height=450, margin=dict(l=10, r=10, t=10, b=10))
    st.plotly_chart(fig2, use_container_width=True)

st.markdown("---")

# --- Segment profile table ---
st.subheader("Segment Profiles")
profile = (segments.groupby("Segment")
           .agg(Customers=("CustomerID", "count"),
                AvgRecency=("Recency", "mean"),
                AvgFrequency=("Frequency", "mean"),
                AvgMonetary=("Monetary", "mean"),
                AvgOrderValue=("AvgOrderValue", "mean"))
           .round(1)
           .sort_values("AvgMonetary", ascending=False))
st.dataframe(profile.style.format({"AvgMonetary": "£{:,.0f}", "AvgOrderValue": "£{:,.0f}"}),
             use_container_width=True)

st.markdown("---")

# --- Filterable customer table ---
st.subheader("Explore Customers by Segment")
selected_segments = st.multiselect(
    "Filter by segment", options=sorted(segments["Segment"].unique()),
    default=sorted(segments["Segment"].unique()),
)
show_outliers_only = st.checkbox("Show DBSCAN outliers only")

filtered = segments[segments["Segment"].isin(selected_segments)]
if show_outliers_only:
    filtered = filtered[filtered["Cluster_DBSCAN"] == -1]

display_cols = ["CustomerID", "Segment", "Recency", "Frequency", "Monetary",
                 "AvgOrderValue", "TenureDays", "Cluster_DBSCAN"]
st.dataframe(
    filtered[display_cols].sort_values("Monetary", ascending=False).style.format(
        {"Monetary": "£{:,.0f}", "AvgOrderValue": "£{:,.0f}"}),
    use_container_width=True, hide_index=True, height=350,
)
st.caption(f"Showing {len(filtered):,} of {len(segments):,} customers.")

csv_bytes = filtered[display_cols].to_csv(index=False).encode("utf-8")
st.download_button(
    "⬇ Download filtered customers (CSV)",
    data=csv_bytes,
    file_name="retailpulse_customer_segments.csv",
    mime="text/csv",
)
