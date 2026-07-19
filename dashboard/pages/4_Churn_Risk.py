"""
RetailPulse — Churn Risk page.

Shows the Day 9/11 XGBoost churn model's scores: risk tier breakdown,
probability distribution, and a filterable table of at-risk customers.
"""
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from utils.data_loader import get_churn_scores, get_churn_metrics
from utils.theme import PLOTLY_TEMPLATE, CHURN_TIER_COLOR_MAP

st.set_page_config(page_title="RetailPulse | Churn Risk", page_icon="⚠️", layout="wide")
st.title("⚠️ Churn Risk Assessment")
st.caption("XGBoost churn classifier, Optuna-tuned, explained via SHAP (see notebooks 09 & 11)")

try:
    churn = get_churn_scores()
    metrics = get_churn_metrics()
except FileNotFoundError as e:
    st.error(f"Missing data file: {e.filename}. Run notebooks 09_churn_xgboost.ipynb and "
             "11_tuning_feature_importance.ipynb first.")
    st.stop()

# --- KPI row ---
col1, col2, col3, col4 = st.columns(4)
col1.metric("Model AUC-ROC", f"{metrics['auc_roc']:.3f}", help="Target: ≥ 0.88")
col2.metric("Precision@Top-20%", f"{metrics['precision_at_top20']:.2f}", help="Target: ≥ 0.75")
high_risk_n = (churn["ChurnRiskTier"] == "High").sum()
col3.metric("High-Risk Customers", f"{high_risk_n:,}")
col4.metric("Avg Churn Probability", f"{churn['ChurnProbability'].mean():.1%}")

st.markdown("---")

left, right = st.columns([1, 2])

with left:
    st.subheader("Risk Tier Distribution")
    tier_counts = churn["ChurnRiskTier"].value_counts().reindex(["Low", "Medium", "High"])
    fig = go.Figure(data=[go.Bar(
        x=tier_counts.index, y=tier_counts.values,
        marker_color=[CHURN_TIER_COLOR_MAP[t] for t in tier_counts.index],
    )])
    fig.update_layout(template=PLOTLY_TEMPLATE, height=380, margin=dict(l=10, r=10, t=10, b=10),
                       yaxis_title="Customers")
    st.plotly_chart(fig, use_container_width=True)

with right:
    st.subheader("Churn Probability Distribution")
    fig2 = px.histogram(churn, x="ChurnProbability", nbins=40, color="ChurnRiskTier",
                         color_discrete_map=CHURN_TIER_COLOR_MAP, template=PLOTLY_TEMPLATE)
    fig2.update_layout(height=380, margin=dict(l=10, r=10, t=10, b=10),
                        legend=dict(orientation="h", y=1.1))
    st.plotly_chart(fig2, use_container_width=True)

st.markdown("---")

# --- Recency vs churn probability ---
st.subheader("Recency vs Churn Probability")
st.caption("Recency is the dominant driver per the SHAP analysis in notebook 09 — this view "
           "confirms that relationship visually.")
fig3 = px.scatter(churn, x="Recency", y="ChurnProbability", color="ChurnRiskTier",
                   color_discrete_map=CHURN_TIER_COLOR_MAP, opacity=0.5,
                   hover_data=["CustomerID", "Frequency", "Monetary"], template=PLOTLY_TEMPLATE)
fig3.update_layout(height=400, margin=dict(l=10, r=10, t=10, b=10), legend=dict(orientation="h", y=1.1))
st.plotly_chart(fig3, use_container_width=True)

st.markdown("---")

# --- At-risk customer table ---
st.subheader("At-Risk Customer Lookup")
tier_filter = st.multiselect("Filter by risk tier", options=["Low", "Medium", "High"],
                             default=["High"])
min_monetary = st.slider("Minimum lifetime value (£)", 0, int(churn["Monetary"].max()), 0, step=100)

filtered = churn[churn["ChurnRiskTier"].isin(tier_filter) & (churn["Monetary"] >= min_monetary)]
display_cols = ["CustomerID", "ChurnRiskTier", "ChurnProbability", "Recency", "Frequency",
                 "Monetary", "TenureDays"]
st.dataframe(
    filtered[display_cols].sort_values("ChurnProbability", ascending=False).style.format(
        {"ChurnProbability": "{:.1%}", "Monetary": "£{:,.0f}"}),
    use_container_width=True, hide_index=True, height=350,
)
st.caption(f"Showing {len(filtered):,} of {len(churn):,} customers — prioritize outreach to "
           "high-value, high-risk customers at the top of this list.")

csv_bytes = filtered[display_cols].to_csv(index=False).encode("utf-8")
st.download_button(
    "⬇ Download at-risk customer list (CSV)",
    data=csv_bytes,
    file_name="retailpulse_churn_risk.csv",
    mime="text/csv",
)
