def send_alert(**context):
    """Sends a Slack/email summary of the retraining run outcome.
    Placeholder — wire up to the team's actual notification channel in deployment."""
    drift_status = context["ti"].xcom_pull(task_ids="check_drift", key="drift_status")
    print(f"[RetailPulse MLOps] Pipeline run complete. Drift status: {drift_status}")
