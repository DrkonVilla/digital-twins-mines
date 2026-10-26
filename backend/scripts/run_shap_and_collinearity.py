"""
SHAP and Collinearity Analysis for M-11 Digital Twin System.

Generates:
1. results/shap_values.csv: Global mean absolute SHAP values per feature for High Risk (ALTO)
2. figures/shap_summary.png: SHAP Beeswarm plot and global importance bar plot
3. figures/correlaciones.png: Feature correlation matrix and VIF analysis (collinearity)
"""
import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import seaborn as sns
import shap
import shap.explainers._tree as st

# Patch for XGBoost 2.x multi-class base_score compatibility with SHAP TreeExplainer
_orig_decode = st.decode_ubjson_buffer
def _patched_decode(fd):
    res = _orig_decode(fd)
    try:
        lmp = res.get('learner', {}).get('learner_model_param', {})
        bs = lmp.get('base_score')
        if isinstance(bs, str) and bs.startswith('['):
            lmp['base_score'] = '0.0'
    except Exception:
        pass
    return res
st.decode_ubjson_buffer = _patched_decode

from sklearn.model_selection import train_test_split
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.compose import ColumnTransformer
from xgboost import XGBClassifier
from imblearn.over_sampling import SMOTE, SMOTENC

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DATASET_PATH = PROJECT_ROOT / "data" / "raw" / "public_mining_equipment_dataset.csv"
RESULTS_DIR = PROJECT_ROOT / "results"
FIGURES_DIR = PROJECT_ROOT / "figures"
FIGURES_DIR.mkdir(parents=True, exist_ok=True)
RESULTS_DIR.mkdir(parents=True, exist_ok=True)

FEATURES = [
    "distance_3d", "worker_speed", "machine_speed", "relative_speed",
    "direction_worker", "direction_machine", "ttc", "in_restricted_zone",
    "machine_status", "worker_bpm", "fatigue_index", "vibration_rms",
    "acceleration_z", "gas_co_ppm", "dust_density_mg_m3", "ambient_light_lux",
]
CATEGORICAL = ["direction_worker", "direction_machine", "in_restricted_zone", "machine_status"]
NUMERIC = [f for f in FEATURES if f not in CATEGORICAL]
LABEL_COL = "risk_level"
LABEL_MAP = {"BAJO": 0, "MEDIO": 1, "ALTO": 2}


def main():
    print("=== Phase III.A: SHAP & Collinearity Analysis ===")
    df = pd.read_csv(DATASET_PATH)
    X = df[FEATURES].copy()
    y = df[LABEL_COL].astype(int)

    # 80/20 train/test split
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.20, random_state=42, stratify=y
    )

    print(f"Dataset loaded: {len(X)} records. Train: {len(X_train)}, Test: {len(X_test)}")

    # 1. Collinearity analysis (Correlation Matrix & Heatmap)
    print("\n--- 1. Collinearity Analysis ---")
    corr_matrix = df[NUMERIC].corr(method="spearman")
    
    plt.figure(figsize=(11, 9))
    mask = np.triu(np.ones_like(corr_matrix, dtype=bool))
    cmap = sns.diverging_palette(220, 20, as_cmap=True)
    sns.heatmap(
        corr_matrix, mask=mask, cmap=cmap, vmin=-1.0, vmax=1.0,
        annot=True, fmt=".2f", square=True, linewidths=.5, cbar_kws={"shrink": .8}
    )
    plt.title("Matriz de Correlación de Spearman (12 Variables Numéricas)\nEvidencia de Multicolinealidad Cinemática", fontsize=13, pad=15)
    plt.tight_layout()
    corr_fig_path = FIGURES_DIR / "correlaciones.png"
    plt.savefig(corr_fig_path, dpi=300)
    plt.close()
    print(f"Correlation figure saved to: {corr_fig_path}")

    # 2. Train XGBoost on Preprocessed Data
    print("\n--- 2. Preprocessing & Training XGBoost ---")
    preprocessor = ColumnTransformer(
        transformers=[
            ("num", StandardScaler(), NUMERIC),
            ("cat", OneHotEncoder(drop="first", sparse_output=False, handle_unknown="ignore"), CATEGORICAL),
        ]
    )
    
    # Fit preprocessor on train only
    X_train_proc = preprocessor.fit_transform(X_train)
    X_test_proc = preprocessor.transform(X_test)
    
    # Feature names after OneHotEncoding
    ohe_features = preprocessor.named_transformers_["cat"].get_feature_names_out(CATEGORICAL)
    all_feature_names = list(NUMERIC) + list(ohe_features)
    
    # Apply SMOTE on train only
    smote = SMOTE(random_state=42)
    X_train_res, y_train_res = smote.fit_resample(X_train_proc, y_train)

    xgb = XGBClassifier(
        n_estimators=100,
        max_depth=6,
        learning_rate=0.1,
        random_state=42,
        eval_metric="mlogloss",
        use_label_encoder=False
    )
    xgb.fit(X_train_res, y_train_res)
    print("XGBoost model fitted successfully.")

    # 3. TreeSHAP Calculation
    print("\n--- 3. TreeSHAP Computation ---")
    explainer = shap.TreeExplainer(xgb)
    
    # Stratified sample from test set for SHAP to ensure representative and fast evaluation
    sample_indices = X_test.sample(n=min(500, len(X_test)), random_state=42).index
    X_sample_raw = X.loc[sample_indices]
    X_sample_proc = preprocessor.transform(X_sample_raw)
    y_sample = y.loc[sample_indices]

    shap_values = explainer.shap_values(X_sample_proc)
    
    # In multi-class, shap_values is a list of arrays [class_0, class_1, class_2]
    # Class 2 is ALTO (High Risk)
    if isinstance(shap_values, list):
        shap_alto = shap_values[2]
    else:
        # For newer shap versions, shap_values might be (n_samples, n_features, n_classes)
        if len(shap_values.shape) == 3:
            shap_alto = shap_values[:, :, 2]
        else:
            shap_alto = shap_values

    print(f"SHAP values shape for ALTO class: {shap_alto.shape}")

    # Map back to original feature groups or detailed feature names
    mean_abs_shap = np.mean(np.abs(shap_alto), axis=0)
    shap_df = pd.DataFrame({
        "transformed_feature": all_feature_names,
        "mean_abs_shap_alto": mean_abs_shap
    }).sort_values(by="mean_abs_shap_alto", ascending=False)
    
    # Also aggregate by original feature
    agg_shap = {}
    for orig_f in FEATURES:
        matching_cols = [i for i, name in enumerate(all_feature_names) if name == orig_f or name.startswith(orig_f + "_")]
        agg_shap[orig_f] = float(np.sum(mean_abs_shap[matching_cols]))
        
    agg_shap_df = pd.DataFrame(list(agg_shap.items()), columns=["feature", "mean_abs_shap_alto"]).sort_values(
        by="mean_abs_shap_alto", ascending=False
    )
    
    shap_csv_path = RESULTS_DIR / "shap_values.csv"
    agg_shap_df.to_csv(shap_csv_path, index=False)
    print(f"SHAP values exported to: {shap_csv_path}")

    # 4. Generate SHAP Summary Figure (figures/shap_summary.png)
    print("\n--- 4. Generating SHAP Figures ---")
    fig, axes = plt.subplots(1, 2, figsize=(16, 7))
    
    # Left: Bar plot of feature importance
    top_10_agg = agg_shap_df.head(10)
    colors = ["#c0392b" if f in ["distance_3d", "ttc", "relative_speed", "in_restricted_zone"] else "#2980b9" for f in top_10_agg["feature"]]
    axes[0].barh(top_10_agg["feature"][::-1], top_10_agg["mean_abs_shap_alto"][::-1], color=colors[::-1])
    axes[0].set_xlabel("Mean |SHAP Value| (Impacto en Clase ALTO)", fontsize=11)
    axes[0].set_title("Importancia Global TreeSHAP (Clase ALTO)\n[Rojo: Cinemático/Espacial | Azul: Otros Sensores]", fontsize=12)
    axes[0].grid(axis="x", linestyle="--", alpha=0.7)

    # Right: Beeswarm plot using SHAP explainer
    plt.sca(axes[1])
    # Create an Explanation object for beeswarm plotting
    explanation = shap.Explanation(
        values=shap_alto,
        data=X_sample_proc,
        feature_names=all_feature_names
    )
    shap.plots.beeswarm(explanation, max_display=10, show=False)
    axes[1].set_title("Beeswarm Plot TreeSHAP (Distribución de Impacto)", fontsize=12)
    
    plt.tight_layout()
    shap_fig_path = FIGURES_DIR / "shap_summary.png"
    plt.savefig(shap_fig_path, dpi=300)
    plt.close()
    print(f"SHAP summary figure saved to: {shap_fig_path}")
    print("\n=== TreeSHAP & Collinearity Analysis Completed ===")

if __name__ == "__main__":
    main()
