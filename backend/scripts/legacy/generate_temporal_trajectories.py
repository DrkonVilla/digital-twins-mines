import os
import sys
import numpy as np
import pandas as pd
from pathlib import Path

# Asegurar codificación utf-8 para consola de Windows
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

N_WORKERS = 50
T_STEPS = 200
TOTAL_SAMPLES = N_WORKERS * T_STEPS
SEED = 42

np.random.seed(SEED)

def generate_temporal_trajectories():
    print("=" * 80)
    print("🏔️ GENERANDO SIMULACIÓN DE TRAYECTORIAS SUAVES Y REALISTAS (FICHA 11)")
    print("   [Eliminación del Bug de Oscilación - Eventos de Proximidad Suaves y Multi-Nivel]")
    print(f"   Configuración: {N_WORKERS} trabajadores × {T_STEPS} timesteps = {TOTAL_SAMPLES} registros")
    print("=" * 80)

    rows = []

    for w_id in range(1, N_WORKERS + 1):
        # 1. Definir perfil de eventos de proximidad para el trabajador (3-4 eventos por turno)
        # Evento 1: Moderado (t=30 a 55, min_dist ~14m)
        # Evento 2: Crítico (t=90 a 120, min_dist ~4m)
        # Evento 3: Moderado (t=150 a 175, min_dist ~16m)
        
        # Distancia base nominal segura en galería (35m a 55m)
        base_distance = np.random.uniform(38.0, 52.0)
        
        # Inicialización de fatiga y BPM
        fatigue_index = np.random.uniform(0.05, 0.15)
        worker_bpm = np.random.normal(72, 4)
        gas_co_ppm = np.random.uniform(6.0, 12.0)
        dust_density = np.random.uniform(0.8, 1.8)
        ambient_light = np.random.uniform(45.0, 65.0)

        # Matriz de distancia precalculada suave por trayectorias
        distances = np.full(T_STEPS, base_distance)
        
        # Definición de 3 eventos de aproximación suave con perfil sigmoidal/cosenoidal
        events = [
            {'start': 25, 'dwell': 5, 'end': 55, 'target_dist': np.random.uniform(12.0, 16.0)},
            {'start': 85, 'dwell': 6, 'end': 120, 'target_dist': np.random.uniform(3.0, 7.0)},    # Evento crítico
            {'start': 145, 'dwell': 5, 'end': 175, 'target_dist': np.random.uniform(14.0, 18.0)}
        ]

        for ev in events:
            s, dw, e, target = ev['start'], ev['dwell'], ev['end'], ev['target_dist']
            approach_len = (e - s - dw) // 2
            retreat_len = e - s - dw - approach_len

            # Fase de aproximación suave (Cos1)
            for step_i, t_idx in enumerate(range(s, s + approach_len)):
                tau = step_i / max(1, approach_len - 1)
                factor = 0.5 * (1.0 + np.cos(np.pi * tau))  # 1.0 -> 0.0
                distances[t_idx] = target + (base_distance - target) * factor

            # Fase de permanencia breve en proximidad (Dwell)
            for t_idx in range(s + approach_len, s + approach_len + dw):
                distances[t_idx] = target + np.random.normal(0, 0.3)

            # Fase de retirada suave (Cos2)
            for step_i, t_idx in enumerate(range(s + approach_len + dw, e)):
                tau = step_i / max(1, retreat_len - 1)
                factor = 0.5 * (1.0 - np.cos(np.pi * tau))  # 0.0 -> 1.0
                distances[t_idx] = target + (base_distance - target) * factor

        # Agregar ruido suave a la distancia para simular variabilidad de sensor
        distances += np.random.normal(0, 0.8, T_STEPS)
        distances = np.clip(distances, 1.5, 75.0)

        # Simular serie temporal paso a paso
        for t in range(1, T_STEPS + 1):
            dist_3d = distances[t - 1]

            # Velocidad y TTC coherentes con la distancia
            is_close = dist_3d < 20.0
            worker_speed = np.clip(np.random.normal(1.5 if is_close else 0.8, 0.2), 0.1, 2.5)
            machine_speed = np.clip(np.random.normal(4.0 if is_close else 2.5, 0.8), 0.5, 10.0)
            relative_speed = np.clip(worker_speed + machine_speed, 0.5, 12.0)
            
            ttc = dist_3d / relative_speed
            ttc = np.clip(ttc, 0.2, 90.0)
            in_restricted_zone = 1 if dist_3d < 15.0 else 0

            # Fisiología acoplada suavemente al esfuerzo y proximidad
            # El BPM aumenta cuando el trabajador está cerca de la máquina o se mueve rápido
            target_bpm = 70.0 + (50.0 / np.maximum(dist_3d, 3.0)) * 2.5 + fatigue_index * 30.0
            worker_bpm = 0.88 * worker_bpm + 0.12 * target_bpm + np.random.normal(0, 1.0)
            worker_bpm = np.clip(worker_bpm, 55, 165)

            # Accumulación gradual de fatiga AR(1)
            fatigue_drift = 0.0015 if not (85 <= t <= 105) else -0.003
            fatigue_index = 0.99 * fatigue_index + fatigue_drift + np.random.normal(0, 0.001)
            fatigue_index = np.clip(fatigue_index, 0.02, 0.95)

            # Inercia de gases y ambiente
            gas_spike = 20.0 if (130 <= t <= 160 and w_id % 3 == 0) else 0.0
            gas_co_ppm = 0.92 * gas_co_ppm + 0.08 * (9.0 + gas_spike) + np.random.normal(0, 0.3)
            gas_co_ppm = np.clip(gas_co_ppm, 0.0, 120.0)

            dust_density = 0.93 * dust_density + 0.07 * (1.2 + (machine_speed / 4.0)) + np.random.normal(0, 0.08)
            dust_density = np.clip(dust_density, 0.1, 12.0)

            ambient_light = 0.96 * ambient_light + 0.04 * 50.0 + np.random.normal(0, 0.5)

            # Reconstrucción coherente de coordenadas 3D para la base de datos
            worker_x = 100.0 + (t * 1.5)
            worker_y = 50.0 + np.sin(t / 15.0) * 10.0
            worker_z = -300.0
            
            machine_x = worker_x + dist_3d * 0.8
            machine_y = worker_y + dist_3d * 0.6
            machine_z = worker_z

            rows.append({
                'worker_id': w_id,
                'timestep': t,
                'worker_x': round(worker_x, 2),
                'worker_y': round(worker_y, 2),
                'worker_z': round(worker_z, 2),
                'machine_x': round(machine_x, 2),
                'machine_y': round(machine_y, 2),
                'machine_z': round(machine_z, 2),
                'distance_3d': round(dist_3d, 2),
                'worker_speed': round(worker_speed, 2),
                'machine_speed': round(machine_speed, 2),
                'relative_speed': round(relative_speed, 2),
                'ttc': round(ttc, 2),
                'in_restricted_zone': in_restricted_zone,
                'worker_bpm': round(worker_bpm, 1),
                'fatigue_index': round(fatigue_index, 3),
                'gas_co_ppm': round(gas_co_ppm, 2),
                'dust_density_mg_m3': round(dust_density, 2),
                'ambient_light_lux': round(ambient_light, 1)
            })

    df = pd.DataFrame(rows)

    # --- D. Aplicación de la Función de Riesgo Estocástica No Circular ---
    spatial_risk = (
        (12.0 / np.maximum(df['distance_3d'].values, 0.8)) * 2.0 +
        (8.0 / np.maximum(df['ttc'].values, 0.5)) * 1.8 +
        df['in_restricted_zone'].values * 2.0
    )
    
    multimodal_risk = (
        df['fatigue_index'].values * 1.8 +
        (np.maximum(df['worker_bpm'].values - 60, 0) / 50.0) * 1.0 +
        (df['gas_co_ppm'].values / 40.0) * 1.0 +
        (df['dust_density_mg_m3'].values / 5.0) * 0.6 -
        (df['ambient_light_lux'].values / 120.0) * 0.5
    )
    
    stochastic_noise = np.random.normal(0, 3.5, TOTAL_SAMPLES)
    risk_score = spatial_risk + multimodal_risk + stochastic_noise

    p45, p78 = np.percentile(risk_score, [45, 78])
    risk_level = np.zeros(TOTAL_SAMPLES, dtype=int)
    risk_level[risk_score >= p45] = 1  # MEDIO
    risk_level[risk_score >= p78] = 2  # ALTO

    df['risk_level'] = risk_level

    # Guardar en data/raw/temporal_worker_trajectories.csv
    output_dir = Path(__file__).resolve().parent.parent.parent / "data" / "raw"
    output_dir.mkdir(parents=True, exist_ok=True)
    csv_out = output_dir / "temporal_worker_trajectories.csv"

    df.to_csv(csv_out, index=False)
    print(f"\n✅ Dataset de Trayectorias Temporales Suaves guardado en: {csv_out}")
    print("📊 Distribución de Clases Target (0=BAJO, 1=MEDIO, 2=ALTO):")
    print(df['risk_level'].value_counts(normalize=True))

if __name__ == "__main__":
    generate_temporal_trajectories()
