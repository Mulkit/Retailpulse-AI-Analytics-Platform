#!/usr/bin/env bash
# RetailPulse — Run every notebook workflow, in order, from the terminal.
#
# Usage (from the project root, with your venv activated):
#   bash run_all_notebooks.sh
#
# Runs one notebook at a time and stops immediately if one fails, so you
# always know exactly which workflow broke.

set -e  # stop the whole script if any single command fails

NB_DIR="notebooks"

run_notebook () {
    local name="$1"
    local file="$2"
    echo ""
    echo "=================================================================="
    echo "WORKFLOW: $name"
    echo "File: $NB_DIR/$file"
    echo "=================================================================="
    jupyter nbconvert --to notebook --execute --inplace "$NB_DIR/$file" \
        --ExecutePreprocessor.timeout=600
    echo "✅ DONE: $name"
}

# --- Week 1: Data & Baseline Models ---
run_notebook "Day 1 - Data Generation & EDA"              "01_eda.ipynb"
run_notebook "Day 2 - Cleaning & Feature Engineering"      "02_cleaning_features.ipynb"
run_notebook "Day 3 - Customer Segmentation"               "03_segmentation.ipynb"
run_notebook "Day 4 - Time-Series Prep"                    "04_timeseries_prep.ipynb"
run_notebook "Day 5 - Prophet Baseline Forecast"            "05_prophet_baseline.ipynb"
run_notebook "Day 6 - LSTM Forecaster"                      "06_lstm_forecaster.ipynb"
run_notebook "Day 7 - Week 1 Checkpoint"                    "07_week1_checkpoint.ipynb"

# --- Week 2: Advanced Modeling & MLOps ---
run_notebook "Day 8 - Hybrid Forecast Ensemble"             "08_hybrid_ensemble.ipynb"
run_notebook "Day 9 - Churn Prediction (XGBoost)"           "09_churn_xgboost.ipynb"
run_notebook "Day 10 - Inventory Optimization"              "10_inventory_optimization.ipynb"
run_notebook "Day 11 - Hyperparameter Tuning (Optuna)"      "11_tuning_feature_importance.ipynb"
run_notebook "Day 12 - Drift Detection"                     "12_drift_detection.ipynb"
run_notebook "Day 13 - Retraining Pipeline Dry-Run"         "13_retraining_pipeline.ipynb"
run_notebook "Day 14 - Week 2 Checkpoint"                   "14_week2_checkpoint.ipynb"

echo ""
echo "=================================================================="
echo "ALL WORKFLOWS COMPLETE"
echo "=================================================================="
echo "Now run: python verify_pipeline.py"
echo "Then:    cd dashboard && streamlit run Home.py"
