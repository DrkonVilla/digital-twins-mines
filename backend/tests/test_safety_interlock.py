"""
Unit tests for Deterministic Safety Interlocks (Fixes Audit Finding H12).

Verifies that:
1. Critical proximity, restricted zone or high risk alerts ALWAYS trigger safety lockout.
2. Gas concentration alerts trigger mandatory evacuation orders under D.S. 024-2016-EM.
3. Fatigue alerts trigger mandatory shift relief.
4. Deterministic rules cannot be overridden by LLM output.
"""
import sys
from pathlib import Path
import pytest

BACKEND_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BACKEND_DIR))

from app.services.gemini_service import DeterministicSafetyInterlock


def test_proximity_safety_lockout():
    alert = {
        "alert_level": "ALTO",
        "message": "Operario ingresó a zona restringida de ScoopTram (distancia 1.5m)",
        "worker_id": 1,
        "machine_id": 1,
    }
    res = DeterministicSafetyInterlock.evaluate_rules(alert)
    assert res["safety_lockout_active"] is True
    assert res["override_allowed_by_llm"] is False
    assert any("PARADA DE EMERGENCIA" in m for m in res["deterministic_mandates"])
    assert any("272" in r for r in res["normative_references"])


def test_gas_evacuation_mandate():
    alert = {
        "alert_level": "CRITICO",
        "message": "Concentración de gas monóxido CO elevada (45 ppm)",
        "worker_id": 2,
        "machine_id": 1,
    }
    res = DeterministicSafetyInterlock.evaluate_rules(alert)
    assert res["safety_lockout_active"] is True
    assert any("EVACUACIÓN" in m for m in res["deterministic_mandates"])
    assert any("VENTILACIÓN" in m for m in res["deterministic_mandates"])


def test_fatigue_mandate():
    alert = {
        "alert_level": "MEDIO",
        "message": "Operador presenta índice de fatiga psicofisiológica severo (0.82)",
        "worker_id": 3,
        "machine_id": 1,
    }
    res = DeterministicSafetyInterlock.evaluate_rules(alert)
    assert any("RELEVO OBLIGATORIO" in m for m in res["deterministic_mandates"])
