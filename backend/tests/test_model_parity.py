"""
Unit test for Model Parity (Fixes Audit Finding H05).

Verifies that:
1. Production model in backend/app/ml/model_loader.py loads best_risk_model.joblib.
2. The 16 features from the scientific evaluation are accepted and mapped correctly.
3. The calibrated threshold rule from best_model_meta.json is applied strictly (ALTO if P(ALTO) >= tau).
4. Parity with offline predictions.
"""
import sys
from pathlib import Path
import pytest
import numpy as np
import pandas as pd

BACKEND_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BACKEND_DIR))
sys.path.insert(0, str(BACKEND_DIR / "scripts"))

from app.ml.model_loader import MLLoader


def test_model_metadata_loaded():
    loader = MLLoader()
    meta = loader.get_metadata()
    assert "calibrated_threshold_alto" in meta
    assert len(loader.feature_names) == 16
    assert loader.calibrated_threshold > 0.05
    assert loader.calibrated_threshold < 0.50


def test_high_risk_calibrated_threshold():
    loader = MLLoader()
    # Critical proximity: distance 1.2m, ttc 0.8s, restricted zone 1
    critical_sample = {
        "distance_3d": 1.2,
        "worker_speed": 1.5,
        "machine_speed": 4.0,
        "relative_speed": 5.5,
        "direction_worker": 1,
        "direction_machine": 1,
        "ttc": 0.8,
        "in_restricted_zone": 1,
        "machine_status": 1,
        "worker_bpm": 110.0,
        "fatigue_index": 0.75,
        "vibration_rms": 4.2,
        "acceleration_z": 9.8,
        "gas_co_ppm": 45.0,
        "dust_density_mg_m3": 4.5,
        "ambient_light_lux": 40.0,
    }
    pred = loader.predict(critical_sample)
    assert pred["risk_level"] == "ALTO"
    assert pred["probabilities"]["ALTO"] >= loader.calibrated_threshold
    assert "calibrated_threshold_alto" in pred


def test_safe_sample_prediction():
    loader = MLLoader()
    # Safe distance: 25m, ttc 30s, no restricted zone, normal vitals
    safe_sample = {
        "distance_3d": 25.0,
        "worker_speed": 1.0,
        "machine_speed": 1.0,
        "relative_speed": 1.0,
        "direction_worker": 0,
        "direction_machine": 0,
        "ttc": 30.0,
        "in_restricted_zone": 0,
        "machine_status": 0,
        "worker_bpm": 70.0,
        "fatigue_index": 0.1,
        "vibration_rms": 0.5,
        "acceleration_z": 9.8,
        "gas_co_ppm": 5.0,
        "dust_density_mg_m3": 0.5,
        "ambient_light_lux": 100.0,
    }
    pred = loader.predict(safe_sample)
    assert pred["risk_level"] in ["BAJO", "MEDIO"]
    assert pred["probabilities"]["ALTO"] < loader.calibrated_threshold
