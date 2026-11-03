import sys
import os
import joblib
import pandas as pd
from pathlib import Path

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

# Simulación de la función predict de Streamlit (Página 4)
MODEL_PATH = backend_dir / "app" / "ml" / "artifacts" / "best_risk_model.joblib"
streamlit_artifact = joblib.load(MODEL_PATH)

def streamlit_predict(features_dict):
    model_obj = streamlit_artifact.get("model")
    scaler_obj = streamlit_artifact.get("scaler")
    required_cols = list(scaler_obj.feature_names_in_)
    
    defaults = {
        'distance_3d': 15.0, 'ttc': 10.0, 'relative_speed': 3.5,
        'worker_speed': 1.2, 'machine_speed': 2.3, 'in_restricted_zone': 0,
        'worker_bpm': 75.0, 'fatigue_index': 0.2, 'vibration_rms': 0.8,
        'gas_co_ppm': 10.0, 'dust_density_mg_m3': 1.0, 'ambient_light_lux': 60.0,
        'acceleration_z': 9.81, 'direction_worker': 0, 'direction_machine': 0, 'machine_status': 1
    }
    
    input_data = dict(features_dict)
    for col in required_cols:
        if col not in input_data:
            input_data[col] = defaults.get(col, 0.0)
            
    df_eval = pd.DataFrame([input_data])[required_cols]
    X_eval = scaler_obj.transform(df_eval)
    pred_idx = int(model_obj.predict(X_eval)[0])
    probas = model_obj.predict_proba(X_eval)[0]
    
    class_labels = ["BAJO", "MEDIO", "ALTO"]
    return {
        "risk_level": class_labels[min(pred_idx, 2)],
        "risk_score": round(float(probas[pred_idx]) * 100, 2),
        "probabilities": {name: round(float(p), 4) for name, p in zip(class_labels, probas)}
    }

test_scenarios = [
    {
        'id': 'E1',
        'name': 'Operación Nominal Segura',
        'data': {'distance_3d': 45.0, 'ttc': 15.0, 'worker_speed': 0.8, 'machine_speed': 2.0, 'relative_speed': 2.8, 'in_restricted_zone': 0, 'fatigue_index': 0.10, 'worker_bpm': 72.0, 'gas_co_ppm': 6.0, 'ambient_light_lux': 85.0}
    },
    {
        'id': 'E2',
        'name': 'Alerta Ambiental Gas CO',
        'data': {'distance_3d': 35.0, 'ttc': 10.0, 'worker_speed': 1.0, 'machine_speed': 2.5, 'relative_speed': 3.5, 'in_restricted_zone': 0, 'fatigue_index': 0.25, 'worker_bpm': 88.0, 'gas_co_ppm': 55.0, 'ambient_light_lux': 40.0}
    },
    {
        'id': 'E3',
        'name': 'Colisión Inminente (Zona Restringida)',
        'data': {'distance_3d': 4.0, 'ttc': 1.2, 'worker_speed': 1.2, 'machine_speed': 4.5, 'relative_speed': 5.7, 'in_restricted_zone': 1, 'fatigue_index': 0.35, 'worker_bpm': 115.0, 'gas_co_ppm': 12.0, 'ambient_light_lux': 25.0}
    },
    {
        'id': 'E4',
        'name': 'Fatiga Severa del Operador',
        'data': {'distance_3d': 18.0, 'ttc': 5.5, 'worker_speed': 0.5, 'machine_speed': 3.0, 'relative_speed': 3.5, 'in_restricted_zone': 0, 'fatigue_index': 0.88, 'worker_bpm': 145.0, 'gas_co_ppm': 15.0, 'ambient_light_lux': 30.0}
    },
    {
        'id': 'E5',
        'name': 'Transición / Maniobra Intermedia',
        'data': {'distance_3d': 22.0, 'ttc': 7.0, 'worker_speed': 1.1, 'machine_speed': 2.8, 'relative_speed': 3.9, 'in_restricted_zone': 0, 'fatigue_index': 0.40, 'worker_bpm': 98.0, 'gas_co_ppm': 14.0, 'ambient_light_lux': 50.0}
    }
]

def verify_parity():
    print("=" * 115)
    print("🔍 VERIFICACIÓN DE PARIDAD CRUZADA DE INFERENCIA: STREAMLIT VS NEXT.JS (API / WS)")
    print("=" * 115)
    print(f"{'Escenario Evaluado':<36} | {'Streamlit Predicción':<22} | {'Next.js / Backend API':<22} | {'Paridad':<10}")
    print("-" * 115)

    all_equal = True
    for sc in test_scenarios:
        res_st = streamlit_predict(sc['data'])
        res_next = ml_engine.predict(sc['data'])
        
        st_str = f"{res_st['risk_level']} ({res_st['risk_score']}%)"
        next_str = f"{res_next['risk_level']} ({res_next['risk_score']}%)"
        
        is_equal = (res_st['risk_level'] == res_next['risk_level']) and (abs(res_st['risk_score'] - res_next['risk_score']) < 0.01)
        if not is_equal:
            all_equal = False
            
        tag = "✅ MATCH" if is_equal else "❌ MISMATCH"
        print(f"{sc['name']:<36} | {st_str:<22} | {next_str:<22} | {tag:<10}")

    print("=" * 115)
    if all_equal:
        print("🎉 CONCLUSIÓN: PARIDAD MATEMÁTICA Y CIENTÍFICA DEL 100% CONFIRMADA ENTRE AMBAS PLATAFORMAS.")
    else:
        print("⚠️ ALERTA: SE DETECTARON DISCREPANCIAS ENTRE PLATAFORMAS.")
    print("=" * 115)

if __name__ == "__main__":
    verify_parity()
