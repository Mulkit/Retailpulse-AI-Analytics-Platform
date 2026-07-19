"""
RetailPulse — Sales Analytics page.

Detailed sales breakdown: revenue trend (daily + monthly), top products by
revenue and by units sold, and revenue by country — with a date range filter.
"""
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from utils.data_loader import get_sales_cleaned
from utils.theme import PRIMARY_COLOR, ACCENT_COLOR, PLOTLY_TEMPLATE

st.set_page_config(page_title="RetailPulse | Sales Analytics", page_icon="📈", layout="wide")
st.title("📈 Sales Analytics")
st.caption("Revenue trends, top products, and country performance — from cleaned transaction data")

try:
    sales = get_sales_cleaned()
except FileNotFoundError as e:
    st.error(f"Missing data file: {e.filename}. Run notebook 02_cleaning_features.ipynb first.")
    st.stop()

# --- Date range filter ---
min_date, max_date = sales["InvoiceDate"].min().date(), sales["InvoiceDate"].max().date()
date_range = st.date_input(
    "Date range", value=(min_date, max_date), min_value=min_date, max_value=max_date,
)
if len(date_range) == 2:
    start_date, end_date = date_range
    filtered = sales[
        (sales["InvoiceDate"].dt.date >= start_date) & (sales["InvoiceDate"].dt.date <= end_date)
    ]
else:
    filtered = sales

st.markdown("---")

# --- KPI row ---
total_revenue = filtered["TotalPrice"].sum()
total_orders = filtered["InvoiceNo"].nunique()
total_units = filtered["Quantity"].sum()
avg_order_value = total_revenue / total_orders if total_orders else 0

col1, col2, col3, col4 = st.columns(4)
col1.metric("Revenue (selected range)", f"£{total_revenue:,.0f}")
col2.metric("Orders", f"{total_orders:,}")
col3.metric("Units Sold", f"{total_units:,}")
col4.metric("Avg Order Value", f"£{avg_order_value:,.2f}")

st.markdown("---")

# --- Daily & monthly revenue trend ---
st.subheader("Revenue Trend")
trend_granularity = st.radio("Granularity", ["Daily", "Monthly"], horizontal=True)

if trend_granularity == "Daily":
    trend = filtered.groupby(filtered["InvoiceDate"].dt.date)["TotalPrice"].sum().reset_index()
    trend.columns = ["Period", "Revenue"]
else:
    trend = filtered.groupby(filtered["InvoiceDate"].dt.to_period("M"))["TotalPrice"].sum().reset_index()
    trend["InvoiceDate"] = trend["InvoiceDate"].astype(str)
    trend.columns = ["Period", "Revenue"]

fig = go.Figure()
fig.add_trace(go.Scatter(x=trend["Period"], y=trend["Revenue"], mode="lines",
                          line=dict(color=PRIMARY_COLOR, width=2), fill="tozeroy",
                          fillcolor="rgba(31,78,121,0.1)"))
fig.update_layout(template=PLOTLY_TEMPLATE, height=380, margin=dict(l=10, r=10, t=10, b=10),
                   xaxis_title="Period", yaxis_title="Revenue (£)")
st.plotly_chart(fig, use_container_width=True)

st.markdown("---")

left, right = st.columns(2)

with left:
    st.subheader("Top 10 Products by Revenue")
    top_by_revenue = (filtered.groupby("Description")["TotalPrice"].sum()
                       .sort_values(ascending=False).head(10).reset_index())
    fig2 = px.bar(top_by_revenue, x="TotalPrice", y="Description", orientation="h",
                   color_discrete_sequence=[PRIMARY_COLOR], template=PLOTLY_TEMPLATE)
    fig2.update_layout(height=400, margin=dict(l=10, r=10, t=10, b=10),
                        yaxis={"categoryorder": "total ascending"}, xaxis_title="Revenue (£)",
                        yaxis_title="")
    st.plotly_chart(fig2, use_container_width=True)

with right:
    st.subheader("Top 10 Products by Units Sold")
    top_by_units = (filtered.groupby("Description")["Quantity"].sum()
                     .sort_values(ascending=False).head(10).reset_index())
    fig3 = px.bar(top_by_units, x="Quantity", y="Description", orientation="h",
                   color_discrete_sequence=[ACCENT_COLOR], template=PLOTLY_TEMPLATE)
    fig3.update_layout(height=400, margin=dict(l=10, r=10, t=10, b=10),
                        yaxis={"categoryorder": "total ascending"}, xaxis_title="Units",
                        yaxis_title="")
    st.plotly_chart(fig3, use_container_width=True)

st.markdown("---")

# --- Country breakdown ---
st.subheader("Revenue by Country")
country_revenue = (filtered.groupby("Country")["TotalPrice"].sum()
                    .sort_values(ascending=False).reset_index())
fig4 = px.bar(country_revenue.head(10), x="Country", y="TotalPrice",
              color_discrete_sequence=[PRIMARY_COLOR], template=PLOTLY_TEMPLATE)
fig4.update_layout(height=380, margin=dict(l=10, r=10, t=10, b=10), yaxis_title="Revenue (£)")
st.plotly_chart(fig4, use_container_width=True)

st.markdown("---")

# --- Data table ---
st.subheader("Country Detail Table")
country_revenue["TotalPrice"] = country_revenue["TotalPrice"].round(0)
st.dataframe(
    country_revenue.rename(columns={"TotalPrice": "Revenue (£)"}),
    use_container_width=True, hide_index=True,
)
