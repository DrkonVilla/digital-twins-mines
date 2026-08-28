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
    
    def predict(self, features: Dict[str, Any]) -> Dict[str, Any]:
        if not self.pipeline:
            raise ValueError("Model not loaded.")
        
        # Convert to DataFrame for the pipeline
        df = pd.DataFrame([features])
        
        # In a real scenario, we map the model's output classes to our risk levels
        # Assuming the pipeline returns [0, 1, 2] corresponding to BAJO, MEDIO, ALTO
        # and we use predict_proba for risk score.
        prediction = self.pipeline.predict(df)[0]
        probas = self.pipeline.predict_proba(df)[0]
        
        risk_map = {0: "BAJO", 1: "MEDIO", 2: "ALTO"}
        
        # Assuming class 2 is ALTO
        risk_score = float(probas[2]) * 100 
        
        # Evaluate threshold. In Etapa 1 we found 0.35 recall optimized for ALTO
        if probas[2] >= 0.35:
            prediction_label = "ALTO"
        else:
            prediction_label = risk_map.get(prediction, "BAJO")
            
        return {
            "risk_level": prediction_label,
            "risk_score": round(risk_score, 2)
        }
    
    def predict_batch(self, features_list: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        if not self.pipeline:
            raise ValueError("Model not loaded.")
        
        df = pd.DataFrame(features_list)
        predictions = self.pipeline.predict(df)
        probas = self.pipeline.predict_proba(df)
        
        risk_map = {0: "BAJO", 1: "MEDIO", 2: "ALTO"}
        results = []
        
        for i, (pred, proba) in enumerate(zip(predictions, probas)):
            risk_score = float(proba[2]) * 100
            if proba[2] >= 0.35:
                prediction_label = "ALTO"
            else:
                prediction_label = risk_map.get(pred, "BAJO")
                
            results.append({
                "risk_level": prediction_label,
                "risk_score": round(risk_score, 2)
            })
            
        return results

ml_engine = MLLoader()
