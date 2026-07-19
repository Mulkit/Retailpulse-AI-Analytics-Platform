"""
Shared, cached data-loading utilities for the RetailPulse dashboard.

Every page imports from here rather than reading CSVs directly — one cache
per file, refreshed only when the underlying file's mtime changes, and one
place to update if a file path or schema changes.
"""
import json
from pathlib import Path

import pandas as pd
import streamlit as st

DATA_DIR = Path(__file__).resolve().parents[2] / "data"
MODELS_DIR = Path(__file__).resolve().parents[2] / "models"
RAW_DIR = DATA_DIR / "raw"
PROCESSED_DIR = DATA_DIR / "processed"


def _mtime(path: Path) -> float:
    return path.stat().st_mtime if path.exists() else -1.0


@st.cache_data(show_spinner=False)
def load_sales_cleaned(_mtime_key: float) -> pd.DataFrame:
    return pd.read_csv(PROCESSED_DIR / "sales_cleaned.csv", parse_dates=["InvoiceDate"])


@st.cache_data(show_spinner=False)
def load_customer_segments(_mtime_key: float) -> pd.DataFrame:
    return pd.read_csv(PROCESSED_DIR / "customer_segments.csv")


@st.cache_data(show_spinner=False)
def load_churn_scores(_mtime_key: float) -> pd.DataFrame:
    return pd.read_csv(PROCESSED_DIR / "churn_scores.csv")


@st.cache_data(show_spinner=False)
def load_hybrid_forecast(_mtime_key: float) -> pd.DataFrame:
    return pd.read_csv(PROCESSED_DIR / "hybrid_forecast_30d.csv", parse_dates=["ds"])


@st.cache_data(show_spinner=False)
def load_timeseries_daily(_mtime_key: float) -> pd.DataFrame:
    return pd.read_csv(PROCESSED_DIR / "timeseries_daily.csv", parse_dates=["Date"])


@st.cache_data(show_spinner=False)
def load_inventory_recommendations(_mtime_key: float) -> pd.DataFrame:
    return pd.read_csv(PROCESSED_DIR / "inventory_recommendations.csv")


@st.cache_data(show_spinner=False)
def load_products(_mtime_key: float) -> pd.DataFrame:
    return pd.read_csv(RAW_DIR / "products_master.csv")


@st.cache_data(show_spinner=False)
def load_json(path: Path, _mtime_key: float) -> dict:
    with open(path) as f:
        return json.load(f)


# --- Public accessors: call these from pages; they resolve the mtime key internally ---

def get_sales_cleaned() -> pd.DataFrame:
    path = PROCESSED_DIR / "sales_cleaned.csv"
    return load_sales_cleaned(_mtime(path))


def get_customer_segments() -> pd.DataFrame:
    path = PROCESSED_DIR / "customer_segments.csv"
    return load_customer_segments(_mtime(path))


def get_churn_scores() -> pd.DataFrame:
    path = PROCESSED_DIR / "churn_scores.csv"
    return load_churn_scores(_mtime(path))


def get_hybrid_forecast() -> pd.DataFrame:
    path = PROCESSED_DIR / "hybrid_forecast_30d.csv"
    return load_hybrid_forecast(_mtime(path))


def get_timeseries_daily() -> pd.DataFrame:
    path = PROCESSED_DIR / "timeseries_daily.csv"
    return load_timeseries_daily(_mtime(path))


def get_inventory_recommendations() -> pd.DataFrame:
    path = PROCESSED_DIR / "inventory_recommendations.csv"
    return load_inventory_recommendations(_mtime(path))


def get_products() -> pd.DataFrame:
    path = RAW_DIR / "products_master.csv"
    return load_products(_mtime(path))


def get_hybrid_metrics() -> dict:
    path = MODELS_DIR / "hybrid_metrics.json"
    return load_json(path, _mtime(path))


def get_churn_metrics() -> dict:
    path = MODELS_DIR / "churn_metrics_tuned.json"
    return load_json(path, _mtime(path))


def get_drift_status() -> dict:
    path = PROCESSED_DIR / "drift_alert_status.json"
    return load_json(path, _mtime(path))
