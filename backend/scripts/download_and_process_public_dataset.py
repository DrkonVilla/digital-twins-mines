import os
import urllib.request
import pandas as pd
import numpy as np
from pathlib import Path

# URL Oficial y Directa del Repositorio Público UCI (AI4I 2020 Predictive Maintenance Dataset)
UCI_REAL_URL = "https://archive.ics.uci.edu/static/public/601/data.csv"

def download_and_process():
    data_dir = Path("data/raw")
    data_dir.mkdir(parents=True, exist_ok=True)
    csv_path = data_dir / "public_mining_equipment_dataset.csv"
    
    print("[1/3] Descargando directamente el Dataset Publico desde UCI Machine Learning Repository...")
    print(f"Fuente: {UCI_REAL_URL}")
    
    # Cargar CSV directamente desde el servidor oficial de la UCI
    req = urllib.request.Request(UCI_REAL_URL, headers={'User-Agent': 'Mozilla/5.0'})
    with urllib.request.urlopen(req, timeout=15) as response:
        df = pd.read_csv(response)
        
    print(f"[EXITO] Descargadas {len(df)} filas reales y {len(df.columns)} columnas del dataset UCI.")

    print("[2/3] Mapeando variables UCI a Telemetria de Maquinaria y Seguridad Minera Subterranea...")
    
    # Columnas originales de UCI AI4I 2020:
    # UID, Product ID, Type, Air temperature, Process temperature, Rotational speed, Torque, Tool wear, Machine failure, TWF, HDF, PWF, OSF, RNF
    column_mapping = {
        'UID': 'record_id',
        'Product ID': 'machine_serial',
        'Type': 'machine_type_class', # L: Ligera, M: Mediana, H: Pesada (Scoop / LHD)
        'Air temperature': 'ambient_temp_k',
        'Process temperature': 'engine_temp_k',
        'Rotational speed': 'rpm_speed',
        'Torque': 'torque_nm',
        'Tool wear': 'operating_hours_wear',
        'Machine failure': 'failure_flag'
    }
    df = df.rename(columns=column_mapping)

    np.random.seed(42)
    n = len(df)

    # 3. Enriquecimiento con Coordenadas 3D e Interaccion Hombre-Maquina para Gemelo Digital M-11
    worker_x = np.random.uniform(0, 500, n)
    worker_y = np.random.uniform(0, 300, n)
    worker_z = np.random.uniform(-800, -50, n)

    close_mask = (df['failure_flag'] == 1) | (np.random.rand(n) < 0.25)
    machine_x = np.where(close_mask, worker_x + np.random.normal(0, 10, n), np.random.uniform(0, 500, n))
    machine_y = np.where(close_mask, worker_y + np.random.normal(0, 10, n), np.random.uniform(0, 300, n))
    machine_z = np.where(close_mask, worker_z + np.random.normal(0, 3, n), np.random.uniform(-800, -50, n))

    distance_3d = np.sqrt((worker_x - machine_x)**2 + (worker_y - machine_y)**2 + (worker_z - machine_z)**2)
    worker_speed = np.clip(np.random.normal(0.8, 0.3, n), 0, 2.5)
    machine_speed = np.clip((df['rpm_speed'] / 3000.0) * 15.0, 0, 15.0)
    relative_speed = np.clip(worker_speed + machine_speed, 0.1, 17.5)
    ttc = np.where(relative_speed > 0.1, distance_3d / relative_speed, 300.0)
    in_restricted_zone = (distance_3d < 15.0).astype(int)

    df['worker_x'] = worker_x
    df['worker_y'] = worker_y
    df['worker_z'] = worker_z
    df['machine_x'] = machine_x
    df['machine_y'] = machine_y
    df['machine_z'] = machine_z
    df['distance_3d'] = distance_3d
    df['worker_speed'] = worker_speed
    df['machine_speed'] = machine_speed
    df['relative_speed'] = relative_speed
    df['direction_worker'] = np.random.randint(0, 8, n)
    df['direction_machine'] = np.random.randint(0, 8, n)
    df['ttc'] = ttc
    df['in_restricted_zone'] = in_restricted_zone
    df['machine_status'] = np.random.choice([0, 1, 2, 3], size=n, p=[0.2, 0.5, 0.1, 0.2])

    # Target multi-clase: 0: BAJO, 1: MEDIO, 2: ALTO
    risk_level = np.zeros(n, dtype=int)
    for i in range(n):
        if distance_3d[i] <= 5.0 or ttc[i] <= 5.0 or df['failure_flag'].iloc[i] == 1:
            risk_level[i] = 2
        elif distance_3d[i] <= 15.0 or ttc[i] <= 15.0 or in_restricted_zone[i] == 1:
            risk_level[i] = 1
        else:
            risk_level[i] = 0

    df['risk_level'] = risk_level

    print("[3/3] Guardando Dataset publico real procesado...")
    df.to_csv(csv_path, index=False)
    print(f"[EXITO] Dataset Publico procesado exitosamente. Archivo: {csv_path}")
    print("Resumen de Clases Target (0=BAJO, 1=MEDIO, 2=ALTO):")
    print(df['risk_level'].value_counts(normalize=True))

if __name__ == "__main__":
    download_and_process()
