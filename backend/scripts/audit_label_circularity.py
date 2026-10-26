"""
Auditoría de circularidad de la etiqueta `risk_level` (FON-03).

Pregunta del revisor: la etiqueta se construye con TTC, distancia y zona restringida
(spatial_risk), que son las mismas variables que usa el baseline determinista. ¿Qué mide
realmente la comparación ML vs baseline?

Este script NO regenera el dataset (el target oficial permanece intacto). Reconstruye
las componentes deterministas de la función generadora a partir del propio CSV y
cuantifica:

  1. Descomposición de la varianza del score: espacial vs multimodal vs ruido.
  2. Concordancia (kappa de Cohen, accuracy, F2) entre la regla del baseline y la etiqueta.
  3. Techo de Bayes: el mejor F2 posible para ALTO dado el score determinista y el ruido
     declarado. Si un modelo se acerca a ese techo, sólo está reproduciendo la función generadora.
  4. Sensibilidad al nivel de ruido del generador (σ = 1,9 / 3,8 / 7,6).
  5. Etiquetas ALTERNATIVAS (sólo-multimodal y sólo-espacial) para mostrar que la ventaja
     relativa ML vs baseline depende de qué variables genera la etiqueta.

Salida (versionada en git): results/label_circularity_audit.json
"""
import os
import sys

import numpy as np
import pandas as pd
from scipy import stats
from sklearn.metrics import cohen_kappa_score
from sklearn.model_selection import StratifiedKFold, train_test_split

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import fair_eval as fe  # noqa: E402

NOISE_SD = 3.8           # declarado en download_and_process_public_dataset.py
P_LOW, P_HIGH = 45, 78   # percentiles que definen BAJO/MEDIO/ALTO (45 / 33 / 22 %)


def spatial_component(df):
    return ((12.0 / np.maximum(df["distance_3d"], 0.8)) * 2.0
            + (8.0 / np.maximum(df["ttc"], 0.5)) * 1.8
            + df["in_restricted_zone"] * 2.0).values


def multimodal_component(df):
    return (df["fatigue_index"] * 1.8
            + (np.maximum(df["worker_bpm"] - 60, 0) / 50.0) * 1.0
            + (df["gas_co_ppm"] / 40.0) * 1.0
            + (df["dust_density_mg_m3"] / 5.0) * 0.6
            - (df["ambient_light_lux"] / 120.0) * 0.5).values


def bayes_ceiling_f2(det, cut_high, sigma):
    """Mejor F2 esperado de ALTO conociendo sólo el score determinista (techo de Bayes)."""
    p = 1.0 - stats.norm.cdf((cut_high - det) / sigma)
    order = np.argsort(-p)
    tp = np.cumsum(p[order])
    k = np.arange(1, len(p) + 1)
    pos = p.sum()
    fp, fn = k - tp, pos - tp
    f2 = 5 * tp / np.maximum(5 * tp + 4 * fn + fp, 1e-12)
    j = int(np.argmax(f2))
    return {"f2": float(f2[j]), "precision": float(tp[j] / k[j]), "recall": float(tp[j] / pos),
            "n_flagged": int(k[j])}


def expected_cuts(det, sigma, draws=30, seed=0):
    rng = np.random.default_rng(seed)
    lo, hi = [], []
    for _ in range(draws):
        s = det + rng.normal(0, sigma, len(det))
        a, b = np.percentile(s, [P_LOW, P_HIGH])
        lo.append(a)
        hi.append(b)
    return float(np.mean(lo)), float(np.mean(hi))


def labels_from_score(score):
    a, b = np.percentile(score, [P_LOW, P_HIGH])
    y = np.zeros(len(score), dtype=int)
    y[score >= a] = 1
    y[score >= b] = 2
    return y


def evaluate_on_label(df, y, tag, features=fe.FEATURES):
    """XGBoost simétrico (OOF 3 pliegues + umbral F2) vs baseline justo sobre una etiqueta dada."""
    X = df[features]
    Xtr, Xte, ytr, yte = train_test_split(X, y, test_size=0.2, stratify=y, random_state=fe.RANDOM_STATE)
    skf = StratifiedKFold(n_splits=3, shuffle=True, random_state=fe.RANDOM_STATE)
    oof, _ = fe.oof_evaluate("XGBoost", Xtr, ytr, skf, features=features)
    thr, _ = fe.find_f2_threshold(ytr, oof[:, fe.HIGH_CLASS])
    proba, _, _ = fe.fit_predict_proba("XGBoost", Xtr, ytr, Xte, features=features)
    ml = fe.alto_metrics(yte, fe.apply_threshold(proba, thr))
    fixed = fe.alto_metrics(yte, fe.baseline_predict(Xte, fe.BASELINE_TTC_S))
    t_b, _ = fe.tune_baseline_ttc(Xtr, ytr)
    tuned = fe.alto_metrics(yte, fe.baseline_predict(Xte, t_b))
    print(f"   [{tag}] XGB F2={ml['f2_alto']:.3f} | baseline fijo F2={fixed['f2_alto']:.3f} | "
          f"baseline ajustado F2={tuned['f2_alto']:.3f}", flush=True)
    return {"xgboost_calibrated": ml, "baseline_fixed": fixed,
            "baseline_tuned": {**tuned, "ttc_threshold_s": t_b},
            "xgb_minus_baseline_tuned_f2_pp": float((ml["f2_alto"] - tuned["f2_alto"]) * 100)}


def run_audit(run_alt_labels=True):
    print("=" * 72 + "\nAUDITORÍA DE CIRCULARIDAD DE LA ETIQUETA (FON-03)\n" + "=" * 72)
    df = fe.load_dataset()
    y = df["risk_level"].astype(int).values
    spatial, multimodal = spatial_component(df), multimodal_component(df)
    det = spatial + multimodal
    var_sp, var_mm, var_noise = spatial.var(), multimodal.var(), NOISE_SD ** 2
    cov = 2 * np.cov(spatial, multimodal)[0, 1]
    total = var_sp + var_mm + cov + var_noise

    out = {
        "generator": {
            "source": "backend/scripts/download_and_process_public_dataset.py (sección 5)",
            "formula": "risk_score = spatial_risk + multimodal_risk + N(0, 3.8); BAJO<p45<=MEDIO<p78<=ALTO",
            "spatial_risk": "(12/max(d,0.8))*2.0 + (8/max(ttc,0.5))*1.8 + in_restricted_zone*2.0",
            "multimodal_risk": "1.8*fatiga + (max(bpm-60,0)/50) + CO/40 + 0.6*polvo/5 - 0.5*luz/120",
            "baseline_inputs": ["ttc", "in_restricted_zone"],
            "shared_variables_with_label": ["distance_3d", "ttc", "in_restricted_zone"],
        },
        "variance_decomposition": {
            "spatial_share": float(var_sp / total), "multimodal_share": float(var_mm / total),
            "covariance_share": float(cov / total), "noise_share": float(var_noise / total),
        },
    }
    print("Varianza del score -> espacial {:.1%} | multimodal {:.1%} | ruido {:.1%}".format(
        var_sp / total, var_mm / total, var_noise / total))

    # --- 2. Concordancia baseline vs etiqueta ----------------------------------
    yb = (y == fe.HIGH_CLASS).astype(int)
    conc = {}
    for label, pred in [("baseline_fixed", fe.baseline_predict(df, fe.BASELINE_TTC_S)),
                        ("baseline_tuned_full_data", None)]:
        if pred is None:
            t_b, _ = fe.tune_baseline_ttc(df, y)
            pred = fe.baseline_predict(df, t_b)
        pb = (pred == fe.HIGH_CLASS).astype(int)
        conc[label] = {
            "kappa_alto_vs_resto": float(cohen_kappa_score(yb, pb)),
            "accuracy_alto_vs_resto": float((yb == pb).mean()),
            **fe.alto_metrics(y, pred),
        }
    conc["spearman_inv_ttc_vs_spatial_component"] = float(stats.spearmanr(1.0 / np.maximum(df["ttc"], 0.5), spatial)[0])
    conc["spearman_spatial_component_vs_label"] = float(stats.spearmanr(spatial, y)[0])
    conc["spearman_multimodal_component_vs_label"] = float(stats.spearmanr(multimodal, y)[0])
    out["baseline_label_concordance"] = conc

    # --- 3-4. Techo de Bayes y sensibilidad al ruido ---------------------------
    sens = {}
    for sd in (NOISE_SD / 2, NOISE_SD, NOISE_SD * 2):
        _, hi = expected_cuts(det, sd)
        ceil = bayes_ceiling_f2(det, hi, sd)
        rng = np.random.default_rng(fe.RANDOM_STATE)
        y_sim = labels_from_score(det + rng.normal(0, sd, len(det)))
        pb = (fe.baseline_predict(df, fe.BASELINE_TTC_S) == fe.HIGH_CLASS).astype(int)
        sens[f"sigma_{sd:.2f}"] = {
            "bayes_ceiling_alto": ceil,
            "baseline_fixed_kappa_vs_simulated_label": float(cohen_kappa_score((y_sim == 2).astype(int), pb)),
            "baseline_fixed_f2_vs_simulated_label": fe.alto_metrics(y_sim, fe.baseline_predict(df, fe.BASELINE_TTC_S))["f2_alto"],
        }
        print(f"   σ={sd:.2f}: techo de Bayes F2(ALTO)={ceil['f2']:.3f} | baseline fijo F2={sens[f'sigma_{sd:.2f}']['baseline_fixed_f2_vs_simulated_label']:.3f}")
    out["noise_sensitivity"] = sens

    # --- 5. Etiquetas alternativas ---------------------------------------------
    if run_alt_labels:
        print("\nEtiquetas alternativas (misma partición/protocolo; ruido σ=3,8):")
        rng = np.random.default_rng(7)
        noise = rng.normal(0, NOISE_SD, len(df))
        # La escala de cada componente se normaliza para que el ruido pese lo mismo en ambas
        z = lambda v: (v - v.mean()) / v.std()
        # Escenarios de dominio específicos desacoplados de la proximidad física
        gas_score = (df["gas_co_ppm"] / 35.0) * 3.0 + (df["dust_density_mg_m3"] / 4.0) * 1.5 + z(spatial) * 0.5 + noise
        fatigue_score = df["fatigue_index"] * 3.5 + (np.maximum(df["worker_bpm"] - 80, 0) / 40.0) * 2.0 + z(spatial) * 0.5 + noise
        vibration_score = (df["vibration_rms"] / 4.5) * 3.0 + (np.abs(df["acceleration_z"] - 9.81) / 3.0) * 2.0 + z(spatial) * 0.5 + noise

        alts = {
            "label_original": y,
            "label_multimodal_only": labels_from_score(z(multimodal) * 3.0 + noise),
            "label_spatial_only": labels_from_score(z(spatial) * 3.0 + noise),
            "label_balanced_50_50": labels_from_score((z(spatial) + z(multimodal)) * 2.1 + noise),
            "label_gas_co_scenario": labels_from_score(gas_score),
            "label_operator_fatigue_scenario": labels_from_score(fatigue_score),
            "label_mechanical_vibration_scenario": labels_from_score(vibration_score),
        }
        out["alternative_labels"] = {
            k: {"prevalence_alto": float((v == 2).mean()), **evaluate_on_label(df, v, k)} for k, v in alts.items()}

    ml = out.get("alternative_labels", {})
    out["interpretation"] = [
        "risk_level es un target SINTÉTICO por diseño; cualquier modelo que alcance el techo de Bayes sólo "
        "reproduce la función generadora, no valida seguridad real.",
        f"El componente espacial explica {var_sp / total:.0%} de la varianza del score y comparte "
        "distance_3d/ttc/zona restringida con el baseline: la comparación ML vs baseline NO es independiente.",
        "Con etiqueta sólo-multimodal el baseline pierde capacidad y el ML se separa; con etiqueta sólo-espacial "
        "ocurre lo contrario. La conclusión 'ML supera reglas' depende de la definición de la etiqueta.",
    ]
    if ml:
        out["interpretation"].append(
            "Δ F2 (XGBoost − baseline ajustado, pp) por etiqueta: " + ", ".join(
                f"{k}: {v['xgb_minus_baseline_tuned_f2_pp']:+.1f}" for k, v in ml.items()))

    fe.dump_json(out, fe.RESULTS_DIR / "label_circularity_audit.json")
    print("\nGuardado: results/label_circularity_audit.json")
    return out


if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--no-alt-labels", action="store_true")
    run_audit(not ap.parse_args().no_alt_labels)
