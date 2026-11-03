import os
import sys
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

def plot_after():
    csv_path = Path(__file__).resolve().parent.parent.parent / "data" / "raw" / "temporal_worker_trajectories.csv"
    if not csv_path.exists():
        print(f"File not found: {csv_path}")
        return

    df = pd.read_csv(csv_path)
    
    artifacts_dir = Path(__file__).resolve().parent.parent / "app" / "ml" / "artifacts"
    artifacts_dir.mkdir(parents=True, exist_ok=True)
    out_png = artifacts_dir / "trajectory_debug_after.png"

    plt.figure(figsize=(12, 6), dpi=300)
    
    colors = ['#1f77b4', '#ff7f0e', '#2ca02c']
    for idx, w_id in enumerate([1, 2, 3]):
        df_w = df[df['worker_id'] == w_id]
        plt.plot(df_w['timestep'], df_w['distance_3d'], label=f'Trabajador {w_id}', color=colors[idx], alpha=0.9, linewidth=1.8)

    plt.axhline(y=10.0, color='red', linestyle=':', label='Umbral Riesgo Crítico (<10m)', alpha=0.7)
    plt.axhline(y=20.0, color='orange', linestyle='--', label='Umbral Advertencia (<20m)', alpha=0.7)

    plt.title("Serie Temporal de Distancia 3D (DESPUÉS de la Corrección)\nPerfil Continuo Suave con Eventos de Proximidad Multi-Nivel (Crítico ~4m, Moderado ~15m, Seguro ~45m)", fontsize=11, fontweight='bold')
    plt.xlabel("Pasos de Tiempo (Timestep)", fontsize=10)
    plt.ylabel("Distancia 3D (m)", fontsize=10)
    plt.grid(True, linestyle='--', alpha=0.5)
    plt.legend(loc='upper right')
    plt.tight_layout()
    plt.savefig(out_png)
    plt.close()

    print(f"✅ Gráfico corregido guardado en: {out_png}")

if __name__ == "__main__":
    plot_after()
