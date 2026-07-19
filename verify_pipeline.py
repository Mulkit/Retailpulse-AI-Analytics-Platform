"""
RetailPulse — Pipeline Verification Script

Run this any time to check which notebooks have produced valid output and
whether the model metrics meet their targets. Doesn't require Jupyter —
just run `python verify_pipeline.py` from the project root in your VS Code
terminal (with your venv activated).
"""
import json
import os
import sys

import pandas as pd

BASE = os.path.dirname(os.path.abspath(__file__))


def check(label, condition, detail=""):
    status = "✅ PASS" if condition else "❌ FAIL"
    print(f"{status}  {label}" + (f"  — {detail}" if detail else ""))
    return condition


def check_file_exists(path):
    full_path = os.path.join(BASE, path)
    exists = os.path.exists(full_path)
    size = f"{os.path.getsize(full_path):,} bytes" if exists else "not found"
    return check(f"File exists: {path}", exists, size)


def check_csv_has_rows(path, min_rows=1):
    full_path = os.path.join(BASE, path)
    if not os.path.exists(full_path):
        return check(f"CSV has data: {path}", False, "file missing")
    try:
        df = pd.read_csv(full_path)
        ok = len(df) >= min_rows
        return check(f"CSV has data: {path}", ok, f"{len(df):,} rows, {len(df.columns)} columns")
    except Exception as e:
        return check(f"CSV has data: {path}", False, f"failed to read: {e}")


def check_json_metric(path, key, target_desc, condition_fn):
    full_path = os.path.join(BASE, path)
    if not os.path.exists(full_path):
        return check(f"Metric check: {path} [{key}]", False, "file missing")
    try:
        with open(full_path) as f:
            data = json.load(f)
        value = data[key]
        ok = condition_fn(value)
        return check(f"Metric check: {path} [{key}]", ok, f"value={value}, target={target_desc}")
    except Exception as e:
        return check(f"Metric check: {path} [{key}]", False, f"failed to read: {e}")


print("=" * 70)
print("RetailPulse — Pipeline Verification")
print("=" * 70)

print("\n--- Day 1-2: Raw & Cleaned Data ---")
results = []
results.append(check_csv_has_rows("data/raw/sales_transactions.csv", min_rows=1000))
results.append(check_csv_has_rows("data/raw/customers_master.csv", min_rows=100))
results.append(check_csv_has_rows("data/raw/products_master.csv", min_rows=10))
results.append(check_csv_has_rows("data/processed/sales_cleaned.csv", min_rows=1000))
results.append(check_csv_has_rows("data/processed/rfm_features.csv", min_rows=100))

print("\n--- Day 3: Segmentation ---")
results.append(check_csv_has_rows("data/processed/customer_segments.csv", min_rows=100))

print("\n--- Day 4-8: Forecasting ---")
results.append(check_csv_has_rows("data/processed/prophet_ready.csv", min_rows=100))
results.append(check_json_metric("models/prophet_metrics.json", "mape", "<= 12%", lambda v: v <= 12))
results.append(check_json_metric("models/lstm_metrics.json", "mape", "<= 12%", lambda v: v <= 12))
results.append(check_csv_has_rows("data/processed/hybrid_forecast_30d.csv", min_rows=25))
results.append(check_json_metric("models/hybrid_metrics.json", "mape", "<= 12%", lambda v: v <= 12))

print("\n--- Day 9-11: Churn Prediction ---")
results.append(check_csv_has_rows("data/processed/churn_scores.csv", min_rows=100))
results.append(check_json_metric("models/churn_metrics_tuned.json", "auc_roc", ">= 0.88", lambda v: v >= 0.88))
results.append(check_json_metric("models/churn_metrics_tuned.json", "precision_at_top20", ">= 0.75", lambda v: v >= 0.75))

print("\n--- Day 10: Inventory Optimization ---")
results.append(check_csv_has_rows("data/processed/inventory_recommendations.csv", min_rows=10))

print("\n--- Day 12: Drift Detection ---")
results.append(check_file_exists("data/processed/drift_alert_status.json"))

print("\n" + "=" * 70)
passed = sum(results)
total = len(results)
print(f"RESULT: {passed}/{total} checks passed")
if passed == total:
    print("Everything looks good — the dashboard should have data to read.")
else:
    print("Some checks failed above — re-run the corresponding notebook(s) for")
    print("whichever Day's section shows a FAIL, then run this script again.")
print("=" * 70)

sys.exit(0 if passed == total else 1)
