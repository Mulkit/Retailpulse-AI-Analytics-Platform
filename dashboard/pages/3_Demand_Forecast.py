"""
RetailPulse — Demand Forecast page.

Shows the Day 5/6/8 forecasting outputs (Prophet, LSTM, Hybrid) against recent
actuals, and lets the user run a what-if scenario (promotional uplift +
seasonal multiplier) on top of the production hybrid forecast.
"""
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from utils.data_loader import get_hybrid_forecast, get_timeseries_daily, get_hybrid_metrics
from utils.theme import PRIMARY_COLOR, ACCENT_COLOR, PLOTLY_TEMPLATE

st.set_page_config(page_title="RetailPulse | Demand Forecast", page_icon="🔮", layout="wide")
st.title("🔮 Demand Forecast")
st.caption("Prophet + LSTM hybrid ensemble — 30-day ahead revenue forecast")

try:
    forecast = get_hybrid_forecast()
    history = get_timeseries_daily()
    metrics = get_hybrid_metrics()
except FileNotFoundError as e:
    st.error(f"Missing data file: {e.filename}. Run notebooks 04, 05, 06, and 08 first.")
    st.stop()

# --- KPI row ---
col1, col2, col3, col4 = st.columns(4)
col1.metric("Model MAPE (test window)", f"{metrics['mape']:.2f}%", help="Target: ≤ 12%")
col2.metric("Forecast Horizon", "30 days")
col3.metric("Next 30-Day Revenue (forecast)", f"£{forecast['yhat_hybrid'].sum():,.0f}")
col4.metric("Avg Daily Revenue (forecast)", f"£{forecast['yhat_hybrid'].mean():,.0f}")

st.markdown("---")

# --- Model comparison chart ---
st.subheader("Forecast Components: Prophet vs LSTM vs Hybrid")

recent_history = history.tail(90)

fig = go.Figure()
fig.add_trace(go.Scatter(
    x=recent_history["Date"], y=recent_history["Revenue"],
    mode="lines", name="Recent Actual", line=dict(color="#555555", width=1.5),
))
fig.add_trace(go.Scatter(
    x=forecast["ds"], y=forecast["yhat_prophet"],
    mode="lines", name="Prophet", line=dict(color=ACCENT_COLOR, width=1, dash="dot"),
))
fig.add_trace(go.Scatter(
    x=forecast["ds"], y=forecast["yhat_lstm"],
    mode="lines", name="LSTM", line=dict(color="#C0392B", width=1, dash="dot"),
))
fig.add_trace(go.Scatter(
    x=forecast["ds"], y=forecast["yhat_hybrid"],
    mode="lines", name="Hybrid (production)", line=dict(color=PRIMARY_COLOR, width=3),
))
fig.update_layout(template=PLOTLY_TEMPLATE, height=420, legend=dict(orientation="h", y=1.1),
                   margin=dict(l=10, r=10, t=30, b=10), xaxis_title="Date", yaxis_title="Revenue (£)")
st.plotly_chart(fig, use_container_width=True)

st.markdown("---")

# --- What-if scenario tool ---
st.subheader("What-If Scenario Planner")
st.caption("Layer a promotional uplift and/or a seasonal multiplier on top of the production forecast.")

wcol1, wcol2, wcol3 = st.columns(3)
with wcol1:
    promo_uplift_pct = st.slider("Promotional uplift (%)", -20, 50, 0, step=5,
                                  help="e.g. a marketing campaign or discount event")
with wcol2:
    seasonal_multiplier = st.slider("Seasonal demand multiplier", 0.7, 1.5, 1.0, step=0.05,
                                     help="e.g. holiday season effect not fully captured by the model")
with wcol3:
    weekend_boost_pct = st.slider("Weekend boost (%)", 0, 30, 0, step=5,
                                   help="Extra lift applied to Saturday/Sunday forecasted days")

scenario = forecast.copy()
scenario["is_weekend"] = scenario["ds"].dt.dayofweek.isin([5, 6])
scenario["yhat_scenario"] = scenario["yhat_hybrid"] * (1 + promo_uplift_pct / 100) * seasonal_multiplier
scenario.loc[scenario["is_weekend"], "yhat_scenario"] *= (1 + weekend_boost_pct / 100)

baseline_total = forecast["yhat_hybrid"].sum()
scenario_total = scenario["yhat_scenario"].sum()
delta_pct = (scenario_total / baseline_total - 1) * 100

scol1, scol2 = st.columns(2)
scol1.metric("Baseline 30-Day Forecast", f"£{baseline_total:,.0f}")
scol2.metric("Scenario 30-Day Forecast", f"£{scenario_total:,.0f}", delta=f"{delta_pct:+.1f}%")

fig2 = go.Figure()
fig2.add_trace(go.Scatter(x=forecast["ds"], y=forecast["yhat_hybrid"],
                           mode="lines", name="Baseline", line=dict(color=PRIMARY_COLOR, width=2)))
fig2.add_trace(go.Scatter(x=scenario["ds"], y=scenario["yhat_scenario"],
                           mode="lines", name="Scenario", line=dict(color=ACCENT_COLOR, width=2, dash="dash")))
fig2.update_layout(template=PLOTLY_TEMPLATE, height=350, legend=dict(orientation="h", y=1.1),
                    margin=dict(l=10, r=10, t=30, b=10), xaxis_title="Date", yaxis_title="Revenue (£)")
st.plotly_chart(fig2, use_container_width=True)

st.markdown("---")

# --- Forecast table ---
st.subheader("Forecast Detail Table")
display_df = scenario[["ds", "yhat_prophet", "yhat_lstm", "yhat_hybrid", "yhat_scenario"]].copy()
display_df.columns = ["Date", "Prophet", "LSTM", "Hybrid (baseline)", "Scenario"]
display_df["Date"] = display_df["Date"].dt.date
st.dataframe(
    display_df.style.format({c: "£{:,.0f}" for c in display_df.columns if c != "Date"}),
    use_container_width=True, hide_index=True,
)

csv_bytes = display_df.to_csv(index=False).encode("utf-8")
st.download_button(
    "⬇ Download forecast table (CSV)",
    data=csv_bytes,
    file_name="retailpulse_demand_forecast.csv",
    mime="text/csv",
)
