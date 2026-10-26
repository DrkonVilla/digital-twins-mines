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


def test_no_false_positive_gas_on_collision_message():
    """Verifies that words containing 'co' like 'colisión' or 'correcto' do NOT trigger gas evacuation (Differential Audit 773554b)."""
    alert = {
        "alert_level": "ALTO",
        "hazard": "colision_proximidad",
        "message": "Se detectó colisión inminente entre vehículos y equipo en estado correcto a 2.1 m",
        "worker_id": 4,
        "machine_id": 1,
    }
    res = DeterministicSafetyInterlock.evaluate_rules(alert)
    assert res["safety_lockout_active"] is True
    assert any("PARADA DE EMERGENCIA" in m for m in res["deterministic_mandates"])
    # MUST NOT trigger gas evacuation protocol
    assert not any("EVACUACIÓN" in m for m in res["deterministic_mandates"])
    assert not any("REFUGIO MINERO" in m for m in res["deterministic_mandates"])
    assert not any("252" in r for r in res["normative_references"])


def test_pure_gas_alert_does_not_trigger_collision_stop():
    """Verifies that pure gas alert triggers evacuation without falsely triggering collision/proximity lockout."""
    alert = {
        "alert_level": "CRITICO",
        "hazard": "gas_co",
        "message": "Concentración de gas monóxido CO de 76 ppm en galería norte",
        "worker_id": 5,
        "machine_id": 2,
    }
    res = DeterministicSafetyInterlock.evaluate_rules(alert)
    assert res["safety_lockout_active"] is True
    assert any("EVACUACIÓN" in m for m in res["deterministic_mandates"])
    # MUST NOT trigger proximity exclusion zone stop
    assert not any("PARADA DE EMERGENCIA INMEDIATA: Desconexión" in m for m in res["deterministic_mandates"])
    assert not any("272" in r for r in res["normative_references"])


def test_negation_gas_message_does_not_trigger_evacuation():
    """Verifies that explicit negation like 'No hay gas ... 0 ppm' does NOT trigger evacuation (Audit da81d5f P1)."""
    alert = {
        "alert_level": "ALTO",
        "message": "No hay gas en la labor, concentración normal (0 ppm CO)",
        "worker_id": 6,
        "machine_id": 1,
    }
    res = DeterministicSafetyInterlock.evaluate_rules(alert)
    assert not any("EVACUACIÓN" in m for m in res["deterministic_mandates"])
    assert not any("252" in r for r in res["normative_references"])


def test_critical_dust_hazard_triggers_suspension_and_lockout():
    """Verifies that critical dust (15 mg/m3, 5 lux) triggers transit suspension and lockout (Audit da81d5f P1)."""
    alert = {
        "alert_level": "CRITICO",
        "hazard": "polvo_visibilidad",
        "message": "Polvo en suspensión severo de 15 mg/m3 y visibilidad nula (5 lux) en frente de carguío",
        "worker_id": 7,
        "machine_id": 1,
    }
    res = DeterministicSafetyInterlock.evaluate_rules(alert)
    assert res["safety_lockout_active"] is True
    assert any("SUSPENSIÓN TEMPORAL DE MANIOBRAS" in m for m in res["deterministic_mandates"])
    assert any("SUPRESIÓN DE POLVO" in m for m in res["deterministic_mandates"])
    assert any("104" in r for r in res["normative_references"])
    assert any("105" in r for r in res["normative_references"])
    # MUST NOT falsely trigger gas evacuation
    assert not any("EVACUACIÓN" in m for m in res["deterministic_mandates"])


def test_combined_gas_fatiga_triggers_both_mandates():
    """Verifies that combined gas + fatigue alert triggers both evacuation and fatigue relief (Audit da81d5f P1)."""
    alert = {
        "alert_level": "CRITICO",
        "hazard": "combinado_gas_fatiga",
        "message": "CO de 99 ppm y fatiga 0.72 en operador de ScoopTram",
        "worker_id": 8,
        "machine_id": 1,
    }
    res = DeterministicSafetyInterlock.evaluate_rules(alert)
    assert res["safety_lockout_active"] is True
    assert any("EVACUACIÓN" in m for m in res["deterministic_mandates"])
    assert any("RELEVO OBLIGATORIO" in m for m in res["deterministic_mandates"])
    assert any("252" in r for r in res["normative_references"])
    assert any("138" in r for r in res["normative_references"])
