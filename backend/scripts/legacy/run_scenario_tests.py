import sys
from pathlib import Path
import pandas as pd

# Add backend directory to sys.path
backend_dir = Path(__file__).resolve().parent.parent
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

if sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

from app.ml.model_loader import ml_engine
from app.ml.hmm_model import hmm_engine

scenarios = [
    {
        'name': '1. Operación Nominal Segura',
        'desc': 'Distancia 45m, TTC 15s, fatiga baja (0.10), gas normal (6 ppm)',
        'data': {'distance_3d': 45.0, 'ttc': 15.0, 'worker_speed': 0.8, 'machine_speed': 2.0, 'relative_speed': 2.8, 'in_restricted_zone': 0, 'fatigue_index': 0.10, 'worker_bpm': 72.0, 'gas_co_ppm': 6.0, 'ambient_light_lux': 85.0}
    },
    {
        'name': '2. Alerta Ambiental Gas CO',
        'desc': 'Distancia 35m, TTC 10s, gas elevado (55 ppm CO)',
        'data': {'distance_3d': 35.0, 'ttc': 10.0, 'worker_speed': 1.0, 'machine_speed': 2.5, 'relative_speed': 3.5, 'in_restricted_zone': 0, 'fatigue_index': 0.25, 'worker_bpm': 88.0, 'gas_co_ppm': 55.0, 'ambient_light_lux': 40.0}
    },
    {
        'name': '3. Colisión Inminente (Zona Restringida)',
        'desc': 'Distancia 4m, TTC 1.2s, Zona Restringida=1, BPM 115',
        'data': {'distance_3d': 4.0, 'ttc': 1.2, 'worker_speed': 1.2, 'machine_speed': 4.5, 'relative_speed': 5.7, 'in_restricted_zone': 1, 'fatigue_index': 0.35, 'worker_bpm': 115.0, 'gas_co_ppm': 12.0, 'ambient_light_lux': 25.0}
    },
    {
        'name': '4. Fatiga Severa del Operador',
        'desc': 'Distancia 18m, TTC 5.5s, Fatiga 0.88, BPM 145',
        'data': {'distance_3d': 18.0, 'ttc': 5.5, 'worker_speed': 0.5, 'machine_speed': 3.0, 'relative_speed': 3.5, 'in_restricted_zone': 0, 'fatigue_index': 0.88, 'worker_bpm': 145.0, 'gas_co_ppm': 15.0, 'ambient_light_lux': 30.0}
    },
    {
        'name': '5. Transición / Maniobra Intermedia',
        'desc': 'Distancia 22m, TTC 7.0s, Fatiga 0.40, BPM 98',
        'data': {'distance_3d': 22.0, 'ttc': 7.0, 'worker_speed': 1.1, 'machine_speed': 2.8, 'relative_speed': 3.9, 'in_restricted_zone': 0, 'fatigue_index': 0.40, 'worker_bpm': 98.0, 'gas_co_ppm': 14.0, 'ambient_light_lux': 50.0}
    }
]

def run_tests():
    print("=" * 115)
    print("🧪 BATERÍA DE PRUEBAS COMPLETA DE INFERENCIA DE IA Y ESTADOS HMM (FICHA 11)")
    print("=" * 115)
    print(f"{'Escenario Evaluado':<38} | {'Clasificación':<14} | {'P(BAJO)':<9} | {'P(MEDIO)':<9} | {'P(ALTO)':<9} | {'Estado HMM K=4':<24}")
    print("-" * 115)

    for sc in scenarios:
        res = ml_engine.predict(sc['data'])
        hmm_res = hmm_engine.estimate_hidden_state(sc['data'])
        p = res['probabilities']
        level_tag = f"🔴 {res['risk_level']}" if res['risk_level'] == 'ALTO' else (f"🟡 {res['risk_level']}" if res['risk_level'] == 'MEDIO' else f"🟢 {res['risk_level']}")
        print(f"{sc['name']:<38} | {level_tag:<14} | {p['BAJO']*100:>7.1f}% | {p['MEDIO']*100:>7.1f}% | {p['ALTO']*100:>7.1f}% | {hmm_res['hidden_state_name']:<24}")

    print("=" * 115)

if __name__ == "__main__":
    run_tests()
