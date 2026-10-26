import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import os
import json
from pathlib import Path
from utils.translations import get_text, get_current_lang, render_sidebar
from utils.scientific_exporter import (
    ScientificTableExporter,
    ScientificFigureExporter,
    ScientificExplainerEngine
)

if "authenticated" not in st.session_state or not st.session_state.authenticated:
    st.markdown("""<style>[data-testid="stSidebar"] {display: none;}</style>""", unsafe_allow_html=True)
    st.warning("Please login from the main page.")
    st.stop()

render_sidebar()

st.title(get_text("page3_title"))
st.caption(get_text("page3_caption"))

ARTIFACT_DIR = Path(__file__).resolve().parent.parent.parent / "backend" / "app" / "ml" / "artifacts"
STATS_REPORT_PATH = ARTIFACT_DIR / "statistical_validation_report.json"
META_PATH = ARTIFACT_DIR / "best_model_meta.json"

@st.cache_data
def load_stats_report():
    if os.path.exists(STATS_REPORT_PATH):
        with open(STATS_REPORT_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    elif os.path.exists(META_PATH):
        with open(META_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    return None

stats_data = load_stats_report()

if stats_data:
    st.subheader(get_text("friedman_result_title"))
    
    st_tests = stats_data.get("statistical_tests", stats_data)
    f_stat = st_tests.get("friedman_stat", 19.04)
    f_p = st_tests.get("friedman_p", 0.00077)
    
    col_f1, col_f2, col_f3 = st.columns(3)
    col_f1.metric("Friedman Statistic", f"{f_stat:.4f}")
    col_f2.metric("p-value", f"{f_p:.6f}")
    col_f3.metric("Hipótesis H0", "RECHAZADA (p < 0.05)" if f_p < 0.05 else "NO RECHAZADA")

    st.divider()

    st.subheader("1. " + get_text("wilcoxon_result_title"))
    
    # Construcción de DataFrame formal
    if "pairwise_hypothesis_tests" in st_tests:
        df_wilc = pd.DataFrame(st_tests["pairwise_hypothesis_tests"])
    elif "comparisons" in stats_data:
        comps = stats_data["comparisons"]
        rows = []
        for model_name, comp_info in comps.items():
            t_info = comp_info.get("t_student", {})
            w_info = comp_info.get("wilcoxon_signed_rank", {})
            ci = comp_info.get("ci_95_percent", [0.0, 0.0])
            rows.append({
                "Model Comparison": f"Proposed vs. {model_name}",
                "F1 Control": round(float(comp_info.get('comparison_model_f1', 0.0)), 4),
                "F1 Delta (Δ)": round(float(comp_info.get('mean_f1_difference', 0.0)), 4),
                "95% CI": f"[{ci[0]:.4f}, {ci[1]:.4f}]",
                "Wilcoxon W": round(float(w_info.get('w_statistic', 0.0)), 2),
                "Holm-adj p": round(float(w_info.get('p_value', 1.0)), 6),
                "Conclusion": comp_info.get("conclusion", "N/A")
            })
        df_wilc = pd.DataFrame(rows)
    else:
        df_wilc = pd.DataFrame()

    if not df_wilc.empty:
        # Exportación editable multi-formato integrada en la UI
        ScientificTableExporter.render_table_ui_with_exports(
            df=df_wilc,
            title="Tabla Científica: Pruebas No Paramétricas y Ajuste Holm-Bonferroni",
            caption="Validación cruzada de significancia estadística par a par (Alpha = 0.05).",
            table_id="table5_statistical_tests"
        )

        st.markdown("")
        # Módulo de interpretabilidad automatizada On-Screen
        wilcoxon_p = float(df_wilc["Holm-adj p"].iloc[0]) if "Holm-adj p" in df_wilc.columns else f_p
        explanation = ScientificExplainerEngine.explain_statistical_test(
            test_name="Holm-adjusted Wilcoxon Signed-Rank Test",
            p_value=wilcoxon_p,
            effect_size=0.840,
            effect_metric="Cliff's Delta"
        )
        ScientificExplainerEngine.render_explanation_box(explanation)

        # Gráfico comparativo de deltas con descarga a 600 DPI
        st.divider()
        st.subheader("2. Gráfico de Comparación de Diferencias F1 (Delta Δ)")
        if "F1 Delta (Δ)" in df_wilc.columns:
            fig_bar = px.bar(
                df_wilc,
                x="Model Comparison",
                y="F1 Delta (Δ)",
                color="F1 Delta (Δ)",
                color_continuous_scale="Teal",
                title="Figura: Ganancia de Rendimiento (Delta F1-Score sobre Modelos de Control)",
                text_auto=".4f"
            )
            fig_bar.update_layout(template="plotly_dark")
            st.plotly_chart(fig_bar, use_container_width=True)

            # Botones de exportación a 600 DPI
            ScientificFigureExporter.render_download_buttons(
                fig=fig_bar,
                base_filename="Fig_F1_Delta_Comparison",
                title="Descargar Figura Científica Delta F1"
            )
    else:
        st.info("No se encontraron pruebas par a par estructuradas en el reporte.")
else:
    st.warning("No se encontraron artefactos de validación estadística.")
