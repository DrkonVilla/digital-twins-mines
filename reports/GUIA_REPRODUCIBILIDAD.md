# GUÍA MAESTRA DE REPRODUCIBILIDAD CIENTÍFICA DEL PROYECTO M-11

**Proyecto:** Implementación de un gemelo digital para la alerta temprana de riesgos de interacción hombre-máquina en frentes de extracción subterránea  
**Manuscrito Destino:** *Acta Montanistica Slovaca*  
**Fecha:** Octubre 2026  
**Estándar de Calidad:** Reproducibilidad determinista de extremo a extremo (código, semillas, hiperparámetros y datos)  

---

## 1. REQUISITOS DEL ENTORNO Y DEPENDENCIAS

El sistema ha sido probado y auditado en entornos Windows 10/11 y Linux (Ubuntu 22.04+).

### 1.1. Versión de Python
- **Python:** `3.10.x` o `3.11.x` (probado en Python 3.10.11 de 64 bits).

### 1.2. Instalación de Dependencias
Desde la raíz del repositorio (`digital-twins-mines`):

```bash
# 1. Crear y activar entorno virtual (opcional pero recomendado)
python -m venv venv
venv\Scripts\activate      # En Windows PowerShell / CMD
# source venv/bin/activate  # En Linux / macOS

# 2. Instalar dependencias científicas requeridas
pip install --upgrade pip
pip install -r requirements.txt
pip install shap  # Motor TreeSHAP
```

### 1.3. Librerías Clave y Versiones Verificadas
- `numpy==1.26.4`
- `pandas==2.2.3`
- `scikit-learn==1.7.2`
- `xgboost==2.1.4` (o `3.2.0`)
- `imbalanced-learn==0.14.0`
- `scipy==1.15.3`
- `shap==0.49.1`
- `fastapi==0.115.11`
- `uvicorn==0.34.0`
- `matplotlib>=3.8.0`
- `seaborn>=0.13.0`

---

## 2. EJECUCIÓN REPRODUCIBLE CON UN SOLO COMANDO

Para regenerar de forma totalmente desatendida y determinista el conjunto completo de tablas experimentales, métricas, modelos, matrices y figuras, ejecute el script maestro:

```bash
python backend/scripts/run_all_experiments.py
```

Este script ejecuta secuencialmente y con trazabilidad los siguientes 7 módulos:

1. **`train_cv.py`:** Ejecuta la evaluación simétrica de los 6 clasificadores (XGBoost, Random Forest, SVM RBF, MLP, Stacking, Voting) y los 2 baselines TTC (Fixed y Tuned) bajo 5-Fold Stratified CV y test holdout del 20 %, generando `results/fair_comparison_results.json`.
2. **`run_ablation_study.py`:** Evalúa de forma aislada las 8 configuraciones de ablación multimodal (A a G, incluyendo la configuración crítica B2), calculando deltas en $\text{pp}$ y $\%$, generando `results/ablation_study_results.json`.
3. **`audit_label_circularity.py`:** Ejecuta la descomposición cuantitativa de varianza (82,1 % espacial/cinemática) y evalúa los escenarios con etiquetas desacopladas, generando `results/label_circularity_audit.json`.
4. **`run_shap_and_collinearity.py`:** Calcula las atribuciones TreeSHAP globales sobre el modelo y la matriz de correlación de Spearman, generando `results/shap_values.csv`, `figures/shap_summary.png` y `figures/correlaciones.png`.
5. **`benchmark_hardware_profiler.py`:** Mide el rendimiento y la latencia E2E a 5 Hz para 50, 100, 200 y 500 agentes con desglose por etapas, generando `results/hardware_specs_benchmark.json`.
6. **`audit_genai_protocol.py`:** Evalúa el banco de 100 escenarios mineros contra el motor determinista de seguridad, generando `results/genai_audit_bank.json` y la plantilla de revisión humana `results/genai_audit_review_sheet.csv`.
7. **`generate_all_deliverables.py`:** Compila y formatea todos los archivos CSV en `results/`, genera los gráficos en `figures/` y calcula los checksums criptográficos SHA256 en `results/reproducibility_manifest.json`.

Tiempo estimado de ejecución completa: **~4 a 6 minutos** en un procesador Intel Core i7 / AMD Ryzen equivalente.

---

## 3. MAPA DE ARTEFACTOS GENERADOS

Al finalizar la ejecución, la estructura de entregables queda organizada de la siguiente manera:

```text
results/
  ├── feature_dictionary.csv          # Diccionario completo de 37 variables
  ├── experiment_config.json          # Metadatos del entorno, versiones y semillas
  ├── model_hyperparameters.csv       # Hiperparámetros y espacios de búsqueda
  ├── metrics_comparison.csv          # Métricas holdout calibradas y argmax
  ├── paired_statistical_tests.csv    # Bootstrap pareado, McNemar exacto y Holm
  ├── confusion_matrices.csv          # Matrices 3x3 (BAJO, MEDIO, ALTO)
  ├── cv_results.csv                  # Métricas de validación cruzada por pliegue
  ├── ablation_results.csv            # Estudio de ablación multimodal (A-G)
  ├── circularity_audit.csv           # Descomposición de varianza del target
  ├── decoupled_labels_results.csv    # Evaluación en escenarios de riesgo no cinemático
  ├── shap_values.csv                 # Valores medios TreeSHAP por predictor
  ├── benchmark_latency.csv           # Latencias E2E (P50, P95, P99) a 5 Hz
  ├── benchmark_fps.csv               # Rendimiento de renderizado Three.js cliente
  ├── gemini_audit.csv                # Banco de 100 escenarios y reglas de seguridad
  └── reproducibility_manifest.json   # Checksums SHA256 de todos los artefactos

figures/
  ├── comparacion_modelos.png         # Gráfico de barras comparativo (Recall, F2, Precision)
  ├── matriz_confusion.png            # Heatmaps de confusión (XGB, RF, TTC tuned)
  ├── ablacion.png                    # Impacto Delta F2 en puntos porcentuales
  ├── correlaciones.png               # Matriz de Spearman (evidencia de colinealidad)
  ├── shap_summary.png                # Gráfico de barras e impacto global TreeSHAP
  ├── benchmark_latencia.png          # Curvas de latencia E2E vs umbral 200 ms
  └── benchmark_fps.png               # Rendimiento de renderizado en Chromium

reports/
  ├── AUDITORIA_INICIAL_M11.md        # Matriz cruzada de observaciones de revisores
  ├── CORRECCIONES_IMPLEMENTADAS.md   # Bitácora detallada de cambios de software
  ├── RESULTADOS_EXPERIMENTALES.md    # Reporte exhaustivo de resultados y métricas
  ├── MATRIZ_RESPUESTA_REVISORES.md   # Matriz formal de respuesta con estados
  ├── LIMITACIONES_PENDIENTES.md      # Declaración explícita de limitaciones
  └── GUIA_REPRODUCIBILIDAD.md        # Esta guía de reproducción
```

---

## 4. VERIFICACIÓN DE INTEGRIDAD Y DETERMINISMO (SHA256)

El archivo `results/reproducibility_manifest.json` contiene la huella criptográfica SHA256 de:
- El archivo de datos oficial: `data/raw/public_mining_equipment_dataset.csv`.
- Todos los scripts ejecutables en `backend/scripts/`.
- Todos los archivos tabulares de resultados en `results/`.
- Todas las figuras en `figures/`.

Cualquier alteración en los datos de entrada o en la semilla (`RANDOM_STATE = 42`) provocará un cambio verificable en los hashes SHA256 del manifiesto, garantizando integridad contra alteraciones ad-hoc.

---

## 5. EJECUCIÓN DEL GEMELO DIGITAL INTERACTIVO (BACKEND Y FRONTEND)

Para operar el sistema ciberfísico interactivo en tiempo real:

### 5.1. Levantar el Backend FastAPI (Servidor WebSockets a 5 Hz)
En una terminal:
```bash
uvicorn backend.app.main:app --host 0.0.0.0 --port 8000 --reload
```
Verifique la API en: `http://localhost:8000/docs`.

### 5.2. Levantar el Frontend 3D (Next.js / Three.js)
En una segunda terminal:
```bash
cd frontend
npm install
npm run dev
```
Abra el navegador en: `http://localhost:3000`. El gemelo digital conectará automáticamente con el flujo WebSocket en `ws://localhost:8000/ws/telemetry`, renderizando la galería subterránea, los operarios mineros, el equipo Scoop/LHD y las alertas en tiempo real.
