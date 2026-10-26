"""
Estudio de ablación multimodal formal (FON-04).

Cada configuración usa EXACTAMENTE el mismo protocolo (fair_eval.py): misma partición,
mismos pliegues, SMOTENC anidado, umbral F2 elegido sobre OOF del entrenamiento y
bootstrap PAREADO (mismos índices) contra el modelo completo.

Se separa explícitamente el cambio absoluto (puntos porcentuales) del relativo (%)
para cada métrica (precisión, recall, F2, AUC), de modo que no se confunda una caída
de precisión con una caída de F2 (inconsistencia detectada en la Tabla 6 del manuscrito).

Salida (versionada en git): results/ablation_study_results.json
"""
import argparse
import os
import sys
import time

import numpy as np
from sklearn.model_selection import StratifiedKFold

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import fair_eval as fe  # noqa: E402

G = fe.FEATURE_GROUPS
ALL = fe.FEATURES


def _without(cols):
    return [f for f in ALL if f not in cols]


CONFIGS = {
    "A_full": {
        "label": "Modelo completo (16 variables)", "features": ALL},
    "B_no_distance3d": {
        "label": "Sin distance_3d (resto intacto)", "features": _without(["distance_3d"])},
    "B2_no_distance_ttc_relspeed": {
        "label": "Sin distance_3d, ttc ni relative_speed", "features": _without(["distance_3d", "ttc", "relative_speed"])},
    "C_spatial_only": {
        "label": "Sólo espacial/cinemática", "features": G["spatial_kinematic"]},
    "D_no_biometric": {
        "label": "Sin biometría (BPM, fatiga)", "features": _without(G["biometric"])},
    "E_no_environmental": {
        "label": "Sin ambiental (CO, polvo, luz)", "features": _without(G["environmental"])},
    "F_no_machine_telemetry": {
        "label": "Sin telemetría de máquina (estado, vibración, acel. Z)", "features": _without(G["machine_telemetry"])},
    "G_no_spatial": {
        "label": "Sin espacial/cinemática (sólo biometría + ambiente + máquina)",
        "features": _without(G["spatial_kinematic"])},
}


def _delta(new, ref):
    """Cambio absoluto (pp, en escala 0-100) y relativo (%) frente a la referencia."""
    return {
        "absolute_pp": float((new - ref) * 100.0),
        "relative_pct": float((new - ref) / ref * 100.0) if ref else None,
    }


def run_ablation(model="XGBoost", n_boot=1000, only=None):
    print("=" * 72)
    print(f"ESTUDIO DE ABLACIÓN (modelo: {model}, protocolo simétrico)")
    print("=" * 72)
    df = fe.load_dataset()
    X_train_all, X_test_all, y_train, y_test = fe.split_train_test(df, ALL)
    skf = StratifiedKFold(n_splits=5, shuffle=True, random_state=fe.RANDOM_STATE)
    idx = fe.bootstrap_indices(len(y_test), n_boot)
    truth_alto = (y_test.values == fe.HIGH_CLASS)

    cache, full_boot, full_pred, full_proba = {}, None, None, None
    configs = {k: v for k, v in CONFIGS.items() if not only or k in only or k == "A_full"}
    for key, cfg in configs.items():
        feats = cfg["features"]
        t0 = time.perf_counter()
        Xtr, Xte = X_train_all[feats], X_test_all[feats]
        oof, folds = fe.oof_evaluate(model, Xtr, y_train, skf, features=feats)
        thr, _ = fe.find_f2_threshold(y_train, oof[:, fe.HIGH_CLASS])
        proba, _, _ = fe.fit_predict_proba(model, Xtr, y_train, Xte, features=feats)
        pred = fe.apply_threshold(proba, thr)
        m = fe.full_metrics(y_test, proba, thr)
        boot = fe.bootstrap_binary_metrics(y_test, pred, idx)
        cache[key] = {"cfg": cfg, "metrics": m, "threshold": thr, "boot": boot, "pred": pred,
                      "cv_f1_macro": float(np.mean([f["f1_macro"] for f in folds]))}
        if key == "A_full":
            full_boot, full_pred = boot, pred
        print(f">> {key:<30} n_feat={len(feats):<2} thr={thr:.2f} P={m['precision_alto']:.3f} "
              f"R={m['recall_alto']:.3f} F2={m['f2_alto']:.3f} AUC={m['auc_roc_alto']:.3f} "
              f"({time.perf_counter() - t0:.0f}s)", flush=True)

    ref = cache["A_full"]["metrics"]
    out = {"model": model, "protocol": "idéntico a train_cv.py; bootstrap pareado vs A_full", "configs": {}}
    for key, c in cache.items():
        m = c["metrics"]
        d_boot_f2 = full_boot["f2"] - c["boot"]["f2"]
        out["configs"][key] = {
            "label": c["cfg"]["label"],
            "features": c["cfg"]["features"],
            "n_features": len(c["cfg"]["features"]),
            "threshold_alto": c["threshold"],
            "metrics": {k: m[k] for k in ("precision_alto", "recall_alto", "f1_alto", "f2_alto",
                                          "auc_roc_alto", "auc_pr_alto", "f1_macro", "accuracy")},
            "bootstrap_ci95": {k: fe.percentile_ci(v) for k, v in c["boot"].items()},
            "delta_vs_full": None if key == "A_full" else {
                "precision": _delta(m["precision_alto"], ref["precision_alto"]),
                "recall": _delta(m["recall_alto"], ref["recall_alto"]),
                "f2": _delta(m["f2_alto"], ref["f2_alto"]),
                "auc_roc": _delta(m["auc_roc_alto"], ref["auc_roc_alto"]),
            },
            "paired_bootstrap_f2_full_minus_config": None if key == "A_full" else {
                "mean": float(d_boot_f2.mean()), "ci95": fe.percentile_ci(d_boot_f2),
                "ci_excludes_zero": bool(not (fe.percentile_ci(d_boot_f2)[0] <= 0 <= fe.percentile_ci(d_boot_f2)[1])),
                "cliffs_delta": fe.cliffs_delta(full_boot["f2"], c["boot"]["f2"]),
            },
            "mcnemar_decision_vs_full": None if key == "A_full" else dict(zip(
                ("full_only_correct", "config_only_correct", "p"),
                fe.mcnemar_exact((full_pred == fe.HIGH_CLASS) == truth_alto,
                                 (c["pred"] == fe.HIGH_CLASS) == truth_alto))),
        }

    # Interpretación automática: ¿cada grupo aporta de verdad?
    notes = []
    for key, c in out["configs"].items():
        d = c["delta_vs_full"]
        if not d:
            continue
        ci = c["paired_bootstrap_f2_full_minus_config"]
        if d["f2"]["absolute_pp"] > 0:
            notes.append(f"{key}: F2 SUBE {d['f2']['absolute_pp']:+.2f} pp al quitar estas variables "
                         f"(IC95 de Δ=full−config: {ci['ci95'][0]:+.4f}..{ci['ci95'][1]:+.4f}); "
                         f"no hay evidencia de que aporten a F2.")
        elif ci["ci_excludes_zero"]:
            notes.append(f"{key}: F2 baja {abs(d['f2']['absolute_pp']):.2f} pp y el IC95 pareado excluye 0 (aporte real).")
        else:
            notes.append(f"{key}: F2 baja {abs(d['f2']['absolute_pp']):.2f} pp pero el IC95 pareado incluye 0 (aporte no concluyente).")
    out["interpretation"] = notes
    out["warning"] = ("Con un target sintético generado por una función de utilidad, la ablación mide qué "
                      "variables usa la función generadora y cuán ruidosa es; no es evidencia de campo.")

    fe.dump_json(out, fe.RESULTS_DIR / "ablation_study_results.json")
    print("\nInterpretación:")
    for n in notes:
        print("  -", n)
    print("\nResultados guardados en results/ablation_study_results.json")
    return out


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--model", default="XGBoost")
    ap.add_argument("--n-boot", type=int, default=1000)
    ap.add_argument("--only", nargs="*", default=None)
    a = ap.parse_args()
    run_ablation(a.model, a.n_boot, a.only)
