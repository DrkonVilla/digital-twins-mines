"""
Export Production ML Pipeline & Metadata (Fixes H05).

Trains the reproducible 16-feature XGBoost pipeline on the 80% train set
and exports:
  1. backend/app/ml/artifacts/best_risk_model.joblib
  2. backend/app/ml/artifacts/best_model_meta.json
"""
import json
import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

import joblib
import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.pipeline import Pipeline
from xgboost import XGBClassifier
from imblearn.over_sampling import SMOTE

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DATA_PATH = PROJECT_ROOT / "data" / "raw" / "public_mining_equipment_dataset.csv"
ARTIFACTS_DIR = PROJECT_ROOT / "backend" / "app" / "ml" / "artifacts"
RESULTS_DIR = PROJECT_ROOT / "results"
ARTIFACTS_DIR.mkdir(parents=True, exist_ok=True)

SCRIPTS_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPTS_DIR))
import fair_eval as fe


def main():
    print("=== Exporting Production ML Model Pipeline (Fixing H05) ===")
    df = fe.load_dataset(DATA_PATH)
    X_train, X_test, y_train, y_test = fe.split_train_test(df)

    # 1. Read calibrated threshold from fair_comparison_results.json
    fair_results_path = RESULTS_DIR / "fair_comparison_results.json"
    if fair_results_path.exists():
        with open(fair_results_path, "r", encoding="utf-8") as f:
            fair_data = json.load(f)
        calibrated_threshold = fair_data["models"]["XGBoost"]["test_calibrated"]["threshold"]
        test_metrics = fair_data["models"]["XGBoost"]["test_calibrated"]
    else:
        calibrated_threshold = 0.14
        test_metrics = {"f2_alto": 0.9065, "recall_alto": 0.9477, "precision_alto": 0.7722}

    print(f"Features in pipeline ({len(fe.FEATURES)}): {fe.FEATURES}")
    print(f"Calibrated threshold for ALTO: {calibrated_threshold}")

    # 2. Build and fit pipeline on 80% development set using the exact research pipeline
    # Guarantees 100% identical preprocessing and model weights as evaluated in fair_eval.py
    num_cols = [f for f in fe.FEATURES if f not in fe.CATEGORICAL]
    prod_pipeline = fe.make_pipeline("XGBoost")
    prod_pipeline.fit(X_train, y_train)

    # 4. Verify test holdout metrics with calibrated threshold
    probas = prod_pipeline.predict_proba(X_test)
    preds_calib = fe.apply_threshold(probas, calibrated_threshold)
    eval_metrics = fe.alto_metrics(y_test, preds_calib)
    print(f"Holdout Test Verification: F2={eval_metrics['f2_alto']:.4f}, Recall={eval_metrics['recall_alto']:.4f}, Precision={eval_metrics['precision_alto']:.4f}")

    # 5. Save model artifact
    model_save_path = ARTIFACTS_DIR / "best_risk_model.joblib"
    joblib.dump(prod_pipeline, model_save_path)
    print(f"Saved production model to: {model_save_path}")

    # 6. Save metadata
    meta = {
        "model_name": "XGBoost (Calibrado)",
        "algorithm": "XGBClassifier(n_estimators=150, max_depth=6, learning_rate=0.1)",
        "timestamp_utc": pd.Timestamp.now(tz="UTC").isoformat(),
        "n_features": len(fe.FEATURES),
        "feature_names": fe.FEATURES,
        "categorical_features": fe.CATEGORICAL,
        "numerical_features": num_cols,
        "calibrated_threshold_alto": float(calibrated_threshold),
        "decision_rule": f"Predice ALTO (2) si P(ALTO) >= {calibrated_threshold:.2f}, sino argmax(BAJO, MEDIO)",
        "test_holdout_metrics": {
            "f2_alto": eval_metrics["f2_alto"],
            "recall_alto": eval_metrics["recall_alto"],
            "precision_alto": eval_metrics["precision_alto"],
            "f1_alto": eval_metrics["f1_alto"]
        },
        "scientific_reference": "Protocolo simetrico con calibracion en OOF (M-11 Acta Montanistica Slovaca 2026)"
    }
    meta_save_path = ARTIFACTS_DIR / "best_model_meta.json"
    with open(meta_save_path, "w", encoding="utf-8") as f:
        json.dump(meta, f, indent=2)
    print(f"Saved metadata to: {meta_save_path}")
    print("=== Model and Metadata Export Complete! ===")


if __name__ == "__main__":
    main()
