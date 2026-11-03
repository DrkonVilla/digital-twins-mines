import os
import sys
import numpy as np
import pandas as pd
from datetime import datetime
from hmmlearn.hmm import GaussianHMM

# Asegurar codificación utf-8 para salida de consola en Windows
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

# Matriz Heurística Original de Diseño (hmm_model.py)
A_HEURISTIC = np.array([
    [0.85, 0.12, 0.03],  # Estado 0: SEGURO
    [0.20, 0.65, 0.15],  # Estado 1: INCIPIENTE
    [0.05, 0.25, 0.70]   # Estado 2: INMINENTE
])

MEANS_HEURISTIC = np.array([
    [35.0, 45.0, 75.0, 0.15, 8.0],   # Estado 0: SEGURO
    [12.0, 12.0, 105.0, 0.45, 25.0],  # Estado 1: INCIPIENTE
    [3.0, 3.0, 135.0, 0.80, 65.0]     # Estado 2: INMINENTE
])

STDS_HEURISTIC = np.array([
    [10.0, 15.0, 10.0, 0.10, 5.0],
    [4.0, 4.0, 12.0, 0.12, 10.0],
    [1.5, 1.5, 15.0, 0.10, 20.0]
])

STATE_LABELS = {0: "SEGURO (S0)", 1: "INCIPIENTE (S1)", 2: "INMINENTE (S2)"}
FEATURE_NAMES = ["distance_3d (m)", "ttc (s)", "worker_bpm", "fatigue_index", "gas_co_ppm (ppm)"]

def run_baum_welch_training():
    print("=" * 80)
    print("🤖 TAREA 1: ENTRENAMIENTO HMM MEDIANTE ALGORITMO BAUM-WELCH (EM)")
    print("   [Ajuste de Parámetros de Pipeline - Proof-of-Concept / Telemetría Minera]")
    print(f"   Fecha de ejecución: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)

    # 1. Carga del Dataset de Trayectorias Temporales Continuas
    temporal_csv_path = os.path.join(os.path.dirname(__file__), "..", "..", "data", "raw", "temporal_worker_trajectories.csv")
    dataset_path = os.path.abspath(temporal_csv_path)

    if not os.path.exists(dataset_path):
        # Fallback si no se ha ejecutado el generador temporal
        fallback_path = os.path.join(os.path.dirname(__file__), "..", "..", "data", "raw", "public_mining_equipment_dataset.csv")
        dataset_path = os.path.abspath(fallback_path)

    df = pd.read_csv(dataset_path)
    print(f"\n📂 Dataset cargado: {dataset_path}")
    print(f"   Dimensiones reales: {df.shape[0]} filas × {df.shape[1]} columnas")

    # 2. Inspección de Columnas y Variables Seleccionadas
    print("\n🔍 Paso 1 & 2: Inspección de Variables y Mapeo a Emisiones del HMM")
    print("-" * 75)
    raw_cols = [col.split()[0] for col in FEATURE_NAMES]
    for i, col in enumerate(FEATURE_NAMES):
        raw_col = col.split()[0]
        print(f"   Dimensión {i+1} [{col}]: Columna '{raw_col}' | Min={df[raw_col].min():.2f}, Max={df[raw_col].max():.2f}, Mean={df[raw_col].mean():.2f}")

    # 3. Ventaneo Temporal Estructurado por Trabajador (worker_id)
    print("\n✂️ Paso 3: Agrupamiento de Secuencias Temporales por worker_id")
    print("-" * 75)
    
    if 'worker_id' in df.columns:
        # Agrupar explícitamente por worker_id para garantizar continuidad de Markov por sujeto
        grouped = df.groupby('worker_id')
        lengths = grouped.size().tolist()
        obs_data = df[raw_cols].values
        n_workers = len(lengths)
        seq_len_mean = np.mean(lengths)
        print(f"   ✅ Estructura temporal válida detectada: {n_workers} trabajadores identificados.")
        print(f"   Longitud media por secuencia de trabajador: T = {seq_len_mean:.1f} pasos temporales.")
    else:
        # Fallback a ventaneo ciego de 100 en datos desestructurados
        seq_length = 100
        n_sequences = len(df) // seq_length
        lengths = [seq_length] * n_sequences
        obs_data = df[raw_cols].values[:n_sequences * seq_length]
        print(f"   ⚠️ ADVERTENCIA: No se encontró worker_id. Usando rebanadas fijas T=100.")

    print(f"   Total de observaciones procesadas: {len(obs_data)}")
    print(f"   Estructura del vector lengths: {len(lengths)} secuencias independientes.")

    # 4. Entrenamiento Baum-Welch (GaussianHMM)
    print("\n⚙️ Paso 4 & 5: Entrenamiento Baum-Welch (EM) sobre Secuencias Temporales")
    print("-" * 75)

    hmm = GaussianHMM(
        n_components=3,
        covariance_type='diag',
        n_iter=50,
        random_state=42,
        verbose=True
    )

    hmm.fit(obs_data, lengths)

    final_log_likelihood = hmm.score(obs_data, lengths)
    print(f"\n   ✅ Baum-Welch completado exitosamente.")
    print(f"   📈 Log-Likelihood Final de Convergencia: {final_log_likelihood:.4f}")
    print(f"   📈 Log-Likelihood Medio por Muestra: {final_log_likelihood / len(obs_data):.4f}")

    # 5. Extracción de Parámetros Aprendidos
    print("\n📊 Paso 6: Extracción de Parámetros Aprendidos (A_trained, Medias y Covarianzas)")
    print("-" * 75)
    A_trained = hmm.transmat_
    means_trained = hmm.means_
    covars_trained = hmm.covars_

    print("\n--- MATRIZ DE TRANSICIÓN APRENDIDA (A_trained completa, sin redondear) ---")
    print(A_trained)

    print("\n--- MEDIAS DE EMISIÓN APRENDIDAS POR ESTADO ---")
    means_df = pd.DataFrame(means_trained, columns=raw_cols, index=["Estado 0", "Estado 1", "Estado 2"])
    print(means_df.to_string())

    print("\n--- COVARIANZAS/VARIANZAS DE EMISIÓN APRENDIDAS POR ESTADO ---")
    covars_diag = np.diagonal(covars_trained, axis1=1, axis2=2) if covars_trained.ndim == 3 else covars_trained
    covars_df = pd.DataFrame(covars_diag, columns=raw_cols, index=["Estado 0", "Estado 1", "Estado 2"])
    print(covars_df.to_string())

    # 6. Tabla Comparativa A_heuristic vs A_trained
    print("\n⚖️ Paso 7: Tabla Comparativa Directa A_heuristic vs A_trained")
    print("=" * 80)
    print(f"{'Origen':<15} | {'Destino':<15} | {'P(Heurística)':<15} | {'P(Aprendida BW)':<15} | {'Diferencia Rel.':<15}")
    print("-" * 80)

    states = ["SEGURO", "INCIPIENTE", "INMINENTE"]
    diff_matrix = A_trained - A_HEURISTIC

    for i in range(3):
        for j in range(3):
            orig = states[i]
            dest = states[j]
            p_heur = A_HEURISTIC[i, j]
            p_train = A_trained[i, j]
            diff = diff_matrix[i, j]
            print(f"{orig:<15} -> {dest:<15} | {p_heur:<15.4f} | {p_train:<15.4f} | {diff:<+15.4f}")

    # 7. Diagnóstico de Inercia Temporal y Separabilidad
    print("\n📝 Paso 8: Diagnóstico de Inercia Temporal y Separabilidad Fisiológica")
    print("-" * 80)
    diag_mean = np.mean(np.diag(A_trained))
    print(f"1. Inercia de Transición Diagonal Media: P(S_i -> S_i) = {diag_mean:.4f}")
    if diag_mean > 0.70:
        print("   ✅ ALTA INERCIA TEMPORAL DECTECTADA: El modelo aprendió persistencia real de estados en el tiempo.")
    else:
        print("   ⚠️ INERCIA TEMPORAL MODERADA / BAJA: El modelo presenta transiciones relativamente frecuentes entre estados.")

    print("2. Separabilidad Fisiológica (BPM / Fatiga por Estado):")
    for s_idx in range(3):
        print(f"   - Estado {s_idx}: BPM={means_trained[s_idx, 2]:.1f}, Fatiga={means_trained[s_idx, 3]:.3f}, Distancia3D={means_trained[s_idx, 0]:.1f}m")
    print("=" * 80)
    print("✅ PROCESO DE ENTRENAMIENTO BAUM-WELCH FINALIZADO EXITOSAMENTE.")

if __name__ == "__main__":
    run_baum_welch_training()
