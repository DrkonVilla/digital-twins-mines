"""
Entrenamiento y evaluación de M-11 con protocolo SIMÉTRICO (ver fair_eval.py).

Corrige los hallazgos FON-01 (umbral asimétrico) y FON-02 (SMOTE/escalado dentro
de cada pliegue) del informe de revisión por pares G27:

  * XGBoost, RandomForest, SVM-RBF, MLP, Stacking y Voting se calibran con el MISMO
    criterio (max F2 de la clase ALTO sobre probabilidades OOF del entrenamiento).
  * El baseline determinista de TTC se evalúa con la misma partición y el mismo
    bootstrap pareado; además se reporta una versión "ajustada" con el mismo criterio F2.
  * SMOTENC + escalado/one-hot se ajustan sólo con el entrenamiento de cada pliegue.
  * Análisis de sensibilidad SIN SMOTE (class_weight='balanced' donde aplica).
  * Se exportan curvas PR, sensibilidad al umbral y comparaciones pareadas (McNemar + Holm).

Salidas (backend/app/ml/artifacts):
  cv_metrics_results.json        -> formato histórico {modelo: [métricas por fold]} (usado por el dashboard)
  fair_comparison_results.json   -> resultados completos del protocolo simétrico
  pr_curves_symmetric.png        -> curvas Precision-Recall de todos los modelos
  processed_data.joblib          -> partición train/test
"""
import argparse
import os
import sys
import time

import joblib
import numpy as np
import pandas as pd
from sklearn.metrics import precision_recall_curve
from sklearn.model_selection import StratifiedKFold

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import fair_eval as fe  # noqa: E402

N_BOOT = 1000
THRESHOLD_GRID = [round(t, 2) for t in np.arange(0.10, 0.901, 0.05)]


def _bootstrap_summary(y_test, pred, proba, idx):
    boot = fe.bootstrap_binary_metrics(y_test, pred, idx)
    yb = (np.asarray(y_test) == fe.HIGH_CLASS).astype(int)
    out = {k: {"mean": float(v.mean()), "ci95": fe.percentile_ci(v)} for k, v in boot.items()}
    if proba is not None:
        auc = fe.bootstrap_auc(yb, proba[:, fe.HIGH_CLASS], idx)
        out["auc_roc_alto"] = {"mean": float(auc.mean()), "ci95": fe.percentile_ci(auc)}
    return out


def _wilson_block(y_test, pred):
    yb = np.asarray(y_test) == fe.HIGH_CLASS
    pb = np.asarray(pred) == fe.HIGH_CLASS
    tp, fp, fn = int((yb & pb).sum()), int((~yb & pb).sum()), int((yb & ~pb).sum())
    return {
        "recall_alto_wilson95": fe.wilson_ci(tp, tp + fn),
        "precision_alto_wilson95": fe.wilson_ci(tp, tp + fp),
        "tp": tp, "fp": fp, "fn": fn, "n_alto": int(yb.sum()), "n_test": int(len(yb)),
    }


def evaluate_model(name, X_train, y_train, X_test, y_test, skf, idx, use_smote=True):
    t0 = time.perf_counter()
    oof, folds = fe.oof_evaluate(name, X_train, y_train, skf, use_smote=use_smote)
    thr, oof_f2 = fe.find_f2_threshold(y_train, oof[:, fe.HIGH_CLASS])
    proba, inf_ms, _ = fe.fit_predict_proba(name, X_train, y_train, X_test, use_smote=use_smote)

    pred_argmax = fe.apply_threshold(proba, None)
    pred_cal = fe.apply_threshold(proba, thr)
    yb = (np.asarray(y_test) == fe.HIGH_CLASS).astype(int)
    sens = []
    for t in THRESHOLD_GRID:
        m = fe.alto_metrics(y_test, fe.apply_threshold(proba, t))
        sens.append({"threshold": t, **m})
    prec, rec, _ = precision_recall_curve(yb, proba[:, fe.HIGH_CLASS])

    result = {
        "use_smote": use_smote,
        "cv_folds": folds,
        "calibration": {"criterion": "max F2 (ALTO vs resto) sobre probabilidades OOF del entrenamiento",
                        "threshold_alto": thr, "oof_f2_alto": oof_f2},
        "test_argmax": fe.full_metrics(y_test, proba, None),
        "test_calibrated": fe.full_metrics(y_test, proba, thr),
        "bootstrap_calibrated": _bootstrap_summary(y_test, pred_cal, proba, idx),
        "bootstrap_argmax": _bootstrap_summary(y_test, pred_argmax, proba, idx),
        "wilson_calibrated": _wilson_block(y_test, pred_cal),
        "threshold_sensitivity_test": sens,
        "inference_time_ms_per_sample": inf_ms,
        "elapsed_s": round(time.perf_counter() - t0, 1),
    }
    return result, proba, pred_argmax, pred_cal, (prec, rec)


def _baseline_block(X_train, y_train, X_test, y_test, idx):
    fixed_pred = fe.baseline_predict(X_test, fe.BASELINE_TTC_S)
    t_tuned, f2_tuned = fe.tune_baseline_ttc(X_train, y_train)
    tuned_pred = fe.baseline_predict(X_test, t_tuned)
    block = {}
    for key, pred, desc in [
        ("Baseline_TTC_fixed", fixed_pred,
         f"ALTO si TTC < {fe.BASELINE_TTC_S} s o zona restringida (umbrales fijados a priori)"),
        ("Baseline_TTC_tuned", tuned_pred,
         f"Mismo regla con TTC={t_tuned:.0f} s elegido por F2 sobre el entrenamiento (criterio idéntico a los modelos)"),
    ]:
        block[key] = {
            "description": desc,
            "test": fe.alto_metrics(y_test, pred),
            "bootstrap": _bootstrap_summary(y_test, pred, None, idx),
            "wilson": _wilson_block(y_test, pred),
        }
    block["Baseline_TTC_tuned"]["ttc_threshold_s"] = t_tuned
    block["Baseline_TTC_tuned"]["train_f2"] = f2_tuned
    return block, {"Baseline_TTC_fixed": fixed_pred, "Baseline_TTC_tuned": tuned_pred}


def _plot_pr(curves, positives_rate, path):
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
    except Exception:
        return
    plt.figure(figsize=(8, 6), dpi=200)
    for name, (prec, rec) in curves.items():
        plt.plot(rec, prec, label=name, linewidth=1.6)
    plt.axhline(positives_rate, color="gray", linestyle="--", linewidth=1, label="Azar (prevalencia ALTO)")
    plt.xlabel("Recall (ALTO)")
    plt.ylabel("Precisión (ALTO)")
    plt.title("Curvas Precision-Recall de la clase ALTO (conjunto de prueba, protocolo simétrico)")
    plt.legend(fontsize=8)
    plt.grid(alpha=0.3)
    plt.tight_layout()
    plt.savefig(path)
    plt.close()


def train_and_evaluate_cv(models=None, run_sensitivity=True, n_boot=N_BOOT):
    print("=" * 72)
    print("FASE 1-2: Protocolo simétrico (SMOTENC por fold + umbral F2 idéntico)")
    print("=" * 72)
    models = models or fe.MODEL_NAMES
    df = fe.load_dataset()
    print(f"Dataset: {fe.DATASET_PATH}  ({len(df)} filas)")

    X_train, X_test, y_train, y_test = fe.split_train_test(df)
    skf = StratifiedKFold(n_splits=5, shuffle=True, random_state=fe.RANDOM_STATE)
    idx = fe.bootstrap_indices(len(y_test), n_boot)

    results, preds_cal, preds_arg, curves = {}, {}, {}, {}
    for name in models:
        print(f"\n>> {name} (con SMOTENC)...", flush=True)
        res, proba, p_arg, p_cal, curve = evaluate_model(name, X_train, y_train, X_test, y_test, skf, idx, True)
        results[name] = res
        preds_cal[name], preds_arg[name], curves[name] = p_cal, p_arg, curve
        c, a = res["test_calibrated"], res["test_argmax"]
        print(f"   umbral F2={res['calibration']['threshold_alto']:.2f} | "
              f"calibrado: P={c['precision_alto']:.3f} R={c['recall_alto']:.3f} F2={c['f2_alto']:.3f} AUC={c['auc_roc_alto']:.3f} | "
              f"argmax: P={a['precision_alto']:.3f} R={a['recall_alto']:.3f} F2={a['f2_alto']:.3f} ({res['elapsed_s']}s)")

    baselines, base_preds = _baseline_block(X_train, y_train, X_test, y_test, idx)
    for k, v in baselines.items():
        t = v["test"]
        print(f"\n>> {k}: P={t['precision_alto']:.3f} R={t['recall_alto']:.3f} F2={t['f2_alto']:.3f}")
    preds_cal.update(base_preds)
    preds_arg.update(base_preds)

    reference = "XGBoost" if "XGBoost" in models else models[0]
    comparisons = {
        "reference": reference,
        "calibrated": fe.compare_to_reference(y_test, preds_cal, reference, idx),
        "argmax": fe.compare_to_reference(y_test, preds_arg, reference, idx),
    }

    sensitivity = {}
    if run_sensitivity:
        print("\n" + "-" * 72 + "\nSensibilidad: SIN SMOTE (class_weight='balanced' donde aplica)\n" + "-" * 72)
        for name in models:
            print(f">> {name} (sin SMOTE)...", flush=True)
            res, *_ = evaluate_model(name, X_train, y_train, X_test, y_test, skf, idx, False)
            sensitivity[name] = {
                "threshold_alto": res["calibration"]["threshold_alto"],
                "test_calibrated": res["test_calibrated"],
                "test_argmax": res["test_argmax"],
            }
            c = res["test_calibrated"]
            print(f"   P={c['precision_alto']:.3f} R={c['recall_alto']:.3f} F2={c['f2_alto']:.3f}")

    # --- Archivos de salida ---------------------------------------------------
    fe.ARTIFACT_DIR.mkdir(parents=True, exist_ok=True)
    cv_legacy = {n: r["cv_folds"] for n, r in results.items()}
    fe.dump_json(cv_legacy, fe.ARTIFACT_DIR / "cv_metrics_results.json")

    report = {
        "protocol": {
            "split": "estratificada 80/20, semilla 42",
            "cv": "StratifiedKFold(5, shuffle, 42) sobre el 80 % de entrenamiento",
            "resampling": "SMOTENC dentro del pipeline (se ajusta sólo con el entrenamiento de cada pliegue)",
            "threshold": "max F2 (ALTO vs resto) sobre probabilidades OOF del entrenamiento; mismo procedimiento para TODOS los modelos",
            "test": "el 20 % de prueba se usa una sola vez; sin ajuste de umbral ni de hiperparámetros sobre él",
            "bootstrap": f"{n_boot} remuestreos pareados (mismos índices para todos los sistemas)",
            "paired_tests": "McNemar exacto (mismas muestras) + corrección de Holm; Cliff's delta sobre el bootstrap",
            "n_train": int(len(y_train)), "n_test": int(len(y_test)),
            "prevalence_alto_test": float((y_test == fe.HIGH_CLASS).mean()),
            "label_note": "risk_level es un target sintético heurístico; ver audit_label_circularity.py (FON-03)",
        },
        "models": results,
        "baselines": baselines,
        "paired_comparisons": comparisons,
        "sensitivity_no_smote": sensitivity,
    }
    fe.dump_json(report, fe.ARTIFACT_DIR / "fair_comparison_results.json")
    _plot_pr(curves, float((y_test == fe.HIGH_CLASS).mean()), fe.ARTIFACT_DIR / "pr_curves_symmetric.png")
    joblib.dump({"X_train": X_train, "X_test": X_test, "y_train": y_train, "y_test": y_test,
                 "feature_names": fe.FEATURES}, fe.ARTIFACT_DIR / "processed_data.joblib")

    print("\nArtefactos escritos en:", fe.ARTIFACT_DIR)
    return cv_legacy


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--no-sensitivity", action="store_true", help="omitir la corrida sin SMOTE")
    ap.add_argument("--models", nargs="*", default=None, help="subconjunto de modelos")
    ap.add_argument("--n-boot", type=int, default=N_BOOT)
    a = ap.parse_args()
    train_and_evaluate_cv(a.models, not a.no_sensitivity, a.n_boot)
