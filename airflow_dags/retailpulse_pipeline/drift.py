"""
Drift-check task — thin wrapper around the same logic as
notebooks/12_drift_detection.ipynb, so the Airflow DAG and the interactive
notebook never drift apart from each other.
"""
import json
import os

DRIFT_STATUS_PATH = os.path.join(
    os.path.dirname(__file__), "..", "..", "data", "processed", "drift_alert_status.json"
)


def check_drift(**context):
    """Reads the latest drift-alert status produced by the Day 12 drift-detection
    step and returns it so downstream tasks can branch on `retraining_recommended`.

    In production this would re-run the Evidently AI report against the freshest
    data before returning the decision; here it reads the persisted status file
    to keep the DAG and the notebook pipeline logic identical.
    """
    with open(DRIFT_STATUS_PATH) as f:
        status = json.load(f)

    context["ti"].xcom_push(key="drift_status", value=status)
    return status
