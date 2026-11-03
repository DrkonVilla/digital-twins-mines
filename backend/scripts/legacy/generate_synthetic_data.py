import os
import numpy as np
import pandas as pd
from pathlib import Path

# Configuración
N_SAMPLES = 50000
N_WORKERS = 50
N_MACHINES = 15
SEED = 42
np.random.seed(SEED)

def generate_synthetic_data():
    print(f"Generating {N_SAMPLES} synthetic records...")
    
    # 1-3. Trabajador Posición (X, Y, Z)
    worker_x = np.random.uniform(0, 500, N_SAMPLES)
    worker_y = np.random.uniform(0, 300, N_SAMPLES)
    worker_z = np.random.uniform(-800, -50, N_SAMPLES)
    
    # 4-6. Máquina Posición (X, Y, Z)
    # Generamos la posición de la máquina. Para forzar interacciones, un % de las veces la pondremos cerca del trabajador.
    close_interaction_mask = np.random.rand(N_SAMPLES) < 0.3 # 30% of time close interaction
    
    machine_x = np.where(close_interaction_mask, worker_x + np.random.normal(0, 15, N_SAMPLES), np.random.uniform(0, 500, N_SAMPLES))
    machine_y = np.where(close_interaction_mask, worker_y + np.random.normal(0, 15, N_SAMPLES), np.random.uniform(0, 300, N_SAMPLES))
    machine_z = np.where(close_interaction_mask, worker_z + np.random.normal(0, 5, N_SAMPLES), np.random.uniform(-800, -50, N_SAMPLES))
    
    # 7. Distancia 3D
    distance_3d = np.sqrt((worker_x - machine_x)**2 + (worker_y - machine_y)**2 + (worker_z - machine_z)**2)
    
    # 8. Velocidad del trabajador (0 a 2.5 m/s)
    worker_speed = np.abs(np.random.normal(0.8, 0.3, N_SAMPLES))
    worker_speed = np.clip(worker_speed, 0, 2.5)
    
    # 9. Velocidad de la máquina (0 a 15 m/s)
    # Status: 0=Detenida, 1=Operando, 2=Reversa, 3=Transporte
    machine_status = np.random.choice([0, 1, 2, 3], size=N_SAMPLES, p=[0.3, 0.4, 0.1, 0.2])
    machine_speed = np.zeros(N_SAMPLES)
    
    mask_op = machine_status == 1
    machine_speed[mask_op] = np.abs(np.random.normal(3.0, 1.0, np.sum(mask_op)))
    mask_rev = machine_status == 2
    machine_speed[mask_rev] = np.abs(np.random.normal(1.5, 0.5, np.sum(mask_rev)))
    mask_trans = machine_status == 3
    machine_speed[mask_trans] = np.abs(np.random.normal(8.0, 2.0, np.sum(mask_trans)))
    machine_speed = np.clip(machine_speed, 0, 15)
    
    # 10. Velocidad relativa
    # Aproximación simple: suma de velocidades si van en direcciones opuestas, resta si van en la misma
    relative_speed_factor = np.random.uniform(0.1, 2.0, N_SAMPLES)
    relative_speed = np.clip((worker_speed + machine_speed) * relative_speed_factor, 0, 17.5)
    
    # 11-12. Direcciones
    direction_worker = np.random.randint(0, 8, N_SAMPLES)
    direction_machine = np.random.randint(0, 8, N_SAMPLES)
    
    # 13. TTC (Time To Collision)
    # Si distance es pequeña o relative speed alta, TTC pequeño.
    # Evitar div por cero
    ttc = np.where(relative_speed > 0.1, distance_3d / relative_speed, 300.0)
    # Introducimos ruido
    ttc = ttc + np.random.normal(0, 2.0, N_SAMPLES)
    ttc = np.clip(ttc, 0, 300)
    
    # 14. Zona restringida (0 o 1)
    # Mayor probabilidad si están cerca
    in_restricted_zone = np.where(distance_3d < 20, np.random.choice([0, 1], p=[0.7, 0.3], size=N_SAMPLES), np.random.choice([0, 1], p=[0.9, 0.1], size=N_SAMPLES))
    
    # TARGET: risk_level
    # 0: BAJO, 1: MEDIO, 2: ALTO
    risk_level = np.zeros(N_SAMPLES, dtype=int)
    
    for i in range(N_SAMPLES):
        dist = distance_3d[i]
        t = ttc[i]
        restr = in_restricted_zone[i]
        ms = machine_speed[i]
        
        # ALTO crítico
        if dist <= 5 or t <= 5:
            risk_level[i] = 2
        # ALTO
        elif dist <= 10 or t <= 15 or (restr == 1 and ms > 0):
            risk_level[i] = 2
        # MEDIO
        elif (dist <= 30 and dist > 10) and t > 15:
            risk_level[i] = 1
        # BAJO
        elif dist > 30 and t > 60 and restr == 0:
            risk_level[i] = 0
        else:
            # Regla por defecto para casos grises
            if dist > 20:
                risk_level[i] = 0
            else:
                risk_level[i] = 1

    df = pd.DataFrame({
        'worker_x': worker_x,
        'worker_y': worker_y,
        'worker_z': worker_z,
        'machine_x': machine_x,
        'machine_y': machine_y,
        'machine_z': machine_z,
        'distance_3d': distance_3d,
        'worker_speed': worker_speed,
        'machine_speed': machine_speed,
        'relative_speed': relative_speed,
        'direction_worker': direction_worker,
        'direction_machine': direction_machine,
        'ttc': ttc,
        'in_restricted_zone': in_restricted_zone,
        'machine_status': machine_status,
        'risk_level': risk_level
    })
    
    print(f"Distribution of risk_level:")
    print(df['risk_level'].value_counts(normalize=True))
    
    # Guardar raw data
    data_dir = Path("../../data/raw")
    data_dir.mkdir(parents=True, exist_ok=True)
    out_path = data_dir / "synthetic_interactions.csv"
    df.to_csv(out_path, index=False)
    print(f"Saved synthetic data to {out_path}")

if __name__ == "__main__":
    generate_synthetic_data()
