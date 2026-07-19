"""
RetailPulse — Alerts & Monitoring page.

Surfaces the same alert conditions the Day 12 drift check and Day 13 retraining
pipeline compute, plus live threshold checks on churn and inventory, in one
place. "Real-time" here means: re-reads the underlying files (which the
notebooks/pipeline update) on every manual refresh, rather than a fixed
in-memory snapshot — a manual refresh button stands in for the scheduled
Airflow run status in a live deployment.
"""
import time

import pandas as pd
import streamlit as st

from utils.data_loader import get_churn_scores, get_inventory_recommendations, get_drift_status, get_hybrid_metrics

st.set_page_config(page_title="RetailPulse | Alerts", page_icon="🔔", layout="wide")
st.title("🔔 Alerts & Monitoring")
st.caption("Live threshold checks across drift, churn, and inventory — refresh to re-evaluate against the latest data")

refresh_col, time_col = st.columns([1, 3])
with refresh_col:
    if st.button("🔄 Refresh Now"):
        st.cache_data.clear()
        st.rerun()
with time_col:
    st.caption(f"Last checked: {time.strftime('%Y-%m-%d %H:%M:%S')}")

st.markdown("---")

try:
    churn = get_churn_scores()
    inventory = get_inventory_recommendations()
    drift_status = get_drift_status()
    forecast_metrics = get_hybrid_metrics()
except FileNotFoundError as e:
    st.error(f"Missing data file: {e.filename}. Run the pipeline notebooks first.")
    st.stop()

alerts = []

# --- Drift alert ---
if drift_status.get("retraining_recommended"):
    alerts.append({
        "severity": "🔴 High",
        "area": "Data Drift",
        "message": f"{drift_status['feature_drift_share']*100:.0f}% of monitored features have "
                   f"drifted from the reference window. Automated retraining pipeline triggered "
                   f"(see notebook 13).",
    })
else:
    alerts.append({"severity": "🟢 OK", "area": "Data Drift", "message": "No significant drift detected."})

# --- Churn alert ---
high_risk_count = (churn["ChurnRiskTier"] == "High").sum()
high_risk_share = high_risk_count / len(churn)
if high_risk_share > 0.15:
    alerts.append({
        "severity": "🟠 Medium",
        "area": "Customer Churn",
        "message": f"{high_risk_count:,} customers ({high_risk_share:.1%}) are in the High risk "
                   f"tier — above the 15% watch threshold. Consider a retention campaign.",
    })
else:
    alerts.append({"severity": "🟢 OK", "area": "Customer Churn",
                    "message": f"{high_risk_count:,} customers ({high_risk_share:.1%}) in High risk tier — within normal range."})

# --- Inventory alert ---
understock_count = (inventory["StockRisk"] == "Understock Risk").sum()
if understock_count > 0:
    alerts.append({
        "severity": "🟠 Medium",
        "area": "Inventory",
        "message": f"{understock_count} SKUs are below their reorder point and need restocking "
                   f"— see Inventory Health for the full list.",
    })
else:
    alerts.append({"severity": "🟢 OK", "area": "Inventory", "message": "No SKUs currently below reorder point."})

# --- Forecast accuracy alert ---
if forecast_metrics["mape"] > 12:
    alerts.append({
        "severity": "🔴 High",
        "area": "Forecast Accuracy",
        "message": f"Hybrid forecast MAPE is {forecast_metrics['mape']:.2f}%, above the 12% target.",
    })
else:
    alerts.append({"severity": "🟢 OK", "area": "Forecast Accuracy",
                    "message": f"Hybrid forecast MAPE is {forecast_metrics['mape']:.2f}%, within target."})

alerts_df = pd.DataFrame(alerts)
n_active = sum(1 for a in alerts if "OK" not in a["severity"])

st.subheader(f"Active Alerts ({n_active} of {len(alerts)} checks flagged)")
for _, row in alerts_df.iterrows():
    if "High" in row["severity"]:
        st.error(f"{row['severity']} — **{row['area']}**: {row['message']}")
    elif "Medium" in row["severity"]:
        st.warning(f"{row['severity']} — **{row['area']}**: {row['message']}")
    else:
        st.success(f"{row['severity']} — **{row['area']}**: {row['message']}")

st.markdown("---")
st.subheader("Alert History Table")
st.dataframe(alerts_df, use_container_width=True, hide_index=True)

st.caption(
    "In production, this page's checks run on the Day 13 Airflow schedule rather than on "
    "manual refresh, and would push to Slack/email via the DAG's `send_alert` task."
)
