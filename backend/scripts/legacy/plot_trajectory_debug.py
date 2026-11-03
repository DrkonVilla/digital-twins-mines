import os
import sys
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path

# Ensure UTF-8 console output
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

def plot_debug():
    csv_path = Path(__file__).resolve().parent.parent.parent / "data" / "raw" / "temporal_worker_trajectories.csv"
    if not csv_path.exists():
        print(f"File not found: {csv_path}")
        return

    df = pd.read_csv(csv_path)
    
    artifacts_dir = Path(__file__).resolve().parent.parent / "app" / "ml" / "artifacts"
    artifacts_dir.mkdir(parents=True, exist_ok=True)
    out_png = artifacts_dir / "trajectory_debug_before.png"

    plt.figure(figsize=(12, 6), dpi=300)
    
    # Plot first 3 workers
    for w_id in [1, 2, 3]:
        df_w = df[df['worker_id'] == w_id]
        plt.plot(df_w['timestep'], df_w['distance_3d'], label=f'Trabajador {w_id}', alpha=0.8, linewidth=1.5)

    plt.title("Serie Temporal de Distancia 3D (Antes de la Corrección)\nDemostración de Oscilación / Jitter de Alta Frecuencia (Bug np.sign / Bang-Bang)", fontsize=11, fontweight='bold')
    plt.xlabel("Pasos de Tiempo (Timestep)", fontsize=10)
    plt.ylabel("Distancia 3D (m)", fontsize=10)
    plt.grid(True, linestyle='--', alpha=0.5)
    plt.legend()
    plt.tight_layout()
    plt.savefig(out_png)
    plt.close()

    print(f"✅ Gráfico de diagnóstico guardado en: {out_png}")

if __name__ == "__main__":
    plot_debug()
