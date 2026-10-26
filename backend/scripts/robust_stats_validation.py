import os
import sys
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime
from scipy import stats
from sklearn.model_selection import StratifiedKFold
from sklearn.metrics import f1_score, accuracy_score

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import fair_eval as fe  # noqa: E402

# Asegurar codificación utf-8 en consola de Windows
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

RANDOM_STATE = 42

# Grupos de variables comparados en la ablación pareada (misma partición y mismos pliegues)
FEATURES_BASE = ['distance_3d', 'ttc', 'relative_speed', 'in_restricted_zone']
FEATURES_HYBRID = FEATURES_BASE + ['worker_bpm', 'fatigue_index', 'gas_co_ppm', 'dust_density_mg_m3']


def _cv_scores(X_df, y, features, skf):
    """F1-macro y accuracy por fold con SMOTENC + escalado AJUSTADOS DENTRO DE CADA FOLD."""
    X = X_df[features].values.astype(float)
    f1s, accs = [], []
    for tr, te in skf.split(X, y):
        pipe = fe.make_pipeline("XGBoost", features=features)
        pipe.fit(X[tr], y[tr])
        pred = pipe.predict(X[te])
        f1s.append(f1_score(y[te], pred, average='macro'))
        accs.append(accuracy_score(y[te], pred))
    return np.array(f1s), np.array(accs)


def run_robust_stats_validation():
    print("=" * 85)
    print("🔬 VALIDACIÓN TÉCNICA DE PIPELINE - PROOF OF CONCEPT (PoC)")
    print("   [Ablación Multimodal Pareada: Modelo Cinemático Base vs Modelo Híbrido]")
    print("   ⚠️ AVISO METODOLÓGICO: el target es sintético; esto verifica la integridad de la")
    print("      arquitectura y NO constituye validación empírica de campo.")
    print("   ✔ SMOTENC y escalado se ajustan DENTRO de cada fold (sin fuga de información).")
    print(f"   Fecha de ejecución: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 85)

    df = fe.load_dataset()
    print(f"\n📂 Dataset cargado: {fe.DATASET_PATH} ({len(df)} registros)")

    y = df['risk_level'].astype(int).values
    print(f"\n📋 Definición de Experimentos:")
    print(f"   - Modelo Base (Cinemático Espacial)    [{len(FEATURES_BASE)} features]: {FEATURES_BASE}")
    print(f"   - Modelo Híbrido (Multimodal)          [{len(FEATURES_HYBRID)} features]: {FEATURES_HYBRID}")
    print(f"   - Distribución de Clases Target: {dict(pd.Series(y).value_counts())}")

    n_splits = 10
    print(f"\n⚙️ Ejecutando Stratified {n_splits}-Fold CV (mismos pliegues para ambos modelos)...")
    skf = StratifiedKFold(n_splits=n_splits, shuffle=True, random_state=RANDOM_STATE)

    f1_base_folds, acc_base_folds = _cv_scores(df, y, FEATURES_BASE, skf)
    f1_hybrid_folds, acc_hybrid_folds = _cv_scores(df, y, FEATURES_HYBRID, skf)

    diffs = f1_hybrid_folds - f1_base_folds
    t_stat, p_val_t = stats.ttest_rel(f1_hybrid_folds, f1_base_folds)
    try:
        w_stat, p_val_w = stats.wilcoxon(f1_hybrid_folds, f1_base_folds)
    except ValueError:
        w_stat, p_val_w = 0.0, 1.0

    print("\n📊 TABLA DE RESULTADOS POR FOLD (F1-SCORE MACRO):")
    print("=" * 75)
    print(f"{'Fold':<8} | {'F1 Base (Cinemático)':<22} | {'F1 Híbrido (Multimodal)':<24} | {'Diferencia (H-B)':<15}")
    print("-" * 75)
    for i in range(n_splits):
        print(f"Fold {i+1:<3} | {f1_base_folds[i]:<22.4f} | {f1_hybrid_folds[i]:<24.4f} | {diffs[i]:<+15.4f}")
    print("-" * 75)

    mean_base, mean_hybrid, mean_diff = f1_base_folds.mean(), f1_hybrid_folds.mean(), diffs.mean()
    std_base, std_hybrid = np.std(f1_base_folds, ddof=1), np.std(f1_hybrid_folds, ddof=1)
    std_diff = np.std(diffs, ddof=1)
    print(f"{'MEDIA':<8} | {mean_base:<22.4f} | {mean_hybrid:<24.4f} | {mean_diff:<+15.4f}")
    print(f"{'DESV.EST':<8} | {std_base:<22.4f} | {std_hybrid:<24.4f} | {std_diff:<15.4f}")
    print("=" * 75)

    # Diagnóstico estadístico. NOTA: las diferencias entre folds de CV no son independientes
    # (los conjuntos de entrenamiento se solapan), por lo que los p-valores de t/Wilcoxon son
    # optimistas. Se acompañan de Cliff's delta y se corrigen por Holm; la comparación
    # confirmatoria es el bootstrap pareado de train_cv.py / run_ablation_study.py.
    shapiro_stat, shapiro_p = stats.shapiro(diffs)
    cohen_d = mean_diff / (std_diff if std_diff > 0 else 1e-6)
    cliff = fe.cliffs_delta(f1_hybrid_folds, f1_base_folds)
    holm_p = fe.holm_adjust([p_val_t, p_val_w])
    se_diff = std_diff / np.sqrt(n_splits)
    t_crit = stats.t.ppf(0.975, df=n_splits - 1)
    ic_inf, ic_sup = mean_diff - t_crit * se_diff, mean_diff + t_crit * se_diff

    print("\n📈 PRUEBAS ESTADÍSTICAS PAREADAS:")
    print("-" * 75)
    print(f"0. Shapiro-Wilk de las diferencias: W={shapiro_stat:.4f}, p={shapiro_p:.4f} -> "
          f"{'Normal' if shapiro_p >= 0.05 else 'No normal (preferir Wilcoxon)'}")
    print(f"1. t de Student pareada : t={t_stat:.4f} | p={p_val_t:.4e} | p Holm={holm_p[0]:.4e}")
    print(f"2. Wilcoxon signed-rank : W={w_stat:.4f} | p={p_val_w:.4e} | p Holm={holm_p[1]:.4e}")
    print(f"3. Tamaño de efecto     : Cohen's d={cohen_d:.4f} | Cliff's delta={cliff:+.3f} ({fe.cliffs_label(cliff)})")
    print(f"   IC 95% de ΔF1 (t, n={n_splits}): [{ic_inf:+.4f}, {ic_sup:+.4f}]")

    artifacts_dir = str(fe.ARTIFACT_DIR)
    os.makedirs(artifacts_dir, exist_ok=True)
    plot_path = os.path.join(artifacts_dir, "ablation_f1_comparison.png")

    plt.figure(figsize=(9, 6), dpi=300)
    sns.set_theme(style="whitegrid")
    plot_data = pd.DataFrame({
        'F1-Score': list(f1_base_folds) + list(f1_hybrid_folds),
        'Modelo': ['Base (Cinemático)'] * n_splits + ['Híbrido (Multimodal)'] * n_splits
    })
    sns.boxplot(x='Modelo', y='F1-Score', hue='Modelo', data=plot_data, palette=['#e74c3c', '#2ecc71'],
                width=0.4, boxprops=dict(alpha=0.8), legend=False)
    sns.stripplot(x='Modelo', y='F1-Score', data=plot_data, color='black', size=7, jitter=0.15, alpha=0.7)
    plt.title(f"Estudio de Ablación de Pipeline: Distribución de F1-Score ({n_splits}-Fold CV, SMOTENC anidado)\n"
              "Modelo Cinemático Base vs Modelo Híbrido Multimodal", fontsize=12, fontweight='bold', pad=15)
    plt.ylabel("F1-Score (Macro Average)", fontsize=11)
    plt.xlabel("Arquitectura de Características", fontsize=11)
    lo = max(0.0, float(min(f1_base_folds.min(), f1_hybrid_folds.min())) - 0.05)
    plt.ylim(lo, min(1.02, float(max(f1_base_folds.max(), f1_hybrid_folds.max())) + 0.05))
    plt.text(0.5, lo + 0.01, f"t pareada: t={t_stat:.2f}, p_Holm={holm_p[0]:.2e}\nWilcoxon: W={w_stat:.1f}, p_Holm={holm_p[1]:.4f}\n"
                             f"Cliff's δ={cliff:+.2f} ({fe.cliffs_label(cliff)})",
             horizontalalignment='center', bbox=dict(boxstyle='round,pad=0.5', facecolor='white', edgecolor='gray', alpha=0.9), fontsize=10)
    plt.tight_layout()
    plt.savefig(plot_path)
    plt.close()

    fe.dump_json({
        "protocol": "10-fold estratificado, SMOTENC + escalado dentro de cada fold, mismos pliegues",
        "features_base": FEATURES_BASE, "features_hybrid": FEATURES_HYBRID,
        "f1_macro_base_folds": f1_base_folds, "f1_macro_hybrid_folds": f1_hybrid_folds,
        "accuracy_base_folds": acc_base_folds, "accuracy_hybrid_folds": acc_hybrid_folds,
        "mean_diff_f1": mean_diff, "ci95_t": [ic_inf, ic_sup],
        "paired_t": {"t": t_stat, "p": p_val_t, "p_holm": holm_p[0]},
        "wilcoxon": {"W": w_stat, "p": p_val_w, "p_holm": holm_p[1]},
        "cohens_d": cohen_d, "cliffs_delta": cliff, "cliffs_label": fe.cliffs_label(cliff),
        "caveat": "Los folds de CV no son independientes; los p-valores son orientativos. "
                  "La inferencia confirmatoria usa bootstrap pareado + McNemar (train_cv.py).",
    }, os.path.join(artifacts_dir, "robust_stats_validation.json"))

    print(f"\n🖼️ Gráfico comparativo de ablación guardado en: {plot_path}")
    print("=" * 85)
    print("✅ VALIDACIÓN TÉCNICA Y PRUEBAS ESTADÍSTICAS FINALIZADAS EXITOSAMENTE.")


if __name__ == "__main__":
    run_robust_stats_validation()
