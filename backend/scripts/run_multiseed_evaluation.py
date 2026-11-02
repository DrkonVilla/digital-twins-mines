"""
Protocolo de Reejecución Multi-Seed (Seeds 1-10) para M-11.
Cumple estrictamente los requisitos metodológicos de Acta Montanistica Slovaca:
  - Split estratificado 80/20 por seed.
  - Calibración de umbral F2 exclusivamente con development (5-fold OOF).
  - SMOTENC anidado por pliegue.
  - Mismas 16 variables y mismos hiperparámetros.
  - Modelos: XGBoost, Random Forest, Stacking, Voting, SVM-RBF, MLP, TTC fixed, TTC tuned.
  - Métricas: Precision HIGH, Recall HIGH, F2 HIGH, AUC-ROC, AUC-PR.
  - Exporta: results/multiseed_comparison.csv y results/multiseed_summary.csv
"""
import sys
import time
from pathlib import Path
import numpy as np
import pandas as pd
from sklearn.model_selection import StratifiedKFold
from imblearn.over_sampling import SMOTENC
from sklearn.metrics import precision_score, recall_score, roc_auc_score, average_precision_score

PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT / "backend" / "scripts"))
import fair_eval as fe

SEEDS = list(range(1, 11))
MODELS = ["XGBoost", "Random Forest", "Stacking", "Voting", "SVM-RBF", "MLP", "TTC fixed", "TTC tuned"]
RESULTS_DIR = PROJECT_ROOT / "results"
COMPARISON_CSV = RESULTS_DIR / "multiseed_comparison.csv"
SUMMARY_CSV = RESULTS_DIR / "multiseed_summary.csv"

def compute_metrics(y_true, y_pred, y_proba=None):
    yb = (np.asarray(y_true) == fe.HIGH_CLASS).astype(int)
    pb = (np.asarray(y_pred) == fe.HIGH_CLASS).astype(int)
    p = precision_score(yb, pb, zero_division=0)
    r = recall_score(yb, pb, zero_division=0)
    f2 = fe.fbeta(p, r, beta=2.0)
    
    if y_proba is not None:
        try:
            auc_roc = roc_auc_score(yb, y_proba[:, fe.HIGH_CLASS])
        except Exception:
            auc_roc = float("nan")
        try:
            auc_pr = average_precision_score(yb, y_proba[:, fe.HIGH_CLASS])
        except Exception:
            auc_pr = float("nan")
    else:
        # Binary fallback for rule-based baselines
        try:
            auc_roc = roc_auc_score(yb, pb.astype(float))
        except Exception:
            auc_roc = float("nan")
        try:
            auc_pr = average_precision_score(yb, pb.astype(float))
        except Exception:
            auc_pr = float("nan")
            
    return {
        "precision_high": float(p),
        "recall_high": float(r),
        "f2_high": float(f2),
        "auc_roc": float(auc_roc),
        "auc_pr": float(auc_pr)
    }

def main():
    print(f"Iniciando reejecución multi-seed para seeds {SEEDS}...", flush=True)
    df = fe.load_dataset()
    cat_idx = [i for i, f in enumerate(fe.FEATURES) if f in fe.CATEGORICAL]
    
    # Load existing rows if resume needed
    all_rows = []
    completed_seeds = set()
    if COMPARISON_CSV.exists():
        try:
            df_existing = pd.read_csv(COMPARISON_CSV)
            all_rows = df_existing.to_dict("records")
            # Count seeds having all 8 models
            counts = df_existing["seed"].value_counts()
            completed_seeds = set(counts[counts == len(MODELS)].index.tolist())
            if completed_seeds:
                print(f"Seeds ya completadas previamente en {COMPARISON_CSV}: {sorted(list(completed_seeds))}", flush=True)
        except Exception:
            all_rows = []
    
    for seed in SEEDS:
        if seed in completed_seeds:
            print(f"Saltando Seed {seed} ya completada.", flush=True)
            continue
            
        t0 = time.time()
        print(f"\n==========================================", flush=True)
        print(f"--- SEED {seed} / 10 ---", flush=True)
        print(f"==========================================", flush=True)
        
        X_tr, X_te, y_tr, y_te = fe.split_train_test(df, seed=seed)
        skf = StratifiedKFold(n_splits=5, shuffle=True, random_state=seed)
        
        print(f"  [Seed {seed}] Precomputando SMOTENC sobre 5 pliegues...", flush=True)
        resampled_folds = []
        for fold, (tr, va) in enumerate(skf.split(X_tr, y_tr)):
            smote = SMOTENC(categorical_features=cat_idx, random_state=seed)
            X_res, y_res = smote.fit_resample(X_tr.iloc[tr], y_tr.iloc[tr])
            resampled_folds.append((X_res, y_res, va))
            
        smote_full = SMOTENC(categorical_features=cat_idx, random_state=seed)
        X_res_full, y_res_full = smote_full.fit_resample(X_tr, y_tr)
        
        # 1. XGBoost
        print(f"  [Seed {seed}] 1/8 Evaluando XGBoost...", flush=True)
        oof_xgb = np.zeros((len(y_tr), 3))
        for X_res, y_res, va in resampled_folds:
            pipe = fe.make_pipeline("XGBoost", use_smote=False, seed=seed)
            pipe.fit(X_res, y_res)
            oof_xgb[va] = pipe.predict_proba(X_tr.iloc[va])
        thr_xgb, _ = fe.find_f2_threshold(y_tr, oof_xgb[:, fe.HIGH_CLASS])
        pipe_xgb = fe.make_pipeline("XGBoost", use_smote=False, seed=seed).fit(X_res_full, y_res_full)
        proba_xgb = pipe_xgb.predict_proba(X_te)
        pred_xgb = fe.apply_threshold(proba_xgb, thr_xgb)
        m_xgb = compute_metrics(y_te, pred_xgb, proba_xgb)
        all_rows.append({"seed": seed, "model": "XGBoost", "threshold": round(thr_xgb, 4), **m_xgb})
        print(f"    XGBoost F2: {m_xgb['f2_high']:.4f}, Rec: {m_xgb['recall_high']:.4f}, Prec: {m_xgb['precision_high']:.4f}, ROC: {m_xgb['auc_roc']:.4f}", flush=True)

        # 2. Random Forest
        print(f"  [Seed {seed}] 2/8 Evaluando Random Forest...", flush=True)
        oof_rf = np.zeros((len(y_tr), 3))
        for X_res, y_res, va in resampled_folds:
            pipe = fe.make_pipeline("RandomForest", use_smote=False, seed=seed)
            pipe.fit(X_res, y_res)
            oof_rf[va] = pipe.predict_proba(X_tr.iloc[va])
        thr_rf, _ = fe.find_f2_threshold(y_tr, oof_rf[:, fe.HIGH_CLASS])
        pipe_rf = fe.make_pipeline("RandomForest", use_smote=False, seed=seed).fit(X_res_full, y_res_full)
        proba_rf = pipe_rf.predict_proba(X_te)
        pred_rf = fe.apply_threshold(proba_rf, thr_rf)
        m_rf = compute_metrics(y_te, pred_rf, proba_rf)
        all_rows.append({"seed": seed, "model": "Random Forest", "threshold": round(thr_rf, 4), **m_rf})
        print(f"    Random Forest F2: {m_rf['f2_high']:.4f}, Rec: {m_rf['recall_high']:.4f}, Prec: {m_rf['precision_high']:.4f}, ROC: {m_rf['auc_roc']:.4f}", flush=True)

        # 3. SVM-RBF
        print(f"  [Seed {seed}] 3/8 Evaluando SVM-RBF...", flush=True)
        oof_svm = np.zeros((len(y_tr), 3))
        for X_res, y_res, va in resampled_folds:
            pipe = fe.make_pipeline("SVM_RBF", use_smote=False, seed=seed)
            pipe.fit(X_res, y_res)
            oof_svm[va] = pipe.predict_proba(X_tr.iloc[va])
        thr_svm, _ = fe.find_f2_threshold(y_tr, oof_svm[:, fe.HIGH_CLASS])
        pipe_svm = fe.make_pipeline("SVM_RBF", use_smote=False, seed=seed).fit(X_res_full, y_res_full)
        proba_svm = pipe_svm.predict_proba(X_te)
        pred_svm = fe.apply_threshold(proba_svm, thr_svm)
        m_svm = compute_metrics(y_te, pred_svm, proba_svm)
        all_rows.append({"seed": seed, "model": "SVM-RBF", "threshold": round(thr_svm, 4), **m_svm})
        print(f"    SVM-RBF F2: {m_svm['f2_high']:.4f}, Rec: {m_svm['recall_high']:.4f}, Prec: {m_svm['precision_high']:.4f}, ROC: {m_svm['auc_roc']:.4f}", flush=True)

        # 4. MLP
        print(f"  [Seed {seed}] 4/8 Evaluando MLP...", flush=True)
        oof_mlp = np.zeros((len(y_tr), 3))
        for X_res, y_res, va in resampled_folds:
            pipe = fe.make_pipeline("MLP_NeuralNet", use_smote=False, seed=seed)
            pipe.fit(X_res, y_res)
            oof_mlp[va] = pipe.predict_proba(X_tr.iloc[va])
        thr_mlp, _ = fe.find_f2_threshold(y_tr, oof_mlp[:, fe.HIGH_CLASS])
        pipe_mlp = fe.make_pipeline("MLP_NeuralNet", use_smote=False, seed=seed).fit(X_res_full, y_res_full)
        proba_mlp = pipe_mlp.predict_proba(X_te)
        pred_mlp = fe.apply_threshold(proba_mlp, thr_mlp)
        m_mlp = compute_metrics(y_te, pred_mlp, proba_mlp)
        all_rows.append({"seed": seed, "model": "MLP", "threshold": round(thr_mlp, 4), **m_mlp})
        print(f"    MLP F2: {m_mlp['f2_high']:.4f}, Rec: {m_mlp['recall_high']:.4f}, Prec: {m_mlp['precision_high']:.4f}, ROC: {m_mlp['auc_roc']:.4f}", flush=True)

        # 5. Stacking
        print(f"  [Seed {seed}] 5/8 Evaluando Stacking...", flush=True)
        oof_stk = np.zeros((len(y_tr), 3))
        for X_res, y_res, va in resampled_folds:
            pipe = fe.make_pipeline("Stacking_Ensemble", use_smote=False, seed=seed)
            pipe.fit(X_res, y_res)
            oof_stk[va] = pipe.predict_proba(X_tr.iloc[va])
        thr_stk, _ = fe.find_f2_threshold(y_tr, oof_stk[:, fe.HIGH_CLASS])
        pipe_stk = fe.make_pipeline("Stacking_Ensemble", use_smote=False, seed=seed).fit(X_res_full, y_res_full)
        proba_stk = pipe_stk.predict_proba(X_te)
        pred_stk = fe.apply_threshold(proba_stk, thr_stk)
        m_stk = compute_metrics(y_te, pred_stk, proba_stk)
        all_rows.append({"seed": seed, "model": "Stacking", "threshold": round(thr_stk, 4), **m_stk})
        print(f"    Stacking F2: {m_stk['f2_high']:.4f}, Rec: {m_stk['recall_high']:.4f}, Prec: {m_stk['precision_high']:.4f}, ROC: {m_stk['auc_roc']:.4f}", flush=True)

        # 6. Voting (soft voting averaging RF, XGB, MLP)
        print(f"  [Seed {seed}] 6/8 Evaluando Voting...", flush=True)
        oof_vot = (oof_rf + oof_xgb + oof_mlp) / 3.0
        thr_vot, _ = fe.find_f2_threshold(y_tr, oof_vot[:, fe.HIGH_CLASS])
        proba_vot = (proba_rf + proba_xgb + proba_mlp) / 3.0
        pred_vot = fe.apply_threshold(proba_vot, thr_vot)
        m_vot = compute_metrics(y_te, pred_vot, proba_vot)
        all_rows.append({"seed": seed, "model": "Voting", "threshold": round(thr_vot, 4), **m_vot})
        print(f"    Voting F2: {m_vot['f2_high']:.4f}, Rec: {m_vot['recall_high']:.4f}, Prec: {m_vot['precision_high']:.4f}, ROC: {m_vot['auc_roc']:.4f}", flush=True)

        # 7. TTC fixed
        print(f"  [Seed {seed}] 7/8 Evaluando Baseline TTC fixed...", flush=True)
        pred_ttc_fix = fe.baseline_predict(X_te, 5.0)
        m_ttc_fix = compute_metrics(y_te, pred_ttc_fix)
        all_rows.append({"seed": seed, "model": "TTC fixed", "threshold": 5.0, **m_ttc_fix})
        print(f"    TTC fixed F2: {m_ttc_fix['f2_high']:.4f}, Rec: {m_ttc_fix['recall_high']:.4f}, Prec: {m_ttc_fix['precision_high']:.4f}", flush=True)

        # 8. TTC tuned
        print(f"  [Seed {seed}] 8/8 Evaluando Baseline TTC tuned...", flush=True)
        t_tuned, _ = fe.tune_baseline_ttc(X_tr, y_tr)
        pred_ttc_tun = fe.baseline_predict(X_te, t_tuned)
        m_ttc_tun = compute_metrics(y_te, pred_ttc_tun)
        all_rows.append({"seed": seed, "model": "TTC tuned", "threshold": round(float(t_tuned), 2), **m_ttc_tun})
        print(f"    TTC tuned F2: {m_ttc_tun['f2_high']:.4f}, Rec: {m_ttc_tun['recall_high']:.4f}, Prec: {m_ttc_tun['precision_high']:.4f} (tuned threshold={t_tuned:.1f}s)", flush=True)

        # Export partial dataframe after each seed
        df_comp = pd.DataFrame(all_rows)
        df_comp.to_csv(COMPARISON_CSV, index=False, encoding="utf-8")
        elapsed = time.time() - t0
        print(f"--- Seed {seed} completada en {elapsed:.1f}s. Guardado en {COMPARISON_CSV} ---", flush=True)

    print(f"\n==========================================", flush=True)
    print("CALCULANDO RESUMEN MULTI-SEED (Summary Statistics)", flush=True)
    print(f"==========================================", flush=True)
    df_comp = pd.DataFrame(all_rows)
    metrics_to_summarize = ["precision_high", "recall_high", "f2_high", "auc_roc", "auc_pr"]
    
    summary_rows = []
    for model in MODELS:
        sub = df_comp[df_comp["model"] == model]
        row = {"model": model, "n_seeds": len(sub)}
        for m in metrics_to_summarize:
            vals = sub[m].dropna()
            row[f"{m}_mean"] = round(float(vals.mean()), 4) if len(vals) > 0 else None
            row[f"{m}_std"] = round(float(vals.std(ddof=1)), 4) if len(vals) > 1 else 0.0
            row[f"{m}_min"] = round(float(vals.min()), 4) if len(vals) > 0 else None
            row[f"{m}_max"] = round(float(vals.max()), 4) if len(vals) > 0 else None
        summary_rows.append(row)
        
    df_sum = pd.DataFrame(summary_rows)
    df_sum.to_csv(SUMMARY_CSV, index=False, encoding="utf-8")
    print(f"SUCCESS: Exportado resumen a {SUMMARY_CSV}", flush=True)
    print(df_sum[["model", "precision_high_mean", "recall_high_mean", "f2_high_mean", "auc_roc_mean", "auc_pr_mean"]].to_string(), flush=True)

if __name__ == "__main__":
    main()
