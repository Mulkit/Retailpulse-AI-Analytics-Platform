"""
Retraining tasks for the RetailPulse pipeline. Each function is intentionally
a thin orchestration layer — the actual model-fitting code lives in the
Day 5/6/9/11 notebooks; these wrappers exist so Airflow can call them as
independent, retryable tasks.
"""


def retrain_prophet(**context):
    """Refits the Prophet baseline on the latest cleaned data.
    Mirrors notebooks/05_prophet_baseline.ipynb section 6 (production refit)."""
    raise NotImplementedError(
        "Production implementation calls the same fit routine as "
        "05_prophet_baseline.ipynb; see notebooks/13_retraining_pipeline.ipynb "
        "for the executed equivalent used to validate this logic."
    )


def retrain_lstm(**context):
    """Retrains the LSTM forecaster. Mirrors notebooks/06_lstm_forecaster.ipynb."""
    raise NotImplementedError(
        "Production implementation calls the same training loop as "
        "06_lstm_forecaster.ipynb. Skipped in the Day 13 local dry-run to keep "
        "iteration time short — see notebook for rationale."
    )


def retrain_churn_model(**context):
    """Retrains the XGBoost churn classifier with the Day 11 tuned hyperparameters."""
    raise NotImplementedError(
        "Production implementation reuses the Optuna-tuned params from "
        "11_tuning_feature_importance.ipynb and refits on the latest cutoff window."
    )


def evaluate_and_compare(**context):
    """Compares newly retrained models against the currently promoted ones on
    a held-out window; only promote if the challenger beats the incumbent."""
    raise NotImplementedError("See notebooks/13_retraining_pipeline.ipynb for the executed logic.")


def promote_best_model(**context):
    """Updates the MLflow Model Registry stage (staging -> production) for any
    challenger that won its evaluation, and leaves the incumbent in place otherwise."""
    raise NotImplementedError("See notebooks/13_retraining_pipeline.ipynb for the executed logic.")
