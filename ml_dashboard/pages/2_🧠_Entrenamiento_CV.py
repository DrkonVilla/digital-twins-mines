import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as gg
import os
import json
import joblib
from pathlib import Path
from utils.translations import get_text, get_current_lang, render_sidebar
from utils.data_generator import generate_mining_telemetry_dataset

if "authenticated" not in st.session_state or not st.session_state.authenticated:
    st.markdown("""<style>[data-testid="stSidebar"] {display: none;}</style>""", unsafe_allow_html=True)
    st.warning("Please login from the main page.")
    st.stop()

render_sidebar()

st.title(get_text("page2_title"))
st.caption(get_text("page2_caption"))

ARTIFACT_DIR = Path(__file__).resolve().parent.parent.parent / "backend" / "app" / "ml" / "artifacts"
CV_METRICS_PATH = ARTIFACT_DIR / "cv_metrics_results.json"
META_PATH = ARTIFACT_DIR / "best_model_meta.json"

@st.cache_data
def load_cv_data():
    cv_data = None
    meta_data = None
    if os.path.exists(CV_METRICS_PATH):
        with open(CV_METRICS_PATH, "r", encoding="utf-8") as f:
            cv_data = json.load(f)
    if os.path.exists(META_PATH):
        with open(META_PATH, "r", encoding="utf-8") as f:
            meta_data = json.load(f)
    return cv_data, meta_data

cv_results, meta_info = load_cv_data()

# Botón para ejecutar el pipeline de entrenamiento
col_tr1, col_tr2 = st.columns([3, 1])
with col_tr1:
    st.info(get_text("run_pipeline_info"))
with col_tr2:
    if st.button(get_text("run_pipeline_btn"), type="primary", use_container_width=True):
        with st.spinner("Training models with Stratified 5-Fold CV..."):
            from backend.scripts.train_cv import train_and_evaluate_cv
            from backend.scripts.robust_stats_validation import run_robust_stats_validation
            train_and_evaluate_cv()
            run_robust_stats_validation()
            st.cache_data.clear()
            st.success("¡Pipeline OK!")
            st.rerun()

st.divider()

if cv_results:
    # 1. Tabla Comparativa de Rendimiento
    st.subheader(get_text("table2_title"))
    
    summary_rows = []
    champion_name = meta_info.get("model_name", "Voting Classifier") if meta_info else ""
    
    for model_name, folds in cv_results.items():
        accs = [f["accuracy"] for f in folds]
        f1s = [f["f1_macro"] for f in folds]
        recs = [f["recall_macro"] for f in folds]
        aucs = [f["auc_roc"] for f in folds]
        inf_times = [f["inference_time_ms"] for f in folds]
        
        is_champion = (model_name == champion_name)
        badge = "🏆 " + get_text("champion_model") if is_champion else "⚪ Evaluated"
        
        summary_rows.append({
            "Status": badge,
            "Architecture": model_name,
            get_text("metric_accuracy"): f"{np.mean(accs):.4f} ± {np.std(accs):.4f}",
            get_text("metric_f1"): f"{np.mean(f1s):.4f}",
            get_text("metric_recall"): f"{np.mean(recs):.4f}",
            get_text("metric_auc"): f"{np.mean(aucs):.4f}",
            "Inference Time (ms)": f"{np.mean(inf_times):.2f} ms"
        })
        
    df_summary = pd.DataFrame(summary_rows)
    st.dataframe(df_summary, use_container_width=True)

    # 1b. Comparación SIMÉTRICA con umbral F2 idéntico para todos los modelos (revisión por pares G27, FON-01/02)
    fair_path = ARTIFACT_DIR / "fair_comparison_results.json"
    if fair_path.exists():
        with open(fair_path, "r", encoding="utf-8") as f:
            fair = json.load(f)
        st.subheader("Comparación simétrica — clase ALTO (umbral F2 calibrado igual para todos)")
        st.caption(
            "Todos los modelos usan el mismo protocolo: SMOTENC dentro de cada pliegue, umbral F2 elegido sobre "
            "probabilidades OOF del entrenamiento y evaluación única sobre el 20 % de prueba. "
            "El baseline determinista se evalúa con la misma partición y el mismo bootstrap pareado."
        )
        fair_rows = []
        for mname, res in fair["models"].items():
            c, a = res["test_calibrated"], res["test_argmax"]
            ci = res["bootstrap_calibrated"]["f2"]["ci95"]
            fair_rows.append({
                "Sistema": mname,
                "Umbral F2": f"{res['calibration']['threshold_alto']:.2f}",
                "Precisión ALTO": f"{c['precision_alto']:.3f}",
                "Recall ALTO": f"{c['recall_alto']:.3f}",
                "F2 ALTO (IC95 bootstrap)": f"{c['f2_alto']:.3f} [{ci[0]:.3f}, {ci[1]:.3f}]",
                "AUC-ROC ALTO": f"{c['auc_roc_alto']:.3f}",
                "AUC-PR ALTO": f"{c['auc_pr_alto']:.3f}",
                "F2 con argmax": f"{a['f2_alto']:.3f}",
            })
        for bname, b in fair["baselines"].items():
            ci = b["bootstrap"]["f2"]["ci95"]
            fair_rows.append({
                "Sistema": bname,
                "Umbral F2": "regla fija" if "fixed" in bname else f"TTC<{b['ttc_threshold_s']:.0f}s",
                "Precisión ALTO": f"{b['test']['precision_alto']:.3f}",
                "Recall ALTO": f"{b['test']['recall_alto']:.3f}",
                "F2 ALTO (IC95 bootstrap)": f"{b['test']['f2_alto']:.3f} [{ci[0]:.3f}, {ci[1]:.3f}]",
                "AUC-ROC ALTO": "—", "AUC-PR ALTO": "—", "F2 con argmax": "—",
            })
        st.dataframe(pd.DataFrame(fair_rows), use_container_width=True)

        ref = fair["paired_comparisons"]["reference"]
        cmp_rows = []
        for other, r in fair["paired_comparisons"]["calibrated"].items():
            d = r["delta_f2_ref_minus_other"]
            cmp_rows.append({
                "Comparación": f"{ref} vs {other}",
                "ΔF2 (IC95 pareado)": f"{d['mean']:+.4f} [{d['ci95'][0]:+.4f}, {d['ci95'][1]:+.4f}]",
                "McNemar recall p (Holm)": f"{r['mcnemar_recall']['p_holm']:.4f}",
                "McNemar decisión p (Holm)": f"{r['mcnemar_decision']['p_holm']:.4f}",
                "Cliff's δ": f"{r['cliffs_delta_f2_bootstrap']:+.2f} ({r['cliffs_delta_label']})",
            })
        st.markdown(f"**Pruebas pareadas sobre las mismas predicciones (referencia: {ref})**")
        st.dataframe(pd.DataFrame(cmp_rows), use_container_width=True)
        st.warning(
            "El target `risk_level` es sintético y comparte variables con el baseline (ver "
            "`results/label_circularity_audit.json`). Estos resultados no constituyen validación de campo."
        )
    else:
        st.info("Ejecute el pipeline para generar `fair_comparison_results.json` (comparación simétrica).")

    
    st.divider()
    
    # 2. Boxplot de Estabilidad (Figura 5)
    st.subheader(get_text("fig5_title"))
    
    boxplot_data = []
    for model_name, folds in cv_results.items():
        for fold in folds:
            boxplot_data.append({
                "Modelo": model_name,
                "Fold": f"Fold {fold['fold']}",
                "Accuracy": fold["accuracy"]
            })
    df_box = pd.DataFrame(boxplot_data)
    fig5 = px.box(df_box, x="Modelo", y="Accuracy", color="Modelo", points="all")
    st.plotly_chart(fig5, use_container_width=True)

    st.divider()

    # 3. Matriz de Ponderación Multicriterio de Negocio (Business Multi-Criteria Decision Matrix)
    st.subheader(get_text("business_scoring_title"))
    st.caption(get_text("business_scoring_caption"))

    # Configuración de Ponderaciones Interactivas
    with st.expander(get_text("weights_config_title"), expanded=False):
        col_w1, col_w2, col_w3, col_w4 = st.columns(4)
        with col_w1:
            w_perf = st.slider(get_text("weight_perf_label"), min_value=0.0, max_value=1.0, value=0.40, step=0.05)
        with col_w2:
            w_lat = st.slider(get_text("weight_latency_label"), min_value=0.0, max_value=1.0, value=0.25, step=0.05)
        with col_w3:
            w_interp = st.slider(get_text("weight_interp_label"), min_value=0.0, max_value=1.0, value=0.20, step=0.05)
        with col_w4:
            w_maint = st.slider(get_text("weight_maint_label"), min_value=0.0, max_value=1.0, value=0.15, step=0.05)

    total_w = w_perf + w_lat + w_interp + w_maint
    if total_w == 0:
        total_w = 1.0

    # Calificaciones intrínsecas de interpretabilidad y mantenibilidad técnica para minería (1 a 10)
    intrinsic_ratings = {
        "RandomForest": {"interp": 9.5, "maint": 9.5, "desc": "Árboles interpretables, Feature Importances directas, serialización nativa Scikit-Learn."},
        "XGBoost": {"interp": 8.5, "maint": 9.0, "desc": "Gradient Boosting de alto rendimiento, soporte nativo de TreeSHAP y bajo consumo de memoria."},
        "Voting_Ensemble": {"interp": 7.5, "maint": 7.5, "desc": "Ensamble ponderado por votación blanda, robusto pero requiere orquestar múltiples modelos."},
        "Stacking_Ensemble": {"interp": 6.0, "maint": 6.5, "desc": "Meta-modelo de dos niveles con mayor complejidad computacional de despliegue."},
        "MLP_NeuralNet": {"interp": 4.0, "maint": 5.5, "desc": "Red neuronal de caja negra, alta sensibilidad a normalización y calibración."}
    }

    # Recopilar métricas promedio para cada modelo desde cv_results
    model_stats = {}
    inf_times_all = []
    for model_name, folds in cv_results.items():
        f1_mean = float(np.mean([f["f1_macro"] for f in folds]))
        auc_mean = float(np.mean([f["auc_roc"] for f in folds]))
        inf_mean = float(np.mean([f["inference_time_ms"] for f in folds]))
        inf_times_all.append(inf_mean)
        model_stats[model_name] = {
            "f1": f1_mean,
            "auc": auc_mean,
            "perf": (f1_mean + auc_mean) / 2.0,
            "inf_time": inf_mean
        }

    min_t = min(inf_times_all) if inf_times_all else 0.001
    max_t = max(inf_times_all) if inf_times_all else 1.0

    # Calcular puntuaciones de negocio dinámicamente
    business_rows = []
    for model_name, stats in model_stats.items():
        ratings = intrinsic_ratings.get(model_name, {"interp": 7.0, "maint": 7.0, "desc": "Arquitectura estándar"})
        
        # Puntuación de latencia normalizada (1.0 = más rápido)
        if max_t != min_t:
            lat_score = 1.0 - (stats["inf_time"] - min_t) / (max_t - min_t)
        else:
            lat_score = 1.0
            
        interp_score = ratings["interp"] / 10.0
        maint_score = ratings["maint"] / 10.0
        
        raw_business_score = (
            (stats["perf"] * w_perf) +
            (lat_score * w_lat) +
            (interp_score * w_interp) +
            (maint_score * w_maint)
        ) / total_w
        
        business_score_pct = raw_business_score * 100.0
        
        business_rows.append({
            "model_name": model_name,
            "perf_raw": stats["perf"],
            "f1": stats["f1"],
            "auc": stats["auc"],
            "inf_time": stats["inf_time"],
            "lat_score": lat_score,
            "interp": ratings["interp"],
            "maint": ratings["maint"],
            "desc": ratings["desc"],
            "score_pct": business_score_pct
        })

    # Ordenar por puntuación de negocio descendente
    business_rows.sort(key=lambda x: x["score_pct"], reverse=True)
    winner = business_rows[0]

    # Banner tipo Trofeo / Decisión Ejecutiva para Gerencia
    col_lead1, col_lead2 = st.columns([1, 2])
    with col_lead1:
        st.markdown(f"""
        <div style="background: linear-gradient(135deg, #1e3a8a, #0284c7); padding: 22px; border-radius: 14px; text-align: center; color: white; box-shadow: 0 4px 14px rgba(0,0,0,0.3);">
            <div style="font-size: 38px; margin-bottom: 4px;">🏆</div>
            <div style="font-size: 13px; text-transform: uppercase; letter-spacing: 1px; opacity: 0.85;">{get_text("business_winner_badge")}</div>
            <div style="font-size: 22px; font-weight: 800; margin: 6px 0;">{winner['model_name']}</div>
            <div style="font-size: 15px; opacity: 0.95;">{get_text('business_score_col')}: <strong>{winner['score_pct']:.2f}%</strong></div>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("<div style='margin-top: 10px;'></div>", unsafe_allow_html=True)
        c_m1, c_m2 = st.columns(2)
        c_m1.metric("F1-Score", f"{winner['f1']:.4f}")
        c_m2.metric("Latencia", f"{winner['inf_time']:.2f} ms")

    with col_lead2:
        st.markdown(f"**{get_text('business_scoring_title')} — Justificación Operacional:**")
        st.info(f"💡 **Criterio de Selección Gerencial:** {winner['desc']}")
        
        # Tabla comparativa de negocio formateada
        display_table = []
        for rank_idx, r in enumerate(business_rows, start=1):
            badge = "🏆 " + get_text("business_winner_badge") if rank_idx == 1 else ("⭐ " + get_text("business_recommended_badge") if rank_idx == 2 else f"#{rank_idx}")
            display_table.append({
                "Ranking": badge,
                "Arquitectura": r["model_name"],
                get_text("business_score_col"): f"{r['score_pct']:.2f}%",
                "Rendimiento (F1+AUC)": f"{r['perf_raw']:.4f}",
                "Latencia Inferencia": f"{r['inf_time']:.2f} ms",
                "Interpretabilidad": f"{r['interp']:.1f}/10",
                "Mantenibilidad": f"{r['maint']:.1f}/10"
            })
        st.dataframe(pd.DataFrame(display_table), use_container_width=True)

    # Gráfico de barras comparativo de Puntuación Ponderada de Negocio
    fig_score = px.bar(
        pd.DataFrame(business_rows),
        x="model_name",
        y="score_pct",
        color="score_pct",
        color_continuous_scale="Blues",
        labels={"model_name": "Arquitectura", "score_pct": "Puntuación de Negocio (%)"},
        title=f"Comparativa de Puntuación Ponderada de Negocio (Total = 100%)",
        text=pd.DataFrame(business_rows)["score_pct"].apply(lambda v: f"{v:.2f}%")
    )
    fig_score.update_traces(textposition='outside')
    fig_score.update_layout(yaxis=dict(range=[0, 115]), coloraxis_showscale=False)
    st.plotly_chart(fig_score, use_container_width=True)
