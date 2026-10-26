"""
Protocolo de evaluación SIMÉTRICO y sin fuga de información para M-11.

Responde a los hallazgos del informe de revisión por pares G27:
  * FON-01: TODOS los modelos (y el baseline) pasan por exactamente el mismo
            procedimiento de calibración del umbral F2 (clase ALTO vs resto).
  * FON-02: SMOTENC y el escalado/codificación viven DENTRO del pipeline, por lo
            que sólo se ajustan con los datos de entrenamiento de cada pliegue.
  * Estadística: pruebas pareadas sobre las MISMAS predicciones (McNemar exacto),
            corrección de Holm, IC de Wilson, bootstrap pareado y Cliff's delta.

Protocolo (idéntico para cada modelo):
  1. Partición estratificada 80/20 (semilla 42). El 20 % de prueba no se toca.
  2. CV estratificada de 5 pliegues sobre el 80 %: SMOTENC -> preprocesado ->
     clasificador, ajustados por pliegue. Se obtienen probabilidades OOF.
  3. El umbral F2 de la clase ALTO se elige sobre las probabilidades OOF del
     entrenamiento (nunca sobre el conjunto de prueba).
  4. El modelo se reajusta con todo el 80 % y se evalúa UNA vez sobre el 20 %,
     tanto con argmax estándar como con el umbral calibrado.
"""
import json
import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestClassifier, StackingClassifier, VotingClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score, average_precision_score, f1_score, precision_score,
    recall_score, roc_auc_score,
)
from sklearn.neural_network import MLPClassifier
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.svm import SVC
from xgboost import XGBClassifier
from imblearn.over_sampling import SMOTE, SMOTENC
from imblearn.pipeline import Pipeline as ImbPipeline

if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

RANDOM_STATE = 42
HIGH_CLASS = 2  # 0=BAJO, 1=MEDIO, 2=ALTO
BETA = 2.0

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DATASET_PATH = PROJECT_ROOT / "data" / "raw" / "public_mining_equipment_dataset.csv"
ARTIFACT_DIR = PROJECT_ROOT / "backend" / "app" / "ml" / "artifacts"
# Resultados de auditoría versionados en git (reports_output/ está en .gitignore)
RESULTS_DIR = PROJECT_ROOT / "results"

FEATURES = [
    "distance_3d", "worker_speed", "machine_speed", "relative_speed",
    "direction_worker", "direction_machine", "ttc", "in_restricted_zone",
    "machine_status", "worker_bpm", "fatigue_index", "vibration_rms",
    "acceleration_z", "gas_co_ppm", "dust_density_mg_m3", "ambient_light_lux",
]
CATEGORICAL = ["direction_worker", "direction_machine", "in_restricted_zone", "machine_status"]

# Grupos funcionales usados por el estudio de ablación (FON-04)
FEATURE_GROUPS = {
    "spatial_kinematic": ["distance_3d", "worker_speed", "machine_speed", "relative_speed",
                          "direction_worker", "direction_machine", "ttc", "in_restricted_zone"],
    "machine_telemetry": ["machine_status", "vibration_rms", "acceleration_z"],
    "biometric": ["worker_bpm", "fatigue_index"],
    "environmental": ["gas_co_ppm", "dust_density_mg_m3", "ambient_light_lux"],
}

MODEL_NAMES = ["XGBoost", "RandomForest", "SVM_RBF", "MLP_NeuralNet",
               "Stacking_Ensemble", "Voting_Ensemble"]

# Regla determinista (baseline). Umbrales fijados a priori, NO ajustados al target.
BASELINE_TTC_S = 5.0


# --------------------------------------------------------------------------- #
# Datos
# --------------------------------------------------------------------------- #
def load_dataset(path=DATASET_PATH):
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(f"No se encontró el dataset oficial en {path}")
    return pd.read_csv(path)


def split_train_test(df, features=FEATURES, seed=RANDOM_STATE):
    from sklearn.model_selection import train_test_split
    X = df[features]
    y = df["risk_level"].astype(int)
    return train_test_split(X, y, test_size=0.2, stratify=y, random_state=seed)


# --------------------------------------------------------------------------- #
# Modelos y pipelines (SMOTENC anidado)
# --------------------------------------------------------------------------- #
def build_estimator(name, seed=RANDOM_STATE, use_smote=True):
    cw = None if use_smote else "balanced"  # sensibilidad "sin SMOTE"
    rf = lambda: RandomForestClassifier(n_estimators=200, max_depth=12, random_state=seed,
                                        n_jobs=-1, class_weight=cw)
    xgb = lambda: XGBClassifier(n_estimators=150, max_depth=6, learning_rate=0.1,
                                eval_metric="mlogloss", random_state=seed, n_jobs=-1)
    mlp = lambda: MLPClassifier(hidden_layer_sizes=(64, 32), max_iter=500, random_state=seed)
    if name == "XGBoost":
        return xgb()
    if name == "RandomForest":
        return rf()
    if name == "SVM_RBF":
        return SVC(kernel="rbf", C=1.0, gamma="scale", probability=True,
                   class_weight=cw, random_state=seed)
    if name == "MLP_NeuralNet":
        return mlp()
    if name == "Stacking_Ensemble":
        return StackingClassifier(
            estimators=[("rf", rf()), ("xgb", xgb())],
            final_estimator=LogisticRegression(max_iter=1000, random_state=seed), cv=3)
    if name == "Voting_Ensemble":
        return VotingClassifier(estimators=[("rf", rf()), ("xgb", xgb()), ("mlp", mlp())],
                                voting="soft")
    raise ValueError(f"Modelo desconocido: {name}")


def make_pipeline(name, features=FEATURES, use_smote=True, seed=RANDOM_STATE):
    """SMOTENC -> (StandardScaler | OneHot) -> clasificador. Todo se ajusta por pliegue."""
    cat_idx = [i for i, f in enumerate(features) if f in CATEGORICAL]
    num_idx = [i for i, f in enumerate(features) if f not in CATEGORICAL]
    transformers = []
    if num_idx:
        transformers.append(("num", StandardScaler(), num_idx))
    if cat_idx:
        transformers.append(("cat", OneHotEncoder(handle_unknown="ignore", sparse_output=False), cat_idx))
    steps = []
    if use_smote:
        if cat_idx and num_idx:
            steps.append(("smote", SMOTENC(categorical_features=cat_idx, random_state=seed)))
        else:
            steps.append(("smote", SMOTE(random_state=seed)))
    steps.append(("prep", ColumnTransformer(transformers)))
    steps.append(("clf", build_estimator(name, seed, use_smote)))
    return ImbPipeline(steps)


# --------------------------------------------------------------------------- #
# Métricas y umbral F2
# --------------------------------------------------------------------------- #
def fbeta(precision, recall, beta=BETA):
    denom = beta ** 2 * precision + recall
    return 0.0 if denom <= 0 else (1 + beta ** 2) * precision * recall / denom


def apply_threshold(proba, threshold=None):
    """argmax estándar (threshold=None) o regla 'ALTO si P(ALTO) >= umbral'."""
    if threshold is None:
        return np.argmax(proba, axis=1)
    pred = np.argmax(proba[:, :HIGH_CLASS], axis=1)
    pred[proba[:, HIGH_CLASS] >= threshold] = HIGH_CLASS
    return pred


def find_f2_threshold(y_true, p_high, grid=None, beta=BETA):
    """Umbral que maximiza F-beta de la clase ALTO. y_true: etiquetas 0/1/2 o binarias."""
    yb = (np.asarray(y_true) == HIGH_CLASS).astype(int) if np.max(y_true) > 1 else np.asarray(y_true)
    grid = np.round(np.arange(0.05, 0.951, 0.01), 2) if grid is None else grid
    best_t, best_f = 0.5, -1.0
    for t in grid:
        pred = (p_high >= t).astype(int)
        p = precision_score(yb, pred, zero_division=0)
        r = recall_score(yb, pred, zero_division=0)
        f = fbeta(p, r, beta)
        if f > best_f + 1e-12:
            best_t, best_f = float(t), float(f)
    return best_t, best_f


def alto_metrics(y_true, pred):
    yb = (np.asarray(y_true) == HIGH_CLASS).astype(int)
    pb = (np.asarray(pred) == HIGH_CLASS).astype(int)
    p = precision_score(yb, pb, zero_division=0)
    r = recall_score(yb, pb, zero_division=0)
    return {"precision_alto": float(p), "recall_alto": float(r),
            "f1_alto": float(fbeta(p, r, 1.0)), "f2_alto": float(fbeta(p, r, 2.0))}


def full_metrics(y_true, proba, threshold=None):
    y_true = np.asarray(y_true)
    pred = apply_threshold(proba, threshold)
    m = alto_metrics(y_true, pred)
    yb = (y_true == HIGH_CLASS).astype(int)
    m.update({
        "accuracy": float(accuracy_score(y_true, pred)),
        "f1_macro": float(f1_score(y_true, pred, average="macro")),
        "auc_roc_ovr": float(roc_auc_score(y_true, proba, multi_class="ovr")),
        "auc_roc_alto": float(roc_auc_score(yb, proba[:, HIGH_CLASS])),
        "auc_pr_alto": float(average_precision_score(yb, proba[:, HIGH_CLASS])),
        "threshold": None if threshold is None else float(threshold),
    })
    return m


# --------------------------------------------------------------------------- #
# Validación cruzada con probabilidades OOF
# --------------------------------------------------------------------------- #
def oof_evaluate(name, X, y, skf, features=FEATURES, use_smote=True, seed=RANDOM_STATE):
    """CV estratificada; SMOTENC/escalado se ajustan DENTRO de cada pliegue."""
    X = np.asarray(X, dtype=float)
    y = np.asarray(y)
    oof = np.zeros((len(y), 3))
    folds = []
    for fold, (tr, va) in enumerate(skf.split(X, y), 1):
        pipe = make_pipeline(name, features, use_smote, seed)
        pipe.fit(X[tr], y[tr])
        t0 = time.perf_counter()
        proba = pipe.predict_proba(X[va])
        t1 = time.perf_counter()
        oof[va] = proba
        pred = np.argmax(proba, axis=1)
        row = {
            "fold": fold,
            "accuracy": float(accuracy_score(y[va], pred)),
            "f1_macro": float(f1_score(y[va], pred, average="macro")),
            "f1_micro": float(f1_score(y[va], pred, average="micro")),
            "precision_macro": float(precision_score(y[va], pred, average="macro", zero_division=0)),
            "recall_macro": float(recall_score(y[va], pred, average="macro", zero_division=0)),
            "auc_roc": float(roc_auc_score(y[va], proba, multi_class="ovr")),
            "inference_time_ms": float((t1 - t0) / len(va) * 1000.0),
        }
        row.update({k + "_argmax": v for k, v in alto_metrics(y[va], pred).items()})
        folds.append(row)
    return oof, folds


def fit_predict_proba(name, X_train, y_train, X_test, features=FEATURES, use_smote=True,
                      seed=RANDOM_STATE):
    pipe = make_pipeline(name, features, use_smote, seed)
    pipe.fit(np.asarray(X_train, dtype=float), np.asarray(y_train))
    t0 = time.perf_counter()
    proba = pipe.predict_proba(np.asarray(X_test, dtype=float))
    ms = (time.perf_counter() - t0) / len(X_test) * 1000.0
    return proba, float(ms), pipe


# --------------------------------------------------------------------------- #
# Baseline determinista (regla de seguridad, umbrales fijados a priori)
# --------------------------------------------------------------------------- #
def baseline_predict(X, ttc_threshold=BASELINE_TTC_S):
    """ALTO si TTC < umbral o el trabajador está en zona restringida. Devuelve 0/2."""
    X = X if isinstance(X, pd.DataFrame) else pd.DataFrame(X, columns=FEATURES)
    flag = (X["ttc"].values < ttc_threshold) | (X["in_restricted_zone"].values == 1)
    return np.where(flag, HIGH_CLASS, 0)


def tune_baseline_ttc(X_train, y_train, grid=None):
    """Baseline 'justo': mismo criterio F2 y mismos datos de entrenamiento que los modelos."""
    grid = np.round(np.arange(1.0, 120.0, 1.0), 1) if grid is None else grid
    yb = (np.asarray(y_train) == HIGH_CLASS).astype(int)
    best_t, best_f = BASELINE_TTC_S, -1.0
    for t in grid:
        pb = (baseline_predict(X_train, t) == HIGH_CLASS).astype(int)
        f = fbeta(precision_score(yb, pb, zero_division=0), recall_score(yb, pb, zero_division=0))
        if f > best_f:
            best_t, best_f = float(t), float(f)
    return best_t, best_f


# --------------------------------------------------------------------------- #
# Estadística: Wilson, bootstrap pareado, McNemar, Holm, Cliff
# --------------------------------------------------------------------------- #
def wilson_ci(successes, n, z=1.959964):
    if n == 0:
        return [float("nan"), float("nan")]
    p = successes / n
    denom = 1 + z ** 2 / n
    centre = (p + z ** 2 / (2 * n)) / denom
    half = z * np.sqrt(p * (1 - p) / n + z ** 2 / (4 * n ** 2)) / denom
    return [float(centre - half), float(centre + half)]


def bootstrap_indices(n, n_boot=1000, seed=RANDOM_STATE):
    rng = np.random.default_rng(seed)
    return rng.integers(0, n, size=(n_boot, n))


def bootstrap_binary_metrics(y_true, pred, idx):
    """Precisión/recall/F2 de ALTO sobre cada remuestreo (mismos índices para todos)."""
    yb = (np.asarray(y_true) == HIGH_CLASS)
    pb = (np.asarray(pred) == HIGH_CLASS)
    yb_s, pb_s = yb[idx], pb[idx]
    tp = (yb_s & pb_s).sum(axis=1).astype(float)
    fp = (~yb_s & pb_s).sum(axis=1).astype(float)
    fn = (yb_s & ~pb_s).sum(axis=1).astype(float)
    prec = np.divide(tp, tp + fp, out=np.zeros_like(tp), where=(tp + fp) > 0)
    rec = np.divide(tp, tp + fn, out=np.zeros_like(tp), where=(tp + fn) > 0)
    denom = BETA ** 2 * prec + rec
    f2 = np.divide((1 + BETA ** 2) * prec * rec, denom, out=np.zeros_like(prec), where=denom > 0)
    return {"precision": prec, "recall": rec, "f2": f2}


def percentile_ci(values, alpha=0.05):
    return [float(np.percentile(values, 100 * alpha / 2)), float(np.percentile(values, 100 * (1 - alpha / 2)))]


def bootstrap_auc(y_bin, score, idx, max_boot=1000):
    out = []
    for row in idx[:max_boot]:
        yb = y_bin[row]
        if yb.min() == yb.max():
            continue
        out.append(roc_auc_score(yb, score[row]))
    return np.asarray(out)


def mcnemar_exact(correct_a, correct_b):
    """Prueba pareada exacta sobre las MISMAS muestras. Devuelve b, c, p."""
    a, b_ = np.asarray(correct_a, bool), np.asarray(correct_b, bool)
    b = int((a & ~b_).sum())   # A acierta, B falla
    c = int((~a & b_).sum())   # A falla, B acierta
    n = b + c
    p = 1.0 if n == 0 else float(stats.binomtest(min(b, c), n, 0.5).pvalue)
    return b, c, p


def holm_adjust(pvalues):
    p = np.asarray(pvalues, float)
    m = len(p)
    order = np.argsort(p)
    adj = np.empty(m)
    running = 0.0
    for rank, i in enumerate(order):
        running = max(running, (m - rank) * p[i])
        adj[i] = min(1.0, running)
    return adj.tolist()


def cliffs_delta(a, b):
    a, b = np.asarray(a), np.asarray(b)
    u = stats.mannwhitneyu(a, b, alternative="two-sided").statistic
    return float(2.0 * u / (len(a) * len(b)) - 1.0)


def cliffs_label(d):
    d = abs(d)
    return "despreciable" if d < 0.147 else "pequeño" if d < 0.33 else "mediano" if d < 0.474 else "grande"


def compare_to_reference(y_true, preds, reference, idx):
    """Compara cada sistema contra `reference` con pruebas pareadas + Holm.

    preds: dict nombre -> predicciones (0/1/2) sobre el MISMO conjunto de prueba.
    """
    y_true = np.asarray(y_true)
    yb = (y_true == HIGH_CLASS)
    ref_pb = preds[reference] == HIGH_CLASS
    ref_boot = bootstrap_binary_metrics(y_true, preds[reference], idx)
    rows, p_recall, p_decision = {}, [], []
    names = [n for n in preds if n != reference]
    for n in names:
        pb = preds[n] == HIGH_CLASS
        # (a) recall: sólo casos realmente ALTO, ¿cada sistema lo detecta?
        b_r, c_r, p_r = mcnemar_exact(ref_pb[yb], pb[yb])
        # (b) decisión global sobre ALTO (acierto = predicción coincide con realidad)
        b_d, c_d, p_d = mcnemar_exact(ref_pb == yb, pb == yb)
        boot = bootstrap_binary_metrics(y_true, preds[n], idx)
        d_f2 = ref_boot["f2"] - boot["f2"]
        d_rec = ref_boot["recall"] - boot["recall"]
        d_prec = ref_boot["precision"] - boot["precision"]
        cd = cliffs_delta(ref_boot["f2"], boot["f2"])
        rows[n] = {
            "delta_f2_ref_minus_other": {"mean": float(d_f2.mean()), "ci95": percentile_ci(d_f2)},
            "delta_recall_ref_minus_other": {"mean": float(d_rec.mean()), "ci95": percentile_ci(d_rec)},
            "delta_precision_ref_minus_other": {"mean": float(d_prec.mean()), "ci95": percentile_ci(d_prec)},
            "mcnemar_recall": {"ref_only_detects": b_r, "other_only_detects": c_r, "p": p_r},
            "mcnemar_decision": {"ref_only_correct": b_d, "other_only_correct": c_d, "p": p_d},
            "cliffs_delta_f2_bootstrap": cd,
            "cliffs_delta_label": cliffs_label(cd),
        }
        p_recall.append(p_r)
        p_decision.append(p_d)
    for n, a in zip(names, holm_adjust(p_recall)):
        rows[n]["mcnemar_recall"]["p_holm"] = a
    for n, a in zip(names, holm_adjust(p_decision)):
        rows[n]["mcnemar_decision"]["p_holm"] = a
    return rows


def to_jsonable(obj):
    if isinstance(obj, dict):
        return {str(k): to_jsonable(v) for k, v in obj.items()}
    if isinstance(obj, (list, tuple)):
        return [to_jsonable(v) for v in obj]
    if isinstance(obj, np.ndarray):
        return to_jsonable(obj.tolist())
    if isinstance(obj, (np.floating,)):
        return None if np.isnan(obj) else float(obj)
    if isinstance(obj, (np.integer,)):
        return int(obj)
    if isinstance(obj, (np.bool_,)):
        return bool(obj)
    if isinstance(obj, float) and np.isnan(obj):
        return None
    return obj


def dump_json(obj, path):
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(to_jsonable(obj), f, indent=2, ensure_ascii=False)
