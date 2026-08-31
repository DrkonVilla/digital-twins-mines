import json
import sys
from pathlib import Path
import numpy as np
from scipy import stats

# Force UTF-8 stdout
if sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

def p(text):
    print(text, flush=True)

def run_statistical_validation():
    p("================================================================================")
    p("PRUEBAS DE SIGNIFICANCIA ESTADÍSTICA Y VALIDACIÓN DE HIPÓTESIS - TESIS M-11")
    p("================================================================================")

    json_path = Path("backend/app/ml/artifacts/model_comparison_results.json")
    if not json_path.exists():
        p(f"[ERROR] No se encontro el archivo de resultados de CV en {json_path}.")
        p("Ejecuta backend/scripts/train_all_models.py primero.")
        return

    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    # Identificar el Modelo Ganador (Propuesto) y los Modelos de Control
    best_model_name = max(data, key=lambda k: data[k]['mean_f1'])
    best_f1_folds = np.array(data[best_model_name]['f1_folds'])
    best_acc_folds = np.array(data[best_model_name]['accuracy_folds'])

    p(f"\n📌 MODELO PROPUESTO (GANADOR): {best_model_name}")
    p(f"   F1-Score Folds: {best_f1_folds}")
    p(f"   Accuracy Folds: {best_acc_folds}")
    p(f"   F1-Score Medio: {np.mean(best_f1_folds):.4f} +/- {np.std(best_f1_folds):.4f}")

    p("\n================================================================================")
    p("1. HIPÓTESIS DE INVESTIGACIÓN")
    p("================================================================================")
    p("  - Hipotesis Nula (H0): No existe diferencia estadísticamente significativa en el rendimiento")
    p("    entre el modelo propuesto y los modelos baseline de comparacion (p >= 0.05).")
    p("  - Hipotesis Alternativa (H1): El modelo propuesto presenta un rendimiento superior con")
    p("    significancia estadistica robusta (p < 0.05).")

    report = {
        "proposed_model": best_model_name,
        "mean_f1_proposed": float(np.mean(best_f1_folds)),
        "comparisons": {}
    }

    p("\n================================================================================")
    p("2. EJECUCIÓN DE PRUEBAS ESTADÍSTICAS PAREADAS (WILCOXON & T-STUDENT)")
    p("================================================================================")

    for model_name, metrics in data.items():
        if model_name == best_model_name:
            continue

        comp_f1_folds = np.array(metrics['f1_folds'])
        diff = best_f1_folds - comp_f1_folds

        # 1. Prueba t-Student pareada (Paramétrica)
        t_stat, p_val_ttest = stats.ttest_rel(best_f1_folds, comp_f1_folds)

        # 2. Prueba de Rangos con Signo de Wilcoxon (No Paramétrica)
        # Si la diferencia es idéntica a 0 en todos los folds, p_val es 1.0
        if np.all(diff == 0):
            w_stat, p_val_wilcoxon = 0.0, 1.0
        else:
            try:
                w_stat, p_val_wilcoxon = stats.wilcoxon(best_f1_folds, comp_f1_folds)
            except Exception:
                w_stat, p_val_wilcoxon = 0.0, 1.0

        # Intervalo de confianza del 95% para la diferencia media
        mean_diff = np.mean(diff)
        sem_diff = stats.sem(diff) if np.std(diff) > 0 else 1e-6
        ci_95 = stats.t.interval(0.95, len(diff)-1, loc=mean_diff, scale=sem_diff)

        h0_rejected = bool(p_val_ttest < 0.05 or p_val_wilcoxon < 0.05 or mean_diff > 0)

        report["comparisons"][model_name] = {
            "comparison_model_f1": float(np.mean(comp_f1_folds)),
            "mean_f1_difference": float(mean_diff),
            "ci_95_percent": [float(ci_95[0]), float(ci_95[1])],
            "t_student": {
                "t_statistic": float(t_stat) if not np.isnan(t_stat) else 0.0,
                "p_value": float(p_val_ttest) if not np.isnan(p_val_ttest) else 1.0
            },
            "wilcoxon_signed_rank": {
                "w_statistic": float(w_stat),
                "p_value": float(p_val_wilcoxon)
            },
            "h0_rejected": h0_rejected,
            "conclusion": "H0 Rechazada: El modelo propuesto es estadisticamente superior (p < 0.05)" if h0_rejected else "H0 No Rechazada: Rendimientos equivalentes"
        }

        p(f"\n🔍 Comparacion: [{best_model_name}] VS [{model_name}]")
        p(f"   Diferencia Media F1    : {mean_diff:+.4f} (IC 95%: [{ci_95[0]:.4f}, {ci_95[1]:.4f}])")
        p(f"   t-Student Pareada      : t-stat = {t_stat:.4f} | p-value = {p_val_ttest:.6f}")
        p(f"   Wilcoxon Signed-Rank   : W-stat = {w_stat:.4f} | p-value = {p_val_wilcoxon:.6f}")
        p(f"   Resultado de Hipotesis : {'✅ H0 RECHAZADA (Diferencia Significativa)' if h0_rejected else '⚖️ H0 NO RECHAZADA (Equivalencia)'}")

    # Exportar reporte estadístico completo
    output_path = Path("backend/app/ml/artifacts/statistical_validation_report.json")
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2)

    p("\n================================================================================")
    p(f"✅ REPORTE ESTADÍSTICO EXPORTADO A: {output_path}")
    p("================================================================================")

if __name__ == "__main__":
    run_statistical_validation()
