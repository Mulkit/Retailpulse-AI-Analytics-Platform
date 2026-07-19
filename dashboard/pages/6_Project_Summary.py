import streamlit as st

st.set_page_config(page_title="RetailPulse | Project Summary", page_icon="📑", layout="wide")
st.title("📑 Project Summary")

st.markdown("""
### RetailPulse: AI-Powered Sales & Retail Analytics Platform

An end-to-end data science platform delivering demand forecasting, customer
segmentation, churn prediction, and inventory optimization for retail businesses.

#### Pipeline
Raw Sales Data → Data Cleaning → Feature Engineering → Customer Segmentation &
Churn Prediction → Forecasting Models (Prophet + LSTM + Hybrid) → Inventory
Optimization → Streamlit Dashboard → MLflow Tracking & Monitoring

#### Modeling Techniques
- **Customer Segmentation** — RFM + K-Means / DBSCAN
- **Churn Prediction** — XGBoost, tuned via Optuna, explained via SHAP
- **Demand Forecasting** — Prophet + LSTM hybrid ensemble
- **Inventory Optimization** — ABC analysis + EOQ

#### MLOps Practices
- MLflow experiment tracking across forecasting, churn, and retraining
- Evidently AI drift detection (data + prediction drift)
- Airflow-orchestrated automated retraining with promotion governance
- Optuna hyperparameter tuning

#### Technology Stack
| Category | Technology |
|---|---|
| Language | Python 3.12 |
| Data Processing | Pandas, NumPy, Scikit-learn |
| Forecasting | Prophet, PyTorch (LSTM) |
| Dashboard | Streamlit, Plotly |
| Experiment Tracking | MLflow |
| Drift Detection | Evidently AI |
| Hyperparameter Tuning | Optuna |
| Orchestration | Apache Airflow |
""")

st.success("Built incrementally, module by module, with every component executed and validated end-to-end.")
