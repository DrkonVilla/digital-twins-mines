import os
import joblib
import numpy as np
import pandas as pd
from typing import Optional

from langflow.custom import Component
from langflow.io import FloatInput, IntInput, StrInput, Output
from langflow.schema import Data, Message


class MiningRiskPredictorComponent(Component):
    display_name = "Predictor de Riesgo Minero (XGBoost/Voting)"
    description = "Ejecuta inferencia sobre el modelo predictivo de seguridad minera M-11 y emite el diagnóstico de riesgo."
    icon = "hard-hat"
    name = "MiningRiskPredictor"

    inputs = [
        StrInput(
            name="model_path",
            display_name="Ruta del Modelo .joblib",
            info="Ruta al archivo best_risk_model.joblib o model_xgb_v1.joblib",
            value=r"c:\Users\villa\Downloads\Mining\digital-twins-mines\backend\app\ml\artifacts\best_risk_model.joblib",
        ),
        FloatInput(
            name="distance_3d",
            display_name="Distancia 3D (metros)",
            info="Distancia física entre el operario y la maquinaria pesada",
            value=3.2,
        ),
        FloatInput(
            name="ttc",
            display_name="Time to Collision (TTC seg)",
            info="Tiempo estimado para colisión a la velocidad actual",
            value=1.8,
        ),
        FloatInput(
            name="worker_speed",
            display_name="Velocidad del Operario (m/s)",
            info="Velocidad de desplazamiento del trabajador",
            value=1.1,
        ),
        FloatInput(
            name="machine_speed",
            display_name="Velocidad de Maquinaria (m/s)",
            info="Velocidad de desplazamiento de la máquina (Scooptram/Dumper)",
            value=3.8,
        ),
        IntInput(
            name="in_restricted_zone",
            display_name="En Zona Restringida (0 o 1)",
            info="1 si el trabajador ingresó a un área no autorizada, 0 si no",
            value=1,
        ),
        FloatInput(
            name="gas_co_ppm",
            display_name="Gas CO (ppm)",
            info="Concentración de Monóxido de Carbono en el socavón",
            value=38.5,
        ),
        FloatInput(
            name="fatigue_index",
            display_name="Índice de Fatiga (0.0 a 1.0)",
            info="Estimación de fatiga según biométricos / horas de guardia",
            value=0.68,
        ),
        FloatInput(
            name="worker_bpm",
            display_name="Frecuencia Cardíaca (BPM)",
            info="Pulsaciones por minuto del trabajador",
            value=115.0,
        ),
        FloatInput(
            name="dust_density_mg_m3",
            display_name="Polvo en Suspensión (mg/m3)",
            info="Densidad de partículas en el aire",
            value=4.2,
        ),
    ]

    outputs = [
        Output(
            display_name="Diagnóstico Formateado (Texto)",
            name="diagnostic_message",
            method="generate_diagnostic_text",
        ),
        Output(
            display_name="Datos Estructurados (Data)",
            name="prediction_data",
            method="predict_risk",
        ),
    ]

    def _patch_pipeline(self, est):
        """Parche para compatibilidad entre versiones de scikit-learn."""
        if hasattr(est, "steps"):
            for _, step in est.steps:
                self._patch_pipeline(step)
        elif hasattr(est, "transformers_"):
            for _, transformer, _ in est.transformers_:
                self._patch_pipeline(transformer)
        elif hasattr(est, "transformers"):
            for _, transformer, _ in est.transformers:
                self._patch_pipeline(transformer)
        if type(est).__name__ == "SimpleImputer" and not hasattr(est, "_fill_dtype"):
            est._fill_dtype = getattr(est, "_fit_dtype", float)

    def _load_model(self):
        target = getattr(self, "model_path", "")
        candidates = [
            target,
            r"c:\Users\villa\Downloads\Mining\digital-twins-mines\backend\app\ml\artifacts\best_risk_model.joblib",
            os.path.join(os.getcwd(), target) if target else "",
            os.path.join(os.getcwd(), "digital-twins-mines", "backend", "app", "ml", "artifacts", "best_risk_model.joblib"),
            os.path.join(os.getcwd(), "backend", "app", "ml", "artifacts", "best_risk_model.joblib"),
        ]

        resolved = None
        for c in candidates:
            if c and os.path.exists(c):
                resolved = c
                break

        if not resolved:
            raise FileNotFoundError(f"No se encontró el artefacto del modelo en ninguna de las rutas: {candidates}")

        artifact = joblib.load(resolved)
        if isinstance(artifact, dict):
            model = artifact.get("model")
            scaler = artifact.get("scaler")
        else:
            model = artifact
            scaler = None

        self._patch_pipeline(model)
        return model, scaler

    def predict_risk(self) -> Data:
        """Ejecuta inferencia sobre el modelo predictivo entrenado."""
        model, scaler = self._load_model()
        class_names = ["BAJO", "MEDIO", "ALTO"]

        relative_speed = abs(float(self.machine_speed) - float(self.worker_speed))
        features_dict = {
            "distance_3d": float(self.distance_3d),
            "ttc": float(self.ttc),
            "relative_speed": float(relative_speed),
            "worker_speed": float(self.worker_speed),
            "machine_speed": float(self.machine_speed),
            "in_restricted_zone": int(self.in_restricted_zone),
            "worker_bpm": float(self.worker_bpm),
            "fatigue_index": float(self.fatigue_index),
            "vibration_rms": 0.8,
            "gas_co_ppm": float(self.gas_co_ppm),
            "dust_density_mg_m3": float(self.dust_density_mg_m3),
            "ambient_light_lux": 60.0,
            "acceleration_z": 9.81,
            "direction_worker": 0,
            "direction_machine": 0,
            "machine_status": 1
        }

        df = pd.DataFrame([features_dict])

        # Alinear columnas esperadas
        if scaler and hasattr(scaler, "feature_names_in_"):
            target_cols = list(scaler.feature_names_in_)
        elif hasattr(model, "feature_names_in_"):
            target_cols = list(model.feature_names_in_)
        else:
            target_cols = list(features_dict.keys())

        for c in target_cols:
            if c not in df.columns:
                df[c] = 0.0
        X = df[target_cols]

        pred_idx = int(model.predict(X)[0])
        risk_level = class_names[pred_idx] if 0 <= pred_idx < len(class_names) else "DESCONOCIDO"

        proba = None
        probabilities = {}
        if hasattr(model, "predict_proba"):
            probs = model.predict_proba(X)[0]
            proba = float(probs[pred_idx])
            probabilities = {class_names[i]: float(probs[i]) for i in range(len(class_names)) if i < len(probs)}

        # Factores detonantes
        factors = []
        if features_dict["distance_3d"] < 5.0:
            factors.append(f"Distancia 3D crítica ({features_dict['distance_3d']}m < 5.0m)")
        if features_dict["ttc"] < 3.0:
            factors.append(f"Tiempo al choque inminente ({features_dict['ttc']}s < 3.0s)")
        if features_dict["in_restricted_zone"] == 1:
            factors.append("Ingreso no autorizado a Zona Restringida de operación")
        if features_dict["gas_co_ppm"] > 35.0:
            factors.append(f"Concentración peligrosa de Monóxido de Carbono ({features_dict['gas_co_ppm']} ppm)")
        if features_dict["fatigue_index"] > 0.6:
            factors.append(f"Fatiga extrema del operario ({features_dict['fatigue_index']})")

        return Data(data={
            "risk_level": risk_level,
            "probability": proba,
            "probabilities": probabilities,
            "critical_factors": factors,
            "inputs": features_dict
        })

    def generate_diagnostic_text(self) -> Message:
        """Formatea un diagnóstico comprensible para inyectar como prompt en Langflow / Gemini."""
        pred = self.predict_risk()
        data = pred.data if hasattr(pred, "data") else pred

        risk = data.get("risk_level", "DESCONOCIDO")
        prob = data.get("probability", 0.0)
        factors = data.get("critical_factors", [])
        inputs = data.get("inputs", {})

        factors_txt = "\n".join([f"- ⚠️ {f}" for f in factors]) if factors else "- Operación dentro de parámetros tolerables."

        diagnostic = f"""
==================================================
🚨 REPORTE DE TELEMETRÍA Y PREDICCIÓN ML M-11
==================================================
- **Nivel de Riesgo Predicho:** {risk} (Probabilidad: {prob * 100:.1f}%)
- **Distancia al Equipo:** {inputs.get('distance_3d')} metros
- **Tiempo Estimado al Impacto (TTC):** {inputs.get('ttc')} segundos
- **Velocidad de Maquinaria:** {inputs.get('machine_speed')} m/s
- **Velocidad de Operario:** {inputs.get('worker_speed')} m/s
- **Zona Restringida:** {'SÍ (Alerta de Incursión)' if inputs.get('in_restricted_zone') == 1 else 'NO'}
- **Gas Monóxido de Carbono (CO):** {inputs.get('gas_co_ppm')} ppm
- **Fatiga del Operador:** {inputs.get('fatigue_index')} (BPM: {inputs.get('worker_bpm')})

**Factores Críticos Detectados:**
{factors_txt}

Por favor, como asistente de seguridad minera M-11 AI, genera las medidas de mitigación inmediatas y el protocolo de emergencia correspondiente.
""".strip()

        return Message(text=diagnostic)
