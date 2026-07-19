# RetailPulse: AI-Powered Sales & Retail Analytics Platform

Predictive Demand • Customer Segmentation • Churn Analysis • Inventory Optimization

An end-to-end data science platform that ingests retail sales data and delivers
demand forecasts, customer segmentation, churn prediction, and inventory
optimization recommendations — with a full MLOps layer (experiment tracking,
drift detection, automated retraining) and a production-readiness layer
(Docker, Kubernetes, CI/CD, monitoring).

Built incrementally over a 28-day plan, one module at a time, with every
notebook executed end-to-end and every dashboard page boot-tested before being
marked complete.

## Results

| Model | Metric | Target | Result |
|---|---|---|---|
| Hybrid Forecast (Prophet + LSTM) | MAPE | ≤ 12% | **6.26%** |
| Churn Prediction (XGBoost, Optuna-tuned) | AUC-ROC | ≥ 0.88 | **0.9694** |
| Churn Prediction (XGBoost, Optuna-tuned) | Precision@Top-20% | ≥ 0.75 | **1.00** |

## Project Structure

```
notebooks/          16 Jupyter notebooks, Days 1-27 — data, models, MLOps, validation
dashboard/           9-page Streamlit app — Home, Forecast, Segments, Churn,
                     Inventory, Alerts, Export Center, Project Summary
airflow_dags/        Automated retraining DAG + task modules
docker/              Multi-stage Dockerfile, compose file, pinned requirements
k8s/                 Deployment, Service, Ingress, ConfigMap, HPA, Namespace
.github/workflows/   CI/CD pipeline (lint, test, build, push, deploy)
deployment/          Terraform (AWS ECS) + Cloud Run script (GCP) + deployment guide
monitoring/          Prometheus exporter, scrape config, alert rules, Grafana dashboard
load_testing/        Locust script + executed results
data/, models/       Generated datasets and trained model artifacts
reports/             Every chart, week-checkpoint summary, and the drift HTML report
mlflow.db            SQLite-backed MLflow tracking store — 3 experiments, multiple runs
```

## How to Run

### Notebooks (reproduce the pipeline)
```bash
pip install -r docker/requirements-pipeline.txt
jupyter nbconvert --to notebook --execute --inplace notebooks/01_eda.ipynb
# ... run 02 through 28 in order; each depends on the previous day's output
```

### Dashboard
```bash
pip install -r docker/requirements-dashboard.txt
cd dashboard
streamlit run Home.py
```

### Full containerized stack
```bash
cd docker
docker compose up --build
```
Dashboard: http://localhost:8501 · MLflow UI: http://localhost:5000

## Methodology Highlights

- **Data**: synthetic retail transactions with realistic customer lifecycles
  (signup, sustained activity, or genuine dropout) — built specifically so
  the churn model has real signal to learn from, not a circular label.
- **Forecasting**: Prophet baseline, LSTM (PyTorch, autoregressive rollout),
  and a weight-optimized hybrid ensemble — all three evaluated on the same
  held-out window for a fair comparison.
- **Churn**: time-based cutoff (features before, label from genuine future
  behavior after) to avoid a circular Recency-predicts-Recency setup.
  Hyperparameters tuned via Optuna (40-trial TPE search); explained via SHAP,
  cross-checked against permutation and gain-based importance.
- **Inventory**: ABC (Pareto) classification, EOQ, and ABC-tiered safety
  stock, fed by the forecasting module's demand allocation.
- **MLOps**: every model run logged to MLflow across three experiments;
  Evidently AI drift detection on both features and predictions; an Airflow
  DAG with real promotion governance (retrained challengers only replace the
  incumbent if they measurably improve on it — demonstrated by an actual dry
  run where one model was promoted and one wasn't).

## What Was Actually Executed vs. What's a Ready-to-Run Artifact

Every notebook ran end-to-end with zero errors. Every dashboard page was
individually boot-tested (`streamlit run <page>`, HTTP 200, clean logs). The
Prometheus exporter was run live and served real metric values. Locust ran a
real 30-second load test against the live dashboard (292 requests, 0
failures). Kubernetes manifests passed 5/5 automated cross-reference
consistency checks.

Docker builds, Kubernetes deployment, Terraform provisioning, and GCP Cloud
Run deployment were **not** executed in the environment this was built in (no
Docker daemon, no cloud credentials) — they're syntax-validated, consistency-checked
configuration ready for a live run. See `deployment/CLOUD_DEPLOYMENT_GUIDE.md`
for the full breakdown of what was and wasn't live-tested.

## Technology Stack

Python 3.11 · Pandas/NumPy/Scikit-learn · Prophet · PyTorch (LSTM) · XGBoost ·
SHAP · Optuna · MLflow · Evidently AI · Streamlit · Plotly · ReportLab ·
Docker · Kubernetes · GitHub Actions · Terraform · Prometheus · Grafana ·
Locust
# Retailpulse-AI-Analytics-Platform
