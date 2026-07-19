"""
RetailPulse — Inventory Health & Optimization page.

Shows the Day 10 ABC analysis, EOQ/reorder-point recommendations, and current
stock-risk flags, with a filterable table and CSV export.
"""
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from utils.data_loader import get_inventory_recommendations
from utils.theme import PLOTLY_TEMPLATE, RISK_COLOR_MAP

st.set_page_config(page_title="RetailPulse | Inventory Health", page_icon="📦", layout="wide")
st.title("📦 Inventory Health & Optimization")
st.caption("ABC analysis + Economic Order Quantity (EOQ) — see notebook 10_inventory_optimization.ipynb")

try:
    inventory = get_inventory_recommendations()
except FileNotFoundError as e:
    st.error(f"Missing data file: {e.filename}. Run notebook 10_inventory_optimization.ipynb first.")
    st.stop()

# --- KPI row ---
col1, col2, col3, col4 = st.columns(4)
col1.metric("SKUs Tracked", f"{len(inventory):,}")
col2.metric("Need Reorder Now", f"{(inventory['RecommendedOrderQty'] > 0).sum():,}")
col3.metric("Understock Risk", f"{(inventory['StockRisk'] == 'Understock Risk').sum():,}")
col4.metric("Overstock Risk", f"{(inventory['StockRisk'] == 'Overstock Risk').sum():,}")

st.markdown("---")

left, right = st.columns([1, 1])

with left:
    st.subheader("ABC Classification")
    abc_counts = inventory["ABC_Category"].value_counts().reindex(["A", "B", "C"])
    fig = go.Figure(data=[go.Bar(
        x=[f"Class {c}" for c in abc_counts.index], y=abc_counts.values,
        marker_color=["#C0392B", "#F26B21", "#2E8B57"],
    )])
    fig.update_layout(template=PLOTLY_TEMPLATE, height=380, margin=dict(l=10, r=10, t=10, b=10),
                       yaxis_title="Number of SKUs")
    st.plotly_chart(fig, use_container_width=True)

with right:
    st.subheader("Stock Risk Breakdown")
    risk_counts = inventory["StockRisk"].value_counts()
    fig2 = go.Figure(data=[go.Pie(
        labels=risk_counts.index, values=risk_counts.values, hole=0.4,
        marker_colors=[RISK_COLOR_MAP[r] for r in risk_counts.index],
    )])
    fig2.update_layout(template=PLOTLY_TEMPLATE, height=380, margin=dict(l=10, r=10, t=10, b=10))
    st.plotly_chart(fig2, use_container_width=True)

st.markdown("---")

st.subheader("Revenue Contribution by ABC Class")
fig3 = px.bar(inventory.sort_values("TotalRevenue", ascending=False),
              x="StockCode", y="TotalRevenue", color="ABC_Category",
              color_discrete_map={"A": "#C0392B", "B": "#F26B21", "C": "#2E8B57"},
              template=PLOTLY_TEMPLATE)
fig3.update_layout(height=350, margin=dict(l=10, r=10, t=10, b=10), xaxis_visible=False,
                    yaxis_title="Total Revenue (£)")
st.plotly_chart(fig3, use_container_width=True)

st.markdown("---")

# --- Filterable reorder table ---
st.subheader("Reorder Recommendations")
fcol1, fcol2 = st.columns(2)
with fcol1:
    abc_filter = st.multiselect("ABC Class", options=["A", "B", "C"], default=["A", "B", "C"])
with fcol2:
    risk_filter = st.multiselect("Stock Risk", options=["Healthy", "Understock Risk", "Overstock Risk"],
                                 default=["Understock Risk"])

filtered = inventory[inventory["ABC_Category"].isin(abc_filter) & inventory["StockRisk"].isin(risk_filter)]
filtered = filtered.sort_values("RecommendedOrderQty", ascending=False)

st.dataframe(
    filtered.style.format({"TotalRevenue": "£{:,.0f}", "ForecastedAnnualDemand": "{:,.0f}",
                            "EOQ": "{:,.0f}", "ReorderPoint": "{:,.0f}", "SafetyStock": "{:,.0f}",
                            "CurrentStock": "{:,.0f}", "RecommendedOrderQty": "{:,.0f}"}),
    use_container_width=True, hide_index=True, height=400,
)
st.caption(f"Showing {len(filtered):,} of {len(inventory):,} SKUs.")

csv_bytes = filtered.to_csv(index=False).encode("utf-8")
st.download_button(
    "⬇ Download filtered recommendations (CSV)",
    data=csv_bytes,
    file_name="retailpulse_inventory_recommendations.csv",
    mime="text/csv",
)
