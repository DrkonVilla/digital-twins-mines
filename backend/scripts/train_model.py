import os
import joblib
import pandas as pd
import numpy as np
from pathlib import Path
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, accuracy_score, confusion_matrix
from imblearn.over_sampling import SMOTE
from imblearn.pipeline import Pipeline as ImbPipeline
import xgboost as xgb

DATA_PATH = os.path.join(os.path.dirname(__file__), "..", "..", "data", "raw", "synthetic_interactions.csv")
MODEL_PATH = os.path.join(os.path.dirname(__file__), "..", "app", "ml", "artifacts", "xgboost_collision_model.pkl")
PIPELINE_PATH = os.path.join(os.path.dirname(__file__), "..", "app", "ml", "artifacts", "preprocessing_pipeline.pkl")

def train_and_evaluate():
    data_path = Path(DATA_PATH)
    if not data_path.exists():
        print(f"Data file not found at {data_path}. Run generate_synthetic_data.py first.")
        return

    print("Loading data...")
    df = pd.read_csv(data_path)
    
    X = df.drop('risk_level', axis=1)
    y = df['risk_level']
    
    # Preprocessing
    numeric_features = [
        'worker_x', 'worker_y', 'worker_z', 
        'machine_x', 'machine_y', 'machine_z',
        'distance_3d', 'worker_speed', 'machine_speed',
        'relative_speed', 'ttc'
    ]
    categorical_features = ['direction_worker', 'direction_machine', 'in_restricted_zone', 'machine_status']
    
    numeric_transformer = Pipeline(steps=[
        ('imputer', SimpleImputer(strategy='median')),
        ('scaler', StandardScaler())
    ])
    
    categorical_transformer = Pipeline(steps=[
        ('imputer', SimpleImputer(strategy='most_frequent')),
        ('onehot', OneHotEncoder(handle_unknown='ignore'))
    ])
    
    preprocessor = ColumnTransformer(
        transformers=[
            ('num', numeric_transformer, numeric_features),
            ('cat', categorical_transformer, categorical_features)
        ])
    
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)
    
    print("Training XGBoost with SMOTE...")
    # Using XGBoost with SMOTE to handle imbalance and prioritize ALTO (class 2)
    model = ImbPipeline(steps=[
        ('preprocessor', preprocessor),
        ('smote', SMOTE(random_state=42)),
        ('classifier', xgb.XGBClassifier(
            objective='multi:softprob',
            eval_metric='mlogloss',
            use_label_encoder=False,
            n_estimators=100,
            max_depth=6,
            learning_rate=0.1,
            random_state=42
        ))
    ])
    
    model.fit(X_train, y_train)
    
    print("\nEvaluating model...")
    y_pred = model.predict(X_test)
    y_prob = model.predict_proba(X_test)
    
    # We want to optimize recall for class 2 (ALTO). 
    # Applying custom threshold for class 2.
    # By default argmax is used. We can lower threshold for class 2.
    threshold = 0.35 # Lower threshold to increase recall for ALTO
    
    y_pred_custom = []
    for probs in y_prob:
        if probs[2] >= threshold:
            y_pred_custom.append(2)
        elif probs[1] >= 0.5:
            y_pred_custom.append(1)
        else:
            y_pred_custom.append(np.argmax(probs))
            
    print("\n--- Standard XGBoost Metrics ---")
    print(classification_report(y_test, y_pred))
    
    print(f"\n--- Custom Threshold Metrics (ALTO threshold = {threshold}) ---")
    print(classification_report(y_test, y_pred_custom))
    
    print("\nConfusion Matrix (Custom):")
    print(confusion_matrix(y_test, y_pred_custom))
    
    # Save the model
    artifact_dir = Path("../app/ml/artifacts")
    artifact_dir.mkdir(parents=True, exist_ok=True)
    model_path = artifact_dir / "model_xgb_v1.joblib"
    
    # Get feature names after preprocessing
    # This requires fitting the preprocessor separately to extract feature names easily
    preprocessor.fit(X_train)
    cat_encoder = preprocessor.named_transformers_['cat'].named_steps['onehot']
    cat_features = cat_encoder.get_feature_names_out(categorical_features)
    feature_names = numeric_features + list(cat_features)
    
    artifact = {
        "model": model, # The full pipeline including preprocessing
        "feature_names": list(X.columns), # Original input features needed
        "version": "xgb_v1.0.0"
    }
    
    joblib.dump(artifact, model_path)
    print(f"\nModel saved to {model_path}")

if __name__ == "__main__":
    train_and_evaluate()
