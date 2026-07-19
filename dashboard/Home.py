"""
RetailPulse: AI-Powered Sales & Retail Analytics Platform
Executive Overview — main dashboard entry point.

Run with:  streamlit run Home.py
Additional pages live in pages/ and appear automatically in the sidebar nav
(Streamlit's native multi-page app convention).
"""
import streamlit as st
import plotly.graph_objects as go

from utils.data_loader import get_sales_cleaned, get_customer_segments, get_hybrid_metrics, get_churn_metrics
from utils.theme import PRIMARY_COLOR, PLOTLY_TEMPLATE

st.set_page_config(
    page_title="RetailPulse | Executive Overview",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.title("📊 RetailPulse: AI-Powered Sales & Retail Analytics Platform")
st.caption("Predictive Demand • Customer Segmentation • Churn Analysis • Inventory Optimization")

with st.sidebar:
    st.markdown("### Navigation")
    st.markdown(
        "- **Home** — Executive Overview\n"
        "- **Sales Analytics** — trends & product performance\n"
        "- **Customer Segments** — RFM + K-Means/DBSCAN\n"
        "- **Demand Forecast** — Prophet + LSTM hybrid\n"
        "- **Churn Risk** — at-risk customer scoring\n"
        "- **Inventory Health** — ABC/EOQ recommendations\n"
        "- **Project Summary** — methodology & tech stack"
    )
    st.markdown("---")
    st.caption("Data refreshes automatically when underlying files change.")

try:
    sales = get_sales_cleaned()
    segments = get_customer_segments()
    hybrid_metrics = get_hybrid_metrics()
    churn_metrics = get_churn_metrics()
except FileNotFoundError as e:
    st.error(
        f"Missing data file: {e.filename}. Run the notebooks (01 through 11) to generate "
        "the processed data this dashboard reads."
    )
    st.stop()

# --- KPI Row ---
total_revenue = sales["TotalPrice"].sum()
total_orders = sales["InvoiceNo"].nunique()
total_customers = sales["CustomerID"].nunique()
avg_order_value = total_revenue / total_orders

col1, col2, col3, col4 = st.columns(4)
col1.metric("Total Revenue", f"£{total_revenue:,.0f}")
col2.metric("Total Orders", f"{total_orders:,}")
col3.metric("Total Customers", f"{total_customers:,}")
col4.metric("Avg Order Value", f"£{avg_order_value:,.2f}")

st.markdown("---")

# --- Model Health Row ---
st.subheader("Model Health at a Glance")
mcol1, mcol2, mcol3, mcol4 = st.columns(4)
mcol1.metric("Forecast MAPE (Hybrid)", f"{hybrid_metrics['mape']:.2f}%", help="Target: ≤ 12%")
mcol2.metric("Churn AUC-ROC", f"{churn_metrics['auc_roc']:.3f}", help="Target: ≥ 0.88")
mcol3.metric("Churn Precision@Top-20%", f"{churn_metrics['precision_at_top20']:.2f}", help="Target: ≥ 0.75")
mcol4.metric("Customer Segments", f"{segments['Segment'].nunique()}")

st.markdown("---")

# --- Revenue Trend + Segment Mix ---
left, right = st.columns([2, 1])

with left:
    st.subheader("Revenue Trend")
    daily_revenue = sales.groupby(sales["InvoiceDate"].dt.date)["TotalPrice"].sum().reset_index()
    daily_revenue.columns = ["Date", "Revenue"]
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=daily_revenue["Date"], y=daily_revenue["Revenue"],
                              mode="lines", line=dict(color=PRIMARY_COLOR, width=1.5)))
    fig.update_layout(template=PLOTLY_TEMPLATE, height=350, margin=dict(l=10, r=10, t=10, b=10))
    st.plotly_chart(fig, use_container_width=True)

with right:
    st.subheader("Customer Segment Mix")
    segment_counts = segments["Segment"].value_counts()
    fig2 = go.Figure(data=[go.Pie(labels=segment_counts.index, values=segment_counts.values, hole=0.4)])
    fig2.update_layout(template=PLOTLY_TEMPLATE, height=350, margin=dict(l=10, r=10, t=10, b=10),
                        showlegend=True)
    st.plotly_chart(fig2, use_container_width=True)

st.info(
    "Use the sidebar to explore Sales Analytics, Customer Segments, Demand Forecast, "
    "Churn Risk, and Inventory Health in detail.",
    icon="👈",
)
