"""
RetailPulse — Model Metrics Exporter for Prometheus.

The dashboard itself has no natural request-level metrics worth exporting
(it's a read-only Streamlit app over static files), so what's actually worth
monitoring in production is model health: forecast accuracy, churn model
performance, and drift status — the same numbers Day 12/13's pipeline
already computes. This script re-reads those JSON artifacts on a fixed
interval and exposes them as Prometheus gauges on :9105/metrics.

Run standalone:
    python monitoring/model_metrics_exporter.py

Or as a sidecar container next to the dashboard in the same Pod (see
k8s/deployment.yaml, which would need a second container added for this).
"""
import json
import time
from pathlib import Path

from prometheus_client import Gauge, start_http_server

BASE_DIR = Path(__file__).resolve().parents[1]
MODELS_DIR = BASE_DIR / "models"
PROCESSED_DIR = BASE_DIR / "data" / "processed"
SCRAPE_INTERVAL_SECONDS = 30

forecast_mape = Gauge("retailpulse_forecast_mape_percent", "Hybrid forecast MAPE (%)")
churn_auc = Gauge("retailpulse_churn_auc_roc", "Churn model AUC-ROC")
churn_precision_top20 = Gauge("retailpulse_churn_precision_top20", "Churn model precision@top-20%")
drift_feature_share = Gauge("retailpulse_drift_feature_share", "Share of monitored features currently drifted")
drift_retrain_recommended = Gauge("retailpulse_drift_retrain_recommended", "1 if the drift check recommends retraining, else 0")


def _read_json(path: Path) -> dict:
    with open(path) as f:
        return json.load(f)


def refresh_metrics() -> None:
    try:
        hybrid = _read_json(MODELS_DIR / "hybrid_metrics.json")
        forecast_mape.set(hybrid["mape"])
    except (FileNotFoundError, KeyError) as e:
        print(f"[exporter] could not read hybrid_metrics.json: {e}")

    try:
        churn = _read_json(MODELS_DIR / "churn_metrics_tuned.json")
        churn_auc.set(churn["auc_roc"])
        churn_precision_top20.set(churn["precision_at_top20"])
    except (FileNotFoundError, KeyError) as e:
        print(f"[exporter] could not read churn_metrics_tuned.json: {e}")

    try:
        drift = _read_json(PROCESSED_DIR / "drift_alert_status.json")
        drift_feature_share.set(drift["feature_drift_share"])
        drift_retrain_recommended.set(1 if drift["retraining_recommended"] else 0)
    except (FileNotFoundError, KeyError) as e:
        print(f"[exporter] could not read drift_alert_status.json: {e}")


if __name__ == "__main__":
    start_http_server(9105)
    print("RetailPulse model metrics exporter listening on :9105/metrics")
    while True:
        refresh_metrics()
        time.sleep(SCRAPE_INTERVAL_SECONDS)
