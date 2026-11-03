# M-11: Auditing Synthetic Risk Labels and Physical Baselines in a Cyber-Physical Benchmark for Underground Mining

[![Python 3.10.11](https://img.shields.io/badge/python-3.10.11-blue.svg)](https://www.python.org/downloads/release/python-31011/)
[![License: CC BY 4.0](https://img.shields.io/badge/License-CC%20BY%204.0-lightgrey.svg)](https://creativecommons.org/licenses/by/4.0/)
[![DOI](https://img.shields.io/badge/DOI-10.5281%2Fzenodo.23747751-blue.svg)](https://doi.org/10.5281/zenodo.23747751)
[![Tests Passing](https://img.shields.io/badge/tests-17%2F17%20passed-brightgreen.svg)]()

> **Official Research Code and Experimental Reproducibility Repository**  
> **Target Manuscript:** *Acta Montanistica Slovaca* (AMS, 2026)  
> **Authors:** Favian Enrique Villa Valdiviezo (Unitru), Marck Alessandro Hermenegildo Pacheco (Unitru), Juan Pedro Santos Fernández (Unitru), Robert Jerry Sánchez Ticona (Unitru).  
> **Git Branch:** `feature/statistical-reports-validation`  
> **Dataset Identifier (SHA-256):** `b71d0b6baed8b6e0bc7eee1a1a5b7440d06a04ddaea5d502907cf03d958705f0`

---

## 1. Scope and Scientific Premise

**M-11 is a simulation-only cyber-physical benchmark and unidirectional digital shadow** combining industrial maintenance telemetry (UCI AI4I 2020) with synthetic 3D positioning, physiological, and environmental features (10,000 records; 37 fields).

### Core Methodological Findings
1. **Synthetic Label Circularity:** The target risk label is mathematically circular: spatial components account for **82.07% of the score variance**, stochastic noise accounts for **17.43%**, multimodal features (gas, fatigue, vibration) account for only **0.48%**, and covariance accounts for **0.02%**.
2. **Symmetric Model Comparison (Holdout Seed 42, N=2,000):** When thresholds are symmetrically calibrated exclusively on development data out-of-fold (OOF) probabilities, **Random Forest ($F_2 = 0.9103$) and calibrated Time-to-Collision ($F_2 = 0.9103$) match or slightly outperform XGBoost ($F_2 = 0.9065$)**. The paired bootstrap difference is $\Delta F_2 = -0.0038$ (95% CI $[-0.0129, +0.0047]$, Holm-adjusted McNemar $p = 0.6015$, no statistically significant difference).
3. **Multi-Seed Distribution (Seeds 1–10):** Across 10 independent stratified splits, average $F_2$ scores confirm the holdout finding: **TTC tuned ($0.9002 \pm 0.0091$) $\approx$ TTC fixed ($0.9000 \pm 0.0090$) $\approx$ Random Forest ($0.8980 \pm 0.0110$) $\approx$ Stacking ($0.8973 \pm 0.0102$) $\ge$ XGBoost ($0.8927 \pm 0.0121$)**.
4. **Decoupled Hazard Stress Tests:** When non-spatial hazards (CO, fatigue, vibration) are decoupled, $F_2$ optimization forces decision thresholds toward near-universal alarms ($\tau \le 0.05$), collapsing toward the trivial **Always-HIGH baseline ($F_2 = 0.5851$)**. A multimodal-only target achieves $F_2 = 0.6408$ with 54.1% specificity (+5.57 pp over Always-HIGH).
5. **Distinct Feature Ablations:** Removing 3 direct kinematic indicators (B2: `distance_3d`, `relative_speed`, `ttc`) reduces $F_2$ by **$-9.60$ pp** ($0.9065 \to 0.8105$), whereas removing the complete 8-feature spatial block (G) causes a **$-32.52$ pp** collapse ($0.9065 \to 0.5813$).
6. **Safety Boundaries:** M-11 is **not an active-mine collision-avoidance system nor a certified functional safety product (SIL / IEC 61508 / ISO 13849)**. Gemini serves solely as an exploratory natural-language interface under an inviolable software interlock (`override_allowed_by_llm = False`).

---

## 2. Repository Structure

```text
digital-twins-mines/
├── backend/
│   ├── app/                      # FastAPI core, ORM models, ML inference, WebSocket, interlock
│   ├── scripts/                  # Executable scientific benchmark and audit scripts
│   │   ├── download_and_process_public_dataset.py  # Dataset generator (37 fields, SHA-256)
│   │   ├── fair_eval.py                            # Symmetric 80/20 holdout evaluation (Tab. 3)
│   │   ├── run_multiseed_evaluation.py             # Multi-seed 1-10 benchmark (Summary stats)
│   │   ├── audit_label_circularity.py              # Variance breakdown & decoupled tests (Tab. 4)
│   │   ├── run_ablation_study.py                   # Distinct B2 vs G ablations (Tab. 7)
│   │   ├── run_shap_and_collinearity.py            # Global TreeSHAP feature attributions
│   │   ├── audit_genai_protocol.py                 # 100 emergency scenarios interlock check
│   │   ├── benchmark_hardware_profiler.py          # 5 Hz latency profiler (50-500 agents)
│   │   ├── generate_all_deliverables.py            # Master results generator
│   │   └── legacy/                                 # Historical exploratory scripts (archived)
│   ├── tests/                    # Automated pytest suite (17 passed / 100% verified)
│   │   ├── test_safety_interlock.py  # 9 tests: D.S. 024-2016-EM official MINEM 2026 rules
│   │   ├── test_security.py          # 5 tests: scrypt hashing and tampering rejection
│   │   └── test_model_parity.py      # 3 tests: metadata and inference parity
│   └── pytest.ini                # Pytest configuration targeting core verification tests
├── data/
│   └── raw/
│       └── public_mining_equipment_dataset.csv     # Official 10,000-row dataset (CC BY 4.0)
├── results/                      # Versioned CSV and JSON experimental outputs
│   ├── multiseed_comparison.csv             # 80 rows: Seeds 1-10 across all 8 models
│   ├── multiseed_summary.csv                # Mean, std, min, max per model (10 seeds)
│   ├── paired_statistical_tests_final.csv   # Paired bootstrap CI95 & McNemar-Holm tests
│   ├── feature_dictionary_final.csv         # Complete 37-column dataset inventory
│   ├── fair_comparison_results.json         # Primary symmetric classifier evaluation
│   ├── label_circularity_audit.json         # Generator score variance decomposition
│   ├── decoupled_labels_results.csv         # Decoupled targets vs Always-HIGH (Tab. 4)
│   ├── ablation_results.csv                 # B2 (-9.60 pp) vs G (-32.52 pp) ablations
│   ├── benchmark_latency.csv                # Backend P50/P95 latency at 50-500 agents
│   ├── benchmark_fps.csv                    # Historical Three.js browser viewer FPS
│   └── gemini_audit.csv                     # 100/100 deterministic scenario audit
├── reports/                      # Methodological audit reports and review responses
│   ├── MANUSCRIPT_RESULT_TRACEABILITY.md    # Complete traceability for manuscript tables
│   ├── RESULTADOS_EXPERIMENTALES.md         # Comprehensive scientific experimental report
│   ├── LIMITACIONES_PENDIENTES.md           # Formal limitations and boundaries
│   ├── MATRIZ_RESPUESTA_REVISORES.md        # Point-by-point reviewer response matrix
│   └── audit_history/                       # Historical audit sprint logs
├── figures/                      # High-resolution publication plots
├── frontend/                     # Interactive 3D visualization prototype (Next.js / Three.js)
├── DATASET_CHECKSUM.sha256       # Cryptographic SHA-256 verification hash
└── requirements.txt              # Pinned Python package dependencies
```

---

## 3. Quick-Start & Step-by-Step Reproduction Guide

### 3.1. Environment Setup

```bash
git clone https://github.com/DrkonVilla/digital-twins-mines.git
cd digital-twins-mines
git checkout feature/statistical-reports-validation

# Recommended Python 3.10.11 virtual environment
python -m venv venv
# Windows:
venv\Scripts\activate
# Linux/macOS:
source venv/bin/activate

pip install -r requirements.txt
```

### 3.2. Dataset Cryptographic Verification

Verify that the published 10,000-row dataset matches the exact SHA-256 hash declared in the manuscript:

```powershell
# Windows PowerShell:
Get-FileHash data/raw/public_mining_equipment_dataset.csv -Algorithm SHA256
# Expected: B71D0B6BAED8B6E0BC7EEE1A1A5B7440D06A04DDAEA5D502907CF03D958705F0

# Linux / macOS:
sha256sum data/raw/public_mining_equipment_dataset.csv
```

### 3.3. Execute Automated Unit Tests (17/17 Passed)

```bash
cd backend
python -m pytest -v
# Output: 17 passed in ~20 seconds
```

### 3.4. Reproduce Manuscript Tables and Figures

| Manuscript Target | Executable Command | Generated Artifact | Key Reported Metric |
|---|---|---|---|
| **Table 2 (37-Variable Dictionary)** | `python -c "import pandas as pd; print(pd.read_csv('results/feature_dictionary_final.csv'))"` | `results/feature_dictionary_final.csv` | 37 fields, 16 model predictors |
| **Table 3 (Symmetric Holdout Seed 42)** | `python backend/scripts/fair_eval.py` | `results/metrics_comparison.csv` | RF $F_2 = 0.9103$, TTC $F_2 = 0.9103$, XGB $F_2 = 0.9065$ |
| **Paired Statistical Tests (Seed 42)** | Inspected in `results/paired_statistical_tests_final.csv` | `results/paired_statistical_tests_final.csv` | $\Delta F_2 = -0.0038$, CI $[-0.0129, +0.0047]$, Holm $p = 0.6015$ |
| **Multi-Seed Benchmark (Seeds 1–10)** | `python backend/scripts/run_multiseed_evaluation.py` | `results/multiseed_summary.csv` | RF $0.8980$, Stacking $0.8973$, XGB $0.8927$, TTC tuned $0.9002$ |
| **Figure 2 & Table 4 (Decoupled Targets)** | `python backend/scripts/audit_label_circularity.py` | `results/label_circularity_audit.json`<br>`results/decoupled_labels_results.csv` | 82.07% spatial, Multimodal $F_2 = 0.6408$, Always-HIGH $F_2 = 0.5851$ |
| **Table 5 & Figure 4 (Latency at 5 Hz)** | `python backend/scripts/benchmark_hardware_profiler.py` | `results/benchmark_latency.csv` | P95 = 27.91 ms at 500 agents (< 200 ms budget) |
| **Table 6 (100 Scenario Safety Audit)** | `python backend/scripts/audit_genai_protocol.py` | `results/gemini_audit.csv` | 100/100 expectations met (D.S. 024-2016-EM) |
| **Table 7 (Distinct B2 vs G Ablations)** | `python backend/scripts/run_ablation_study.py` | `results/ablation_results.csv` | B2: $-9.60$ pp ($F_2=0.8105$), G: $-32.52$ pp ($F_2=0.5813$) |
| **Table 8 (Alert Burden)** | Inspected in `results/metrics_comparison.csv` | `results/metrics_comparison.csv` | Alert fraction: XGB 27.0%, TTC 26.8%, Always-HIGH 100% |

---

## 4. Key Results Summary Tables

### 4.1. Symmetric Holdout Comparison (Seed 42, N=2,000)

| Model / System | Rule / Threshold ($\tau$) | Precision ALTO | Recall ALTO | $F_2$ ALTO | AUC-ROC | AUC-PR |
|---|:---:|:---:|:---:|:---:|:---:|:---:|
| **Random Forest** | 0.18 | 75.63 % | 95.91 % | **0.9103** | 0.9694 | 0.9463 |
| **TTC tuned** | 3.0 s | 78.00 % | 95.00 % | **0.9103** | — | — |
| **Stacking Ensemble** | 0.09 | 75.86 % | 95.68 % | **0.9093** | 0.9735 | 0.9500 |
| **TTC fixed** | 5.0 s | 75.68 % | 95.45 % | **0.9071** | — | — |
| **XGBoost (Reference)** | 0.18 | 77.22 % | 94.77 % | **0.9065** | 0.9710 | 0.9484 |
| **Voting Ensemble** | 0.18 | 74.56 % | 95.23 % | **0.9022** | 0.9698 | 0.9441 |
| **SVM (RBF Kernel)** | 0.17 | 73.64 % | 92.05 % | **0.8766** | 0.9696 | 0.9293 |
| **MLP Neural Net** | 0.13 | 74.70 % | 84.55 % | **0.8237** | 0.9403 | 0.8787 |

### 4.2. Multi-Seed Empirical Distribution (Seeds 1–10)

| Model / System | Precision ALTO (Mean $\pm$ Std) | Recall ALTO (Mean $\pm$ Std) | $F_2$ ALTO (Mean $\pm$ Std) | Min $F_2$ | Max $F_2$ | AUC-ROC (Mean $\pm$ Std) |
|---|:---:|:---:|:---:|:---:|:---:|:---:|
| **TTC tuned** | $0.7757 \pm 0.0228$ | $0.9380 \pm 0.0071$ | **$0.9002 \pm 0.0091$** | 0.8878 | 0.9145 | $0.9306 \pm 0.0067$ |
| **TTC fixed** | $0.7468 \pm 0.0223$ | $0.9489 \pm 0.0087$ | **$0.9000 \pm 0.0090$** | 0.8868 | 0.9117 | $0.9289 \pm 0.0066$ |
| **Random Forest** | $0.7605 \pm 0.0218$ | $0.9407 \pm 0.0122$ | **$0.8980 \pm 0.0110$** | 0.8751 | 0.9139 | $0.9653 \pm 0.0066$ |
| **Stacking** | $0.7583 \pm 0.0235$ | $0.9407 \pm 0.0109$ | **$0.8973 \pm 0.0102$** | 0.8807 | 0.9139 | $0.9638 \pm 0.0058$ |
| **XGBoost** | $0.7628 \pm 0.0181$ | $0.9325 \pm 0.0136$ | **$0.8927 \pm 0.0121$** | 0.8670 | 0.9109 | $0.9631 \pm 0.0058$ |
| **Voting** | $0.7243 \pm 0.0249$ | $0.9382 \pm 0.0105$ | **$0.8856 \pm 0.0075$** | 0.8732 | 0.8959 | $0.9623 \pm 0.0052$ |
| **SVM (RBF)** | $0.7157 \pm 0.0237$ | $0.9305 \pm 0.0095$ | **$0.8775 \pm 0.0069$** | 0.8688 | 0.8925 | $0.9587 \pm 0.0069$ |
| **MLP** | $0.7271 \pm 0.0310$ | $0.8466 \pm 0.0209$ | **$0.8193 \pm 0.0153$** | 0.7937 | 0.8434 | $0.9315 \pm 0.0102$ |

---

## 5. Software Environment and Reproducibility Metadata

The complete software environment was frozen and verified under Python 3.10.11 on Windows 11 Home 64-bit (build 26200):
- **Core libraries:** `numpy==1.26.4`, `pandas==2.2.3`, `scipy==1.15.3`, `scikit-learn==1.7.2`, `xgboost==3.2.0`, `imbalanced-learn==0.14.2`, `shap==0.49.1`, `joblib==1.5.3`.
- **Complete result mapping:** Consult [`reports/MANUSCRIPT_RESULT_TRACEABILITY.md`](reports/MANUSCRIPT_RESULT_TRACEABILITY.md) for individual cell-by-cell links between the manuscript numbers and versioned result files.
- **Variable dictionary:** Consult [`results/feature_dictionary_final.csv`](results/feature_dictionary_final.csv) for the exhaustive 37-column dataset inventory and documentation of the 16 model predictors.

---

## 6. License and Citation

- **Code:** Licensed under the [MIT License](LICENSE).
- **Dataset:** Distributed under [Creative Commons Attribution 4.0 International (CC BY 4.0)](https://creativecommons.org/licenses/by/4.0/).
- **Permanent Archive:** [https://doi.org/10.5281/zenodo.23747751](https://doi.org/10.5281/zenodo.23747751).
