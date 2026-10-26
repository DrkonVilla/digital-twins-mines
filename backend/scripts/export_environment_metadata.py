"""
Reproducibilidad: requirements fijados, checksum del dataset y diccionario de variables.

Genera:
  requirements.txt                  (raíz) versiones EXACTAS del entorno donde se ejecutó el pipeline
  DATASET_CHECKSUM.sha256           SHA-256 de data/raw/public_mining_equipment_dataset.csv
  results/environment_metadata.json Python, SO, semillas, versiones y hash del dataset
  results/feature_dictionary.csv    Las 37 variables del dataset (anexo para la Tabla 1, FON-05)

Uso:  python backend/scripts/export_environment_metadata.py
"""
import csv
import hashlib
import json
import os
import platform
import re
import sys
from datetime import datetime, timezone
from importlib import metadata

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import fair_eval as fe  # noqa: E402

ROOT = fe.PROJECT_ROOT

# Paquetes que determinan el resultado del pipeline + dashboard + backend
CORE = ["numpy", "pandas", "scipy", "scikit-learn", "xgboost", "imbalanced-learn", "joblib",
        "matplotlib", "seaborn", "plotly", "psutil", "streamlit"]
BACKEND_PKGS = ["fastapi", "uvicorn", "sqlalchemy", "alembic", "pydantic", "pydantic-settings",
                "websockets", "langchain", "langchain-core", "langchain-google-genai",
                "google-generativeai", "reportlab", "openpyxl", "python-docx"]

# (columna, rol, tipo, unidad, origen/descripción)
FEATURE_DICTIONARY = [
    ("record_id", "id", "int", "-", "UCI AI4I 2020 (UID); no se usa como predictor"),
    ("machine_serial", "id", "str", "-", "UCI AI4I 2020 (Product ID); no se usa como predictor"),
    ("machine_type_class", "contexto", "cat (L/M/H)", "-", "UCI AI4I 2020 (Type): clase de equipo"),
    ("ambient_temp_k", "contexto", "float", "K", "UCI AI4I 2020 (Air temperature)"),
    ("engine_temp_k", "contexto", "float", "K", "UCI AI4I 2020 (Process temperature)"),
    ("rpm_speed", "contexto", "int", "rpm", "UCI AI4I 2020 (Rotational speed); genera machine_speed"),
    ("torque_nm", "contexto", "float", "N·m", "UCI AI4I 2020 (Torque)"),
    ("operating_hours_wear", "contexto", "int", "min", "UCI AI4I 2020 (Tool wear)"),
    ("failure_flag", "contexto", "bin", "-", "UCI AI4I 2020 (Machine failure); condiciona la cercanía simulada"),
    ("TWF", "contexto", "bin", "-", "UCI AI4I 2020: falla por desgaste de herramienta"),
    ("HDF", "contexto", "bin", "-", "UCI AI4I 2020: falla por disipación de calor"),
    ("PWF", "contexto", "bin", "-", "UCI AI4I 2020: falla de potencia"),
    ("OSF", "contexto", "bin", "-", "UCI AI4I 2020: falla por sobreesfuerzo"),
    ("RNF", "contexto", "bin", "-", "UCI AI4I 2020: falla aleatoria"),
    ("worker_x", "posición (simulada)", "float", "m", "Uniforme(0,500)"),
    ("worker_y", "posición (simulada)", "float", "m", "Uniforme(0,300)"),
    ("worker_z", "posición (simulada)", "float", "m", "Uniforme(-800,-50)"),
    ("machine_x", "posición (simulada)", "float", "m", "Cercana al trabajador si falla o p=0.25; si no, uniforme"),
    ("machine_y", "posición (simulada)", "float", "m", "ídem"),
    ("machine_z", "posición (simulada)", "float", "m", "ídem"),
    ("distance_3d", "PREDICTOR (espacial)", "float", "m", "Distancia euclídea trabajador-máquina"),
    ("worker_speed", "PREDICTOR (cinemática)", "float", "m/s", "Normal(0.8,0.3) recortada [0,2.5]"),
    ("machine_speed", "PREDICTOR (cinemática)", "float", "m/s", "rpm/3000*15 recortada [0,15]"),
    ("relative_speed", "PREDICTOR (cinemática)", "float", "m/s", "worker_speed + machine_speed"),
    ("direction_worker", "PREDICTOR (categórica)", "int 0-7", "-", "Rumbo discretizado en 8 sectores (aleatorio)"),
    ("direction_machine", "PREDICTOR (categórica)", "int 0-7", "-", "ídem"),
    ("ttc", "PREDICTOR (espacial)", "float", "s", "distance_3d / relative_speed (300 si ≈ 0)"),
    ("in_restricted_zone", "PREDICTOR (categórica)", "bin", "-", "1 si distance_3d < 15 m"),
    ("machine_status", "PREDICTOR (telemetría máquina)", "int 0-3", "-", "Estado operacional (aleatorio, p=[.2,.5,.1,.2])"),
    ("worker_bpm", "PREDICTOR (biometría)", "float", "lpm", "Normal(85,18) recortada [55,165]"),
    ("fatigue_index", "PREDICTOR (biometría)", "float", "0-1", "Beta(2,5); proxy PERCLOS"),
    ("vibration_rms", "PREDICTOR (telemetría máquina)", "float", "m/s²", "Gamma(2,1.5) recortada [0.1,12]"),
    ("acceleration_z", "PREDICTOR (telemetría máquina)", "float", "m/s²", "Normal(9.81,1.2) recortada [6,15]"),
    ("gas_co_ppm", "PREDICTOR (ambiental)", "float", "ppm", "Exponencial(15) recortada [0,150]"),
    ("dust_density_mg_m3", "PREDICTOR (ambiental)", "float", "mg/m³", "Exponencial(2) recortada [0.1,15]"),
    ("ambient_light_lux", "PREDICTOR (ambiental)", "float", "lx", "Normal(45,15) recortada [5,120]"),
    ("risk_level", "TARGET (sintético)", "int 0-2", "-", "0=BAJO 45 %, 1=MEDIO 33 %, 2=ALTO 22 %; ver audit_label_circularity.py"),
]


def sha256_of(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def ver(name):
    try:
        return metadata.version(name)
    except metadata.PackageNotFoundError:
        return None


def main():
    # --- diccionario de variables (FON-05) -----------------------------------
    import pandas as pd
    df = pd.read_csv(fe.DATASET_PATH, nrows=5)
    cols = list(df.columns)
    listed = [c[0] for c in FEATURE_DICTIONARY]
    assert cols == listed, f"El diccionario no coincide con el CSV:\n{set(cols) ^ set(listed)}"
    fe.RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    with open(fe.RESULTS_DIR / "feature_dictionary.csv", "w", encoding="utf-8-sig", newline="") as f:
        w = csv.writer(f)
        w.writerow(["n", "variable", "rol", "tipo", "unidad", "origen_descripcion"])
        for i, row in enumerate(FEATURE_DICTIONARY, 1):
            w.writerow([i, *row])
    print(f"Diccionario de {len(listed)} variables -> results/feature_dictionary.csv")

    # --- checksum del dataset ---------------------------------------------------
    digest = sha256_of(fe.DATASET_PATH)
    rel = fe.DATASET_PATH.relative_to(ROOT).as_posix()
    (ROOT / "DATASET_CHECKSUM.sha256").write_text(f"{digest}  {rel}\n", encoding="utf-8")
    print(f"SHA-256 {digest}  {rel}")

    # --- requirements.txt con versiones exactas ---------------------------------
    lines = [
        "# Versiones EXACTAS del entorno donde se ejecutó el pipeline (generado por",
        "# backend/scripts/export_environment_metadata.py). Re-generar tras cambiar dependencias.",
        f"# Python {platform.python_version()}  |  {platform.platform()}",
        "# NOTA: el manuscrito debe citar estas versiones (no las de otro entorno).",
        "",
        "# --- Núcleo ML / estadística ---",
    ]
    missing = []
    for group, pkgs in (("", CORE), ("\n# --- Backend / servicios ---", BACKEND_PKGS)):
        if group:
            lines.append(group)
        for p in pkgs:
            v = ver(p)
            if v:
                lines.append(f"{p}=={v}")
            else:
                lines.append(f"# {p}  (no instalado en este entorno; fijar versión al instalarlo)")
                missing.append(p)
    (ROOT / "requirements.txt").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("requirements.txt escrito en la raíz (sin instalar:", ", ".join(missing) or "ninguno", ")")

    meta = {
        "date_utc": datetime.now(timezone.utc).isoformat(),
        "python": platform.python_version(), "platform": platform.platform(),
        "random_state": fe.RANDOM_STATE, "dataset": {"path": rel, "sha256": digest},
        "packages": {p: ver(p) for p in CORE + BACKEND_PKGS},
        "manuscript_declared_versions": {"python": "3.11", "xgboost": "2.1.3", "scikit-learn": "1.5.2"},
    }
    meta["manuscript_matches_environment"] = (
        meta["python"].startswith("3.11") and meta["packages"]["xgboost"] == "2.1.3"
        and meta["packages"]["scikit-learn"] == "1.5.2")
    fe.dump_json(meta, fe.RESULTS_DIR / "environment_metadata.json")
    if not meta["manuscript_matches_environment"]:
        print("\nAVISO: las versiones del entorno NO coinciden con las declaradas en el manuscrito "
              "(Python 3.11, XGBoost 2.1.3, scikit-learn 1.5.2). Actualice el artículo o reejecute en ese entorno.")


if __name__ == "__main__":
    main()
