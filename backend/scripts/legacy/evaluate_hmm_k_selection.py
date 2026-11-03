import os
import sys
import json
import numpy as np
import pandas as pd
from pathlib import Path
import matplotlib.pyplot as plt
from hmmlearn.hmm import GaussianHMM

# Ensure UTF-8 output
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

FEATURE_NAMES = ["distance_3d", "ttc", "worker_bpm", "fatigue_index", "gas_co_ppm"]

def evaluate_hmm_selection():
    print("=" * 80)
    print("🔬 SELECCIÓN OBJETIVA DEL NÚMERO DE ESTADOS HMM (BIC/AIC & K=4) - FICHA 11")
    print("================================================================================")

    csv_path = Path(__file__).resolve().parent.parent.parent / "data" / "raw" / "temporal_worker_trajectories.csv"
    if not csv_path.exists():
        print(f"❌ Error: No se encontró el dataset en {csv_path}")
        return

    df = pd.read_csv(csv_path)
    grouped = df.groupby('worker_id')
    lengths = grouped.size().tolist()
    obs_data = df[FEATURE_NAMES].values
    N_samples = len(obs_data)
    N_features = len(FEATURE_NAMES)

    print(f"📂 Dataset cargado: {len(df)} registros ({len(lengths)} secuencias de T={np.mean(lengths):.0f})")
    print(f"   Variables de Emisión (d=5): {FEATURE_NAMES}")

    # =========================================================================
    # TAREA 1: EVALUACIÓN DETALLADA PARA K = 4
    # =========================================================================
    print("\n" + "=" * 80)
    print("1. EVALUACIÓN Y ENTRENAMIENTO DETALLADO PARA K = 4 ESTADOS")
    print("=" * 80)

    hmm_k4 = GaussianHMM(n_components=4, covariance_type='diag', n_iter=60, random_state=42)
    hmm_k4.fit(obs_data, lengths)
    log_l_k4 = hmm_k4.score(obs_data, lengths)
    log_l_k4_sample = log_l_k4 / N_samples

    print(f"✅ HMM (K=4) Entrenado exitosamente.")
    print(f"📈 Log-Likelihood Total (K=4): {log_l_k4:.4f}")
    print(f"📈 Log-Likelihood Medio por Muestra (K=4): {log_l_k4_sample:.4f}")

    print("\n--- MATRIZ DE TRANSICIÓN APRENDIDA (A_trained 4x4) ---")
    print(pd.DataFrame(hmm_k4.transmat_, 
                       index=[f"Estado {i}" for i in range(4)], 
                       columns=[f"Estado {j}" for j in range(4)]).to_string())

    print("\n--- MEDIAS DE EMISIÓN POR ESTADO (K=4) ---")
    means_k4_df = pd.DataFrame(hmm_k4.means_, columns=FEATURE_NAMES, index=[f"Estado {i}" for i in range(4)])
    print(means_k4_df.to_string())

    # Sort states by distance_3d
    sorted_indices_k4 = np.argsort(hmm_k4.means_[:, 0])[::-1]  # Highest to lowest distance
    print("\n--- MEDIAS ORDENADAS POR DISTANCIA 3D (DE MAYOR A MENOR) ---")
    for rank, idx in enumerate(sorted_indices_k4, start=1):
        m = hmm_k4.means_[idx]
        print(f"   Posición {rank} [Estado {idx}]: Distancia3D={m[0]:.2f}m | TTC={m[1]:.2f}s | BPM={m[2]:.1f} | Fatiga={m[3]:.3f} | GasCO={m[4]:.2f}ppm")

    # =========================================================================
    # TAREA 2: SELECCIÓN DE ESTADOS CON BIC Y AIC (K = 2, 3, 4, 5, 6)
    # =========================================================================
    print("\n" + "=" * 80)
    print("2. CRITERIOS DE INFORMACIÓN BIC Y AIC PARA K = {2, 3, 4, 5, 6}")
    print("=" * 80)

    results = []

    for k in range(2, 7):
        hmm_k = GaussianHMM(n_components=k, covariance_type='diag', n_iter=60, random_state=42)
        hmm_k.fit(obs_data, lengths)
        ll = hmm_k.score(obs_data, lengths)
        
        # Parámetros libres HMM con covarianza diagonal:
        # Transición (k*(k-1)) + Medias (k*d) + Varianzas (k*d) + Init Probs (k-1)
        n_params = k * (k - 1) + 2 * k * N_features + (k - 1)
        
        bic = -2 * ll + n_params * np.log(N_samples)
        aic = -2 * ll + 2 * n_params

        results.append({
            'k': k,
            'log_likelihood': ll,
            'll_per_sample': ll / N_samples,
            'n_params': n_params,
            'bic': bic,
            'aic': aic,
            'model': hmm_k
        })

    df_res = pd.DataFrame(results)[['k', 'log_likelihood', 'll_per_sample', 'n_params', 'bic', 'aic']]
    print("\n📊 TABLA DE EVALUACIÓN DE CRITERIOS DE INFORMACIÓN BIC / AIC:")
    print("=" * 85)
    print(df_res.to_string(index=False))
    print("=" * 85)

    best_bic_k = df_res.loc[df_res['bic'].idxmin()]['k']
    best_aic_k = df_res.loc[df_res['aic'].idxmin()]['k']

    print(f"\n🏆 Número óptimo de estados según BIC (conservador): K = {int(best_bic_k)}")
    print(f"🏆 Número óptimo de estados según AIC:                K = {int(best_aic_k)}")

    # Guardar gráfico del codo BIC / AIC
    artifacts_dir = Path(__file__).resolve().parent.parent / "app" / "ml" / "artifacts"
    artifacts_dir.mkdir(parents=True, exist_ok=True)
    plot_path = artifacts_dir / "hmm_bic_aic_elbow.png"

    fig, ax1 = plt.subplots(figsize=(9, 5), dpi=300)

    color = '#1f77b4'
    ax1.set_xlabel('Número de Estados (K)', fontsize=11, fontweight='bold')
    ax1.set_ylabel('BIC (Criterio de Información Bayesiano)', color=color, fontsize=11, fontweight='bold')
    line1 = ax1.plot(df_res['k'], df_res['bic'], color=color, marker='o', linewidth=2, label='BIC')
    ax1.tick_params(axis='y', labelcolor=color)
    ax1.grid(True, linestyle='--', alpha=0.5)

    ax2 = ax1.twinx()
    color = '#e74c3c'
    ax2.set_ylabel('AIC (Criterio de Información de Akaike)', color=color, fontsize=11, fontweight='bold')
    line2 = ax2.plot(df_res['k'], df_res['aic'], color=color, marker='s', linestyle='--', linewidth=2, label='AIC')
    ax2.tick_params(axis='y', labelcolor=color)

    plt.title("Evaluación de Selección de Estados HMM: Criterios BIC y AIC vs. K\nGemelo Digital M-11 (Telemetría Temporal)", fontsize=11, fontweight='bold', pad=12)
    fig.tight_layout()
    plt.savefig(plot_path)
    plt.close()

    print(f"🖼️ Gráfico del codo BIC/AIC guardado en: {plot_path}")

    # Exportar resultados estructurados a JSON
    report_data = {
        "bic_best_k": int(best_bic_k),
        "aic_best_k": int(best_aic_k),
        "evaluation_table": df_res.to_dict(orient="records")
    }
    with open(artifacts_dir / "hmm_k_selection_report.json", "w", encoding="utf-8") as f:
        json.dump(report_data, f, indent=2)

if __name__ == "__main__":
    evaluate_hmm_selection()
