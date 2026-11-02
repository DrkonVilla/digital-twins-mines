import sys
import time
from pathlib import Path
import numpy as np
import pandas as pd
from sklearn.model_selection import StratifiedKFold
from imblearn.over_sampling import SMOTENC

PROJECT_ROOT = Path(r"c:\Users\villa\Downloads\Mining\digital-twins-mines")
sys.path.insert(0, str(PROJECT_ROOT / "backend" / "scripts"))
import fair_eval as fe

df = fe.load_dataset()
seed = 1
t_start = time.time()
print(f"Testing Seed {seed} timing...")
X_tr, X_te, y_tr, y_te = fe.split_train_test(df, seed=seed)
skf = StratifiedKFold(n_splits=5, shuffle=True, random_state=seed)
cat_idx = [i for i, f in enumerate(fe.FEATURES) if f in fe.CATEGORICAL]

t0 = time.time()
resampled_folds = []
for fold, (tr, va) in enumerate(skf.split(X_tr, y_tr)):
    smote = SMOTENC(categorical_features=cat_idx, random_state=seed)
    X_res, y_res = smote.fit_resample(X_tr.iloc[tr], y_tr.iloc[tr])
    resampled_folds.append((X_res, y_res, va))
smote_full = SMOTENC(categorical_features=cat_idx, random_state=seed)
X_res_full, y_res_full = smote_full.fit_resample(X_tr, y_tr)
print(f"SMOTENC 5 folds + full: {time.time()-t0:.2f}s")

# 1. XGBoost
t0 = time.time()
oof_xgb = np.zeros((len(y_tr), 3))
for X_res, y_res, va in resampled_folds:
    pipe = fe.make_pipeline("XGBoost", use_smote=False, seed=seed)
    pipe.fit(X_res, y_res)
    oof_xgb[va] = pipe.predict_proba(X_tr.iloc[va])
thr_xgb, _ = fe.find_f2_threshold(y_tr, oof_xgb[:, fe.HIGH_CLASS])
pipe_xgb = fe.make_pipeline("XGBoost", use_smote=False, seed=seed).fit(X_res_full, y_res_full)
proba_xgb = pipe_xgb.predict_proba(X_te)
pred_xgb = fe.apply_threshold(proba_xgb, thr_xgb)
m_xgb = fe.alto_metrics(y_te, pred_xgb)
print(f"XGBoost: {time.time()-t0:.2f}s, F2: {m_xgb['f2_alto']:.4f}")

# 2. RF
t0 = time.time()
oof_rf = np.zeros((len(y_tr), 3))
for X_res, y_res, va in resampled_folds:
    pipe = fe.make_pipeline("RandomForest", use_smote=False, seed=seed)
    pipe.fit(X_res, y_res)
    oof_rf[va] = pipe.predict_proba(X_tr.iloc[va])
thr_rf, _ = fe.find_f2_threshold(y_tr, oof_rf[:, fe.HIGH_CLASS])
pipe_rf = fe.make_pipeline("RandomForest", use_smote=False, seed=seed).fit(X_res_full, y_res_full)
proba_rf = pipe_rf.predict_proba(X_te)
pred_rf = fe.apply_threshold(proba_rf, thr_rf)
m_rf = fe.alto_metrics(y_te, pred_rf)
print(f"Random Forest: {time.time()-t0:.2f}s, F2: {m_rf['f2_alto']:.4f}")

# 3. TTC fixed & tuned
t0 = time.time()
pred_ttc_f = fe.baseline_predict(X_te, 5.0)
m_ttc_f = fe.alto_metrics(y_te, pred_ttc_f)
t_tuned, _ = fe.tune_baseline_ttc(X_tr, y_tr)
pred_ttc_t = fe.baseline_predict(X_te, t_tuned)
m_ttc_t = fe.alto_metrics(y_te, pred_ttc_t)
print(f"Baselines TTC: {time.time()-t0:.2f}s, Fixed F2: {m_ttc_f['f2_alto']:.4f}, Tuned F2: {m_ttc_t['f2_alto']:.4f}")

print(f"Total partial time: {time.time()-t_start:.2f}s")

