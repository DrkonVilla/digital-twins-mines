import os
import sys
import json
import joblib
import pandas as pd
import numpy as np
from pathlib import Path

# Force UTF-8 stdout
if sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

def p(text):
    print(text, flush=True)

from sklearn.model_selection import StratifiedKFold, GridSearchCV, cross_validate
from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.compose import ColumnTransformer

# Modelos Naturales
from sklearn.ensemble import RandomForestClassifier
from sklearn.neural_network import MLPClassifier
import xgboost as xgb

# Modelos Híbridos (Ensembles)
from sklearn.ensemble import StackingClassifier, VotingClassifier
from sklearn.linear_model import LogisticRegression

# Evaluación
from sklearn.metrics import classification_report, accuracy_score, recall_score, f1_score, precision_score, roc_auc_score
from imblearn.over_sampling import SMOTE
from imblearn.pipeline import Pipeline as ImbPipeline

def run_pipeline():
    p("================================================================================")
    p("PIPELINE DE INTELIGENCIA ARTIFICIAL - INVESTIGACION TESIS GEMELO DIGITAL M-11")
    p("================================================================================")

    # 1. Cargar Dataset Real Enriquecido
    data_path = Path("data/raw/public_mining_equipment_dataset.csv")
    if not data_path.exists():
        p(f"[ERROR] Dataset no encontrado en {data_path}. Ejecuta download_and_process_public_dataset.py primero.")
        return

    p(f"\n[1/6] Cargando Dataset Real procesado desde {data_path}...")
    df = pd.read_csv(data_path)
    p(f"   Filas: {len(df)} | Columnas: {len(df.columns)}")
    p(f"   Distribucion de Clases (0=BAJO, 1=MEDIO, 2=ALTO):\n{df['risk_level'].value_counts(normalize=True).to_string()}")

    # 2. Definición de Features y Target
    target_col = 'risk_level'
    X = df.drop(columns=[target_col, 'record_id', 'machine_serial'], errors='ignore')
    y = df[target_col]

    numeric_features = [
        'worker_x', 'worker_y', 'worker_z',
        'machine_x', 'machine_y', 'machine_z',
        'distance_3d', 'worker_speed', 'machine_speed',
        'relative_speed', 'ttc',
        'worker_bpm', 'fatigue_index',
        'vibration_rms', 'acceleration_z',
        'gas_co_ppm', 'dust_density_mg_m3', 'ambient_light_lux',
        'ambient_temp_k', 'engine_temp_k', 'rpm_speed', 'torque_nm', 'operating_hours_wear'
    ]
    categorical_features = ['machine_type_class', 'direction_worker', 'direction_machine', 'in_restricted_zone', 'machine_status', 'failure_flag']

    numeric_features = [col for col in numeric_features if col in X.columns]
    categorical_features = [col for col in categorical_features if col in X.columns]

    numeric_transformer = Pipeline(steps=[
        ('imputer', SimpleImputer(strategy='median')),
        ('scaler', StandardScaler())
    ])

    categorical_transformer = Pipeline(steps=[
        ('imputer', SimpleImputer(strategy='most_frequent')),
        ('onehot', OneHotEncoder(handle_unknown='ignore', sparse_output=False))
    ])

    preprocessor = ColumnTransformer(
        transformers=[
            ('num', numeric_transformer, numeric_features),
            ('cat', categorical_transformer, categorical_features)
        ]
    )

    # 3. Configuración de Validación Cruzada (Stratified K-Fold con K=5)
    p("\n[2/6] Configurando Validacion Cruzada Estratificada (StratifiedKFold, K=5)...")
    cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)

    # 4. Ajuste de Hiperparámetros (GridSearchCV) para Modelos Base Naturales
    p("\n[3/6] Ajustando Hiperparametros (GridSearchCV) para Modelos Naturales...")

    # A) Random Forest
    rf_base = RandomForestClassifier(random_state=42, n_jobs=-1)
    rf_pipe = ImbPipeline([('prep', preprocessor), ('smote', SMOTE(random_state=42)), ('clf', rf_base)])
    rf_param_grid = {
        'clf__n_estimators': [50, 100],
        'clf__max_depth': [12, 20]
    }
    rf_grid = GridSearchCV(rf_pipe, rf_param_grid, cv=cv, scoring='f1_macro', n_jobs=-1)
    rf_grid.fit(X, y)
    best_rf = rf_grid.best_estimator_
    p(f"   [OK] Mejor Random Forest F1-Macro: {rf_grid.best_score_:.4f} | Params: {rf_grid.best_params_}")

    # B) XGBoost
    xgb_base = xgb.XGBClassifier(objective='multi:softprob', eval_metric='mlogloss', random_state=42, n_jobs=-1)
    xgb_pipe = ImbPipeline([('prep', preprocessor), ('smote', SMOTE(random_state=42)), ('clf', xgb_base)])
    xgb_param_grid = {
        'clf__n_estimators': [50, 100],
        'clf__max_depth': [4, 6],
        'clf__learning_rate': [0.1]
    }
    xgb_grid = GridSearchCV(xgb_pipe, xgb_param_grid, cv=cv, scoring='f1_macro', n_jobs=-1)
    xgb_grid.fit(X, y)
    best_xgb = xgb_grid.best_estimator_
    p(f"   [OK] Mejor XGBoost F1-Macro: {xgb_grid.best_score_:.4f} | Params: {xgb_grid.best_params_}")

    # C) MLP (Neural Network)
    mlp_base = MLPClassifier(hidden_layer_sizes=(64, 32), max_iter=150, random_state=42)
    mlp_pipe = ImbPipeline([('prep', preprocessor), ('smote', SMOTE(random_state=42)), ('clf', mlp_base)])
    mlp_param_grid = {
        'clf__alpha': [0.0001, 0.001]
    }
    mlp_grid = GridSearchCV(mlp_pipe, mlp_param_grid, cv=cv, scoring='f1_macro', n_jobs=-1)
    mlp_grid.fit(X, y)
    best_mlp = mlp_grid.best_estimator_
    p(f"   [OK] Mejor MLP Neural Net F1-Macro: {mlp_grid.best_score_:.4f} | Params: {mlp_grid.best_params_}")

    # 5. Construcción de Modelos Híbridos (Ensembles)
    p("\n[4/6] Construyendo Modelos Hibridos (Stacking y Voting Ensembles)...")
    base_estimators = [
        ('rf', RandomForestClassifier(n_estimators=50, max_depth=12, random_state=42)),
        ('xgb', xgb.XGBClassifier(n_estimators=50, max_depth=4, learning_rate=0.1, random_state=42)),
        ('mlp', MLPClassifier(hidden_layer_sizes=(64, 32), max_iter=100, random_state=42))
    ]

    # Stacking Ensemble
    stacking_clf = StackingClassifier(
        estimators=base_estimators,
        final_estimator=LogisticRegression(max_iter=300, random_state=42),
        cv=3,
        n_jobs=-1
    )
    stacking_pipe = ImbPipeline([('prep', preprocessor), ('smote', SMOTE(random_state=42)), ('clf', stacking_clf)])

    # Voting Ensemble (Soft Voting)
    voting_clf = VotingClassifier(
        estimators=base_estimators,
        voting='soft',
        weights=[1, 2, 1],
        n_jobs=-1
    )
    voting_pipe = ImbPipeline([('prep', preprocessor), ('smote', SMOTE(random_state=42)), ('clf', voting_clf)])

    # 6. Evaluación Rigurosa por Validación Cruzada de los 5 Modelos
    p("\n[5/6] Ejecutando Validacion Cruzada Estratificada en los 5 Modelos...")
    models_dict = {
        "RandomForest": best_rf,
        "XGBoost": best_xgb,
        "MLP_NeuralNet": best_mlp,
        "Stacking_Ensemble": stacking_pipe,
        "Voting_Ensemble": voting_pipe
    }

    results = {}
    scoring_metrics = ['accuracy', 'precision_macro', 'recall_macro', 'f1_macro', 'roc_auc_ovr']

    for name, model_pipeline in models_dict.items():
        p(f"   Evaluando {name}...")
        cv_res = cross_validate(model_pipeline, X, y, cv=cv, scoring=scoring_metrics, return_train_score=False, n_jobs=-1)
        
        results[name] = {
            "accuracy_folds": [float(x) for x in cv_res['test_accuracy']],
            "precision_folds": [float(x) for x in cv_res['test_precision_macro']],
            "recall_folds": [float(x) for x in cv_res['test_recall_macro']],
            "f1_folds": [float(x) for x in cv_res['test_f1_macro']],
            "roc_auc_folds": [float(x) for x in cv_res['test_roc_auc_ovr']],
            "mean_accuracy": float(np.mean(cv_res['test_accuracy'])),
            "mean_precision": float(np.mean(cv_res['test_precision_macro'])),
            "mean_recall": float(np.mean(cv_res['test_recall_macro'])),
            "mean_f1": float(np.mean(cv_res['test_f1_macro'])),
            "mean_roc_auc": float(np.mean(cv_res['test_roc_auc_ovr']))
        }

        p(f"     Accuracy : {results[name]['mean_accuracy']:.4f} +/- {np.std(cv_res['test_accuracy']):.4f}")
        p(f"     F1-Score : {results[name]['mean_f1']:.4f} +/- {np.std(cv_res['test_f1_macro']):.4f}")
        p(f"     ROC-AUC  : {results[name]['mean_roc_auc']:.4f} +/- {np.std(cv_res['test_roc_auc_ovr']):.4f}")

    # 7. Selección del Mejor Modelo y Guardado de Artefactos
    p("\n[6/6] Guardando Artefactos y Resultados para Validacion Estadistica...")
    best_model_name = max(results, key=lambda k: results[k]['mean_f1'])
    p(f"\n[GANADOR] GANADOR ABSOLUTO DEL BENCHMARK: {best_model_name} (F1-Score: {results[best_model_name]['mean_f1']:.4f})")

    winning_pipeline = models_dict[best_model_name]
    winning_pipeline.fit(X, y)

    artifact_dir = Path("backend/app/ml/artifacts")
    artifact_dir.mkdir(parents=True, exist_ok=True)

    metrics_json_path = artifact_dir / "model_comparison_results.json"
    with open(metrics_json_path, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2)
    p(f"   [OK] Resultados de CV exportados a: {metrics_json_path}")

    artifact = {
        "model": winning_pipeline,
        "feature_names": list(X.columns),
        "model_name": best_model_name,
        "version": "v2.0.0_ensemble",
        "metrics": results[best_model_name]
    }

    best_model_path = artifact_dir / "best_mining_risk_model.joblib"
    xgb_v1_path = artifact_dir / "model_xgb_v1.joblib"

    joblib.dump(artifact, best_model_path)
    joblib.dump(artifact, xgb_v1_path)
    p(f"   [OK] Modelo ganador guardado en: {best_model_path}")
    p(f"   [OK] Alias de produccion actualizado en: {xgb_v1_path}")

    p("\n================================================================================")
    p("PIPELINE COMPLETO FINALIZADO CON EXITO")
    p("================================================================================")

if __name__ == "__main__":
    run_pipeline()
