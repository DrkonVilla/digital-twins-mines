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

    artifacts_dir = Path(__file__).resolve().parent.parent / "app" / "ml" / "artifacts"
    json_path = artifacts_dir / "model_comparison_results.json"
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

    p(f"\n🏆 MODELO CAMPEÓN PROPUESTO: {best_model_name}")
    p(f"   F1-Score (5-Fold CV): {np.mean(best_f1_folds):.4f} ± {np.std(best_f1_folds):.4f}")
    p(f"   Accuracy (5-Fold CV): {np.mean(best_acc_folds):.4f} ± {np.std(best_acc_folds):.4f}")

    p("\n================================================================================")
    p("1. TABLA COMPARATIVA DE ARCHITECTURAS EVALUADAS (BENCHMARK 5-FOLD CV)")
    p("================================================================================")
    p(f"{'Pos.':<5} | {'Modelo':<20} | {'F1-Score Medio':<16} | {'Std Dev':<10} | {'Accuracy Medio':<14}")
    p("-" * 75)
    
    sorted_models = sorted(data.items(), key=lambda item: item[1]['mean_f1'], reverse=True)
    for rank, (m_name, m_metrics) in enumerate(sorted_models, 1):
        f1_m = np.mean(m_metrics['f1_folds'])
        f1_s = np.std(m_metrics['f1_folds'])
        acc_m = np.mean(m_metrics['accuracy_folds'])
        tag = " 🏆 (Propuesto)" if m_name == best_model_name else ""
        p(f"#{rank:<4} | {m_name + tag:<20} | {f1_m:.4f}           | ±{f1_s:.4f}   | {acc_m:.4f}")

    p("\n================================================================================")
    p("2. HIPÓTESIS GLOBAL DE INVESTIGACIÓN (TEST DE FRIEDMAN)")
    p("================================================================================")
    p("   H0: No existen diferencias estadísticamente significativas en el F1-Score entre los 5 modelos.")
    p("   H1: Al menos un modelo presenta un rendimiento estadísticamente distinto (p < 0.05).")

    all_f1_folds = [np.array(m['f1_folds']) for m in data.values()]
    try:
        f_stat, f_p = stats.friedmanchisquare(*all_f1_folds)
    except Exception:
        f_stat, f_p = 0.0, 1.0

    p(f"\n📊 Resultado Test de Friedman (K=5 folds, 5 modelos):")
    p(f"   Estadístico de Friedman (Q) : {f_stat:.4f}")
    p(f"   p-value                     : {f_p:.6f}")
    p(f"   Conclusión                  : {'✅ H0 RECHAZADA (Existe superioridad/diferencia global)' if f_p < 0.05 else '⚖️ H0 NO RECHAZADA'}")

    report = {
        "proposed_model": best_model_name,
        "mean_f1_proposed": float(np.mean(best_f1_folds)),
        "statistical_tests": {
            "friedman_stat": float(f_stat),
            "friedman_p": float(f_p),
            "h0_rejected": bool(f_p < 0.05)
        },
        "comparisons": {}
    }

    p("\n================================================================================")
    p("3. PRUEBAS ESTADÍSTICAS PAREADAS POST-HOC (WILCOXON & T-STUDENT + COHEN'S d)")
    p("================================================================================")

    for model_name, metrics in data.items():
        if model_name == best_model_name:
            continue

        comp_f1_folds = np.array(metrics['f1_folds'])
        diff = best_f1_folds - comp_f1_folds

        # 1. Prueba t-Student pareada (Paramétrica)
        t_stat, p_val_ttest = stats.ttest_rel(best_f1_folds, comp_f1_folds)

        # 2. Prueba de Rangos con Signo de Wilcoxon (No Paramétrica)
        if np.all(diff == 0):
            w_stat, p_val_wilcoxon = 0.0, 1.0
        else:
            try:
                w_stat, p_val_wilcoxon = stats.wilcoxon(best_f1_folds, comp_f1_folds)
            except Exception:
                w_stat, p_val_wilcoxon = 0.0, 1.0

        # Tamaño del efecto (Cohen's d pareado)
        sd_diff = np.std(diff, ddof=1) if len(diff) > 1 else 0.0
        cohens_d = (np.mean(diff) / sd_diff) if sd_diff > 0 else 0.0

        # Intervalo de confianza del 95%
        mean_diff = np.mean(diff)
        sem_diff = stats.sem(diff) if np.std(diff) > 0 else 1e-6
        ci_95 = stats.t.interval(0.95, len(diff)-1, loc=mean_diff, scale=sem_diff)

        h0_rejected = bool(p_val_ttest < 0.05 or p_val_wilcoxon < 0.05)

        # Magnitud del efecto según Cohen
        effect_label = "Grande (d ≥ 0.8)" if abs(cohens_d) >= 0.8 else ("Medio (d ≥ 0.5)" if abs(cohens_d) >= 0.5 else "Pequeño / Despreciable")

        report["comparisons"][model_name] = {
            "comparison_model_f1": float(np.mean(comp_f1_folds)),
            "mean_f1_difference": float(mean_diff),
            "ci_95_percent": [float(ci_95[0]), float(ci_95[1])],
            "cohens_d": float(cohens_d),
            "t_student": {
                "t_statistic": float(t_stat) if not np.isnan(t_stat) else 0.0,
                "p_value": float(p_val_ttest) if not np.isnan(p_val_ttest) else 1.0
            },
            "wilcoxon_signed_rank": {
                "w_statistic": float(w_stat),
                "p_value": float(p_val_wilcoxon)
            },
            "h0_rejected": h0_rejected,
            "conclusion": "H0 Rechazada: El modelo propuesto es estadísticamente superior (p < 0.05)" if h0_rejected else "H0 No Rechazada: Rendimientos equivalentes (p >= 0.05)"
        }

        p(f"\n🔍 Comparación: [{best_model_name}] VS [{model_name}]")
        p(f"   • Diferencia Media F1 (Δ) : {mean_diff:+.4f} (IC 95%: [{ci_95[0]:.4f}, {ci_95[1]:.4f}])")
        p(f"   • Tamaño del Efecto       : Cohen's d = {cohens_d:.4f} ({effect_label})")
        p(f"   • t-Student Pareada       : t = {t_stat:.4f} | p-value = {p_val_ttest:.6f}")
        p(f"   • Wilcoxon Signed-Rank    : W = {w_stat:.4f} | p-value = {p_val_wilcoxon:.6f}")
        p(f"   • Veredicto Final         : {'✅ H0 RECHAZADA (Diferencia Significativa)' if h0_rejected else '⚖️ H0 NO RECHAZADA (Equivalencia Estadistica)'}")

    # Generación de Tabla LaTeX para Tesis
    p("\n================================================================================")
    p("4. CÓDIGO TABLA LATEX PARA MEMORIA DE TESIS")
    p("================================================================================")
    latex_code = [
        "\\begin{table}[h]",
        "\\centering",
        "\\caption{Resultados del Benchmark y Pruebas Estadísticas de Hipótesis vs. Modelo Propuesto}",
        "\\begin{tabular}{lccccc}",
        "\\hline",
        "\\textbf{Modelo} & \\textbf{F1-Score} & \\textbf{\\Delta F1 (IC 95\\%)} & \\textbf{Wilcoxon p} & \\textbf{Cohen's d} & \\textbf{Conclusión} \\\\",
        "\\hline"
    ]
    for m_name, m_metrics in sorted_models:
        f1_m = np.mean(m_metrics['f1_folds'])
        f1_s = np.std(m_metrics['f1_folds'])
        if m_name == best_model_name:
            latex_code.append(f"\\textbf{{{m_name}}} & \\textbf{{{f1_m:.4f} $\\pm$ {f1_s:.4f}}} & --- & --- & --- & \\textbf{{Campeón Propuesto}} \\\\")
        else:
            comp_info = report["comparisons"][m_name]
            d_val = comp_info['cohens_d']
            p_val = comp_info['wilcoxon_signed_rank']['p_value']
            diff_str = f"{comp_info['mean_f1_difference']:+.4f}"
            p_str = "< 0.001" if p_val < 0.001 else f"{p_val:.4f}"
            verdict = "Superior (p < 0.05)" if comp_info['h0_rejected'] else "Equivalente"
            latex_code.append(f"{m_name} & {f1_m:.4f} $\\pm$ {f1_s:.4f} & {diff_str} & {p_str} & {d_val:.2f} & {verdict} \\\\")
    latex_code.extend([
        "\\hline",
        "\\end{tabular}",
        "\\end{table}"
    ])
    p("\n".join(latex_code))

    # Exportar reporte estadístico completo
    output_path = artifacts_dir / "statistical_validation_report.json"
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2)

    p("\n================================================================================")
    p(f"✅ REPORTE ESTADÍSTICO ACTUALIZADO Y EXPORTADO A: {output_path}")
    p("================================================================================")

if __name__ == "__main__":
    run_statistical_validation()
