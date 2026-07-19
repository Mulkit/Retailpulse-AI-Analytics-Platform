"""
RetailPulse — Automated Retraining DAG

Orchestrates the drift-check -> conditional-retrain -> evaluate -> promote workflow.
Designed to run daily; each task is a thin wrapper around the same pipeline functions
used interactively in notebooks/13_retraining_pipeline.ipynb, so the DAG and the notebook
stay in sync rather than duplicating logic.

NOTE: this file defines the DAG for a real Airflow deployment (Day 22-25's containerized
environment). It is not executed inside this notebook sandbox — Day 13's notebook instead
runs the same underlying Python functions directly to prove the pipeline logic end-to-end.
"""
from datetime import datetime, timedelta

from airflow import DAG
from airflow.operators.python import PythonOperator, BranchPythonOperator
from airflow.operators.empty import EmptyOperator

from retailpulse_pipeline.drift import check_drift
from retailpulse_pipeline.retrain import (
    retrain_prophet,
    retrain_lstm,
    retrain_churn_model,
    evaluate_and_compare,
    promote_best_model,
)
from retailpulse_pipeline.notify import send_alert

default_args = {
    "owner": "retailpulse-mlops",
    "retries": 2,
    "retry_delay": timedelta(minutes=10),
    "email_on_failure": True,
}

with DAG(
    dag_id="retailpulse_retraining_pipeline",
    description="Drift-triggered retraining for RetailPulse forecasting and churn models",
    default_args=default_args,
    schedule_interval="@daily",
    start_date=datetime(2026, 1, 1),
    catchup=False,
    tags=["retailpulse", "mlops", "retraining"],
) as dag:

    check_drift_task = PythonOperator(
        task_id="check_drift",
        python_callable=check_drift,
        doc_md="Runs the Evidently AI drift report (same logic as notebooks/12_drift_detection.ipynb) "
               "and pushes a retrain/no-retrain decision to XCom.",
    )

    def _branch_on_drift(**context):
        needs_retrain = context["ti"].xcom_pull(task_ids="check_drift")["retraining_recommended"]
        return "retrain_group.retrain_prophet" if needs_retrain else "skip_retraining"

    branch_task = BranchPythonOperator(
        task_id="branch_on_drift",
        python_callable=_branch_on_drift,
    )

    skip_retraining = EmptyOperator(task_id="skip_retraining")

    with dag.subdag_or_taskgroup if False else __import__("contextlib").nullcontext():
        pass  # placeholder to keep structure readable; TaskGroup used below

    from airflow.utils.task_group import TaskGroup

    with TaskGroup(group_id="retrain_group") as retrain_group:
        retrain_prophet_task = PythonOperator(
            task_id="retrain_prophet",
            python_callable=retrain_prophet,
        )
        retrain_lstm_task = PythonOperator(
            task_id="retrain_lstm",
            python_callable=retrain_lstm,
        )
        retrain_churn_task = PythonOperator(
            task_id="retrain_churn_model",
            python_callable=retrain_churn_model,
        )
        evaluate_task = PythonOperator(
            task_id="evaluate_and_compare",
            python_callable=evaluate_and_compare,
        )
        promote_task = PythonOperator(
            task_id="promote_best_model",
            python_callable=promote_best_model,
        )

        [retrain_prophet_task, retrain_lstm_task, retrain_churn_task] >> evaluate_task >> promote_task

    notify_task = PythonOperator(
        task_id="send_alert",
        python_callable=send_alert,
        trigger_rule="none_failed_min_one_success",
    )

    check_drift_task >> branch_task >> [retrain_group, skip_retraining]
    [retrain_group, skip_retraining] >> notify_task
