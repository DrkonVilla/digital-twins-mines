import os
import joblib
import pandas as pd
from typing import Dict, Any, List

class MLLoader:
    def __init__(self):
        self.model_path = os.path.join(os.path.dirname(__file__), "artifacts", "model_xgb_v1.joblib")
        self.pipeline = None
        self._load_model()
    
    def _load_model(self):
        if os.path.exists(self.model_path):
            artifact = joblib.load(self.model_path)
            self.pipeline = artifact.get("model")
            self.feature_names = artifact.get("feature_names")
            print(f"Loaded ML model from {self.model_path}")
        else:
            print(f"Warning: ML model not found at {self.model_path}")
    
    def _prepare_df(self, df: pd.DataFrame) -> pd.DataFrame:
        """Ensure all required feature_names exist in DataFrame with reasonable defaults."""
        if hasattr(self, 'feature_names') and self.feature_names:
            defaults = {
                'worker_bpm': 85.0, 'fatigue_index': 0.2, 'vibration_rms': 1.5,
                'acceleration_z': 9.81, 'gas_co_ppm': 10.0, 'dust_density_mg_m3': 1.5,
                'ambient_light_lux': 45.0, 'machine_type_class': 'H', 'ambient_temp_k': 298.15,
                'engine_temp_k': 310.0, 'rpm_speed': 1800.0, 'torque_nm': 400.0,
                'operating_hours_wear': 500.0, 'failure_flag': 0
            }
            for col in self.feature_names:
                if col not in df.columns:
                    df[col] = defaults.get(col, 0)
        return df

    def predict(self, features: Dict[str, Any]) -> Dict[str, Any]:
        if not self.pipeline:
            self._load_model()
            if not self.pipeline:
                raise ValueError("Model not loaded.")
        
        df = pd.DataFrame([features])
        df = self._prepare_df(df)
        
        prediction = self.pipeline.predict(df)[0]
        probas = self.pipeline.predict_proba(df)[0]
        
        risk_score = float(probas[2]) * 100 
        
        if risk_score >= 80.0:
            prediction_label = "ALTO"
        elif risk_score >= 50.0:
            prediction_label = "MEDIO"
        else:
            prediction_label = "BAJO"
            
        return {
            "risk_level": prediction_label,
            "risk_score": round(risk_score, 2)
        }
    
    def predict_batch(self, features_list: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        if not self.pipeline:
            self._load_model()
            if not self.pipeline:
                raise ValueError("Model not loaded.")
        
        df = pd.DataFrame(features_list)
        df = self._prepare_df(df)
        
        predictions = self.pipeline.predict(df)
        probas = self.pipeline.predict_proba(df)
        
        results = []
        
        for i, (pred, proba) in enumerate(zip(predictions, probas)):
            risk_score = float(proba[2]) * 100
            if risk_score >= 80.0:
                prediction_label = "ALTO"
            elif risk_score >= 50.0:
                prediction_label = "MEDIO"
            else:
                prediction_label = "BAJO"
                
            results.append({
                "risk_level": prediction_label,
                "risk_score": round(risk_score, 2)
            })
            
        return results


ml_engine = MLLoader()
