# Plan de Correcciones del Software y Pipeline de IA (M-11)
> **Basado en el Informe de Revisión por Pares (G27) — Manuscrito para *Acta Montanistica Slovaca***  
> **Proyecto:** Gemelo Digital Minero para Alerta Temprana de Riesgos de Interacción Hombre-Máquina (M-11)  
> **Fecha:** Octubre 2026

---

## 1. Justificación y Alcance

El informe de revisión por pares otorgó una calificación de **11.89/20 (*Major Revisions*)**, concluyendo que **las tablas, métricas y afirmaciones del artículo no se pueden corregir mediante simple redacción**. Existen sesgos metodológicos y vacíos de reproducibilidad en el código fuente que deben subsanarse en el software antes de regenerar los datos del manuscrito.

Este plan detalla las modificaciones técnicas, scripts a implementar y validaciones experimentales requeridas en el repositorio `digital-twins-mines`.

---

## 2. Mapa de Archivos del Software Afectados

```
digital-twins-mines/
├── backend/
│   ├── app/
│   │   ├── ml/artifacts/                 # Destino de artefactos re-entrenados
│   │   └── services/
│   │       └── gemini_service.py          # Auditoría de prompts y alucinación
│   └── scripts/
│       ├── train_cv.py                    # Calibración simétrica F2 y anidamiento CV
│       ├── train_all_models.py            # Pipeline con ImbPipeline y umbrales
│       ├── robust_stats_validation.py     # Pruebas estadísticas pareadas
│       ├── run_ablation_study.py          # [NUEVO] Script formal de ablación multimodal
│       ├── audit_genai_protocol.py        # [NUEVO] Protocolo automatizado de auditoría GenAI
│       └── benchmark_hardware.py          # [NUEVO] Registro de hardware y perfilador de latencia
├── data/
│   └── raw/
│       └── public_mining_equipment_dataset.csv  # Verificación de circularidad de etiquetas
├── requirements.txt                       # [NUEVO/ACTUALIZAR] Dependencias fijadas
└── ml_dashboard/
    └── pages/
        ├── 2_🧠_Entrenamiento_CV.py       # Reflejar calibración simétrica
        └── 3_📉_Pruebas_Estadisticas.py   # Actualizar con nuevas métricas
```

---

## 3. Matriz Detallada de Tareas Técnicas en el Software

### Módulo 1: Calibración Simétrica de Umbrales de Clasificación ($F_2$)
* **Código de Hallazgo:** `FON-01` (Gravedad: **Crítica**)
* **Archivos a modificar:**  
  * `backend/scripts/train_cv.py`  
  * `backend/scripts/train_all_models.py`
* **Problema:**  
  En el estudio previo, XGBoost fue evaluado con un umbral optimizado para $F_2$ ($0.35$ para la clase ALTO), mientras que Random Forest, SVM y Red Neuronal se evaluaron con el umbral por defecto (*argmax* / 0.50). Esta disparidad invalida la conclusión de que XGBoost es superior en recall.
* **Acciones en el software:**
  1. Implementar una función `optimize_threshold_f2(y_val, y_proba_val)` en el pipeline.
  2. Aplicar el mismo algoritmo de búsqueda de umbral que maximice $F_2$ en el conjunto de validación para **todos** los modelos comparados (Random Forest, XGBoost, MLP, Stacking y Voting).
  3. Exportar curvas Precision-Recall (PR) completas y tablas de sensibilidad al umbral ($[0.10, 0.90]$ en pasos de $0.05$).
  4. Guardar los resultados en `cv_metrics_results.json` registrando para cada modelo:
     * Umbral óptimo calculado.
     * Recall, Precisión, $F_1$, $F_2$ y AUC-PR bajo dicho umbral.

```python
# Función a incorporar en train_cv.py / train_all_models.py
def find_optimal_fbeta_threshold(y_true, y_prob_high_risk, beta=2.0):
    best_thresh, best_fbeta = 0.5, 0.0
    for thresh in np.linspace(0.1, 0.9, 81):
        y_pred = (y_prob_high_risk >= thresh).astype(int)
        p = precision_score(y_true, y_pred, zero_division=0)
        r = recall_score(y_true, y_pred, zero_division=0)
        if (beta**2 * p + r) > 0:
            f = (1 + beta**2) * (p * r) / (beta**2 * p + r)
            if f > best_fbeta:
                best_fbeta = f
                best_thresh = thresh
    return best_thresh, best_fbeta
```

---

### Módulo 2: Validación Cruzada Estratificada y Aislamiento de SMOTE
* **Código de Hallazgo:** `FON-02` (Gravedad: **Crítica**)
* **Archivos a modificar:**  
  * `backend/scripts/train_cv.py`  
  * `backend/scripts/train_all_models.py`
* **Problema:**  
  El informe cuestiona si SMOTE y el escalado de características se aplicaron fuera de los pliegues de validación cruzada, provocando fuga de datos (*data leakage*).
* **Acciones en el software:**
  1. Asegurar que **todo** remuestreo sintético (SMOTE) y escalado (`StandardScaler`) esté encapsulado exclusivamente dentro del fold de entrenamiento mediante `imblearn.pipeline.Pipeline`.
  2. Implementar `SMOTENC` si existen variables categóricas para evitar sintetizar valores flotantes en variables discretas.
  3. Agregar en el script un análisis de sensibilidad comparativo ejecutando el entrenamiento **con SMOTE** vs **sin SMOTE** (usando `class_weight='balanced'`), guardando ambos resultados en el artefacto JSON.

---

### Módulo 3: Auditoría y Desacoplamiento de la Etiqueta de Riesgo
* **Código de Hallazgo:** `FON-03` (Gravedad: **Mayor**)
* **Archivos a revisar/modificar:**  
  * `backend/scripts/download_and_process_public_dataset.py`  
  * Generadores de datos y reglas deterministas de baseline.
* **Problema:**  
  Sospecha de circularidad metodológica: si la columna `risk_level` fue etiquetada usando fórmulas directas basadas en TTC ($TTC < 2.0\text{ s}$) y distancia ($distancia < 3.0\text{ m}$), y el baseline determinista usa exactamente esas mismas reglas, la comparación entre ML y baseline carece de validez empírica.
* **Acciones en el software:**
  1. Documentar en el script el algoritmo generador de la variable objetivo `risk_level`.
  2. Demostrar independencia o desacoplamiento matemático entre la regla del baseline y la etiqueta ground truth (incorporando ruido operacional, variables fisiológicas de fatiga/BPM, estados mecánicos y condiciones ambientales).
  3. Crear una prueba de correlación y concordancia (coeficiente Kappa de Cohen) entre la regla pura del baseline y el target real.

---

### Módulo 4: Script Formal del Estudio de Ablación Multimodal
* **Código de Hallazgo:** `FON-04` (Gravedad: **Crítica**)
* **Nuevo script a crear:**  
  * `backend/scripts/run_ablation_study.py`
* **Problema:**  
  En la Tabla 6 del manuscrito, la exclusión de `distance_3d` mostraba paradójicamente un incremento en $F_2$, contradiciendo la hipótesis central de que la distancia 3D y la cinemática son indispensables.
* **Acciones en el software:**
  1. Crear un script automatizado que evalúe 5 configuraciones de ablación bajo exactamente las mismas semillas y pliegues:
     * **Configuración A (Modelo Completo):** 16 variables (cinemática + biomecánica + ambiental + telemetría CAN).
     * **Configuración B (Sin Distancia 3D / Posicionamiento):** Excluye `distance_3d`, `relative_speed`, `ttc`.
     * **Configuración C (Solo Posicionamiento / Cinemática):** Excluye telemetría ambiental y fisiológica.
     * **Configuración D (Sin Biomecánica):** Excluye `worker_bpm`, `fatigue_index`.
     * **Configuración E (Sin Telemetría Ambiental / CAN):** Excluye gases, polvo, vibración, etc.
  2. Generar automáticamente un archivo `reports_output/ablation_study_results.json` con:
     * Precisión, Recall, $F_1$, $F_2$, AUC-ROC.
     * Cambio relativo ($\Delta\%$) y cambio absoluto ($\Delta\text{ pp}$) debidamente separados para evitar confusiones de formato.

---

### Módulo 5: Protocolo y Script de Auditoría del Motor GenAI (Gemini)
* **Código de Hallazgo:** `FON-06` (Gravedad: **Mayor**)
* **Nuevo script a crear:**  
  * `backend/scripts/audit_genai_protocol.py`
* **Problema:**  
  El artículo citaba una *"tasa de alucinación del 2.0%"* y *"acuerdo de supervisor del 94.0%"* en las alertas de Gemini, pero no existía ningún script ni protocolo reproducible que respaldara esos números.
* **Acciones en el software:**
  1. Construir un banco de pruebas de $N = 100$ escenarios de emergencia sintéticos controlados que cubran la normativa peruana (D.S. 024-2016-EM) y estándares OSHA (29 CFR 1926.651).
  2. El script consultará el servicio Gemini (`gemini_service.py`), guardará las respuestas en JSON y las confrontará con una matriz de reglas esperadas:
     * Verificación de protocolos obligatorios (e.g. parada de emergencia del ScoopTram, evacuación de frente ciego, ventilación).
     * Detección de alucinaciones (mención de equipos no presentes, procedimientos contradictorios).
  3. Calcular métricas estadísticas reproducibles:
     * Tasa de alucinación con intervalo de confianza de Wilson al 95%.
     * Concordancia normativa (Kappa de Fleiss o Cohen).
     * Latencia media y P95 de la respuesta de la API.

---

### Módulo 6: Perfilador de Hardware y Benchmark de Latencia
* **Código de Hallazgo:** `FON-10` (Gravedad: **Mayor**)
* **Nuevo script a crear:**  
  * `backend/scripts/benchmark_hardware_profiler.py`
* **Problema:**  
  El benchmark reportaba latencia P95 $< 200\text{ ms}$ en hardware *"x86-64 de ocho núcleos"* sin especificar modelo de CPU, tarjeta gráfica, VRAM ni entorno de red.
* **Acciones en el software:**
  1. Crear un script que emplee `platform`, `psutil` y librerías de GPU (e.g., `torch.cuda` o WMI de Windows) para registrar automáticamente en los reportes:
     * Procesador exacto (e.g., AMD Ryzen 7 5800H @ 3.2 GHz / Intel Core i7-11800H).
     * Cantidad de núcleos físicos y lógicos.
     * Memoria RAM disponible y utilizada.
     * Modelo de GPU dedicada e integrada, versión de drivers y VRAM.
     * Sistema Operativo, compilación y versión de Python.
  2. Ejecutar la simulación de carga con 50, 100, 200 y 500 agentes simultáneos midiendo:
     * Latencia de inferencia pura de ML (ms).
     * Latencia de transporte WebSocket (ms).
     * Cuadros por segundo (FPS) en Three.js con `InstancedMesh`.

---

### Módulo 7: Gestión de Dependencias y Reproducibilidad
* **Código de Hallazgo:** Evaluación de Reproducibilidad (Sección 10)
* **Archivos a crear/actualizar:**  
  * `requirements.txt` (raíz del proyecto)
  * `backend/scripts/export_environment_metadata.py`
* **Acciones en el software:**
  1. Generar un `requirements.txt` en la raíz congelando las versiones exactas (`xgboost==2.1.3`, `scikit-learn==1.5.2`, `imbalanced-learn==0.12.3`, `fastapi`, `streamlit`, `three.js/r3f`).
  2. Crear un archivo `DATASET_CHECKSUM.sha256` para certificar la integridad del archivo CSV oficial `public_mining_equipment_dataset.csv`.

---

## 4. Roadmap de Ejecución Recomendado

```
[Paso 1: Dependencias]
    Congelar requirements.txt en la raíz y verificar versiones.
         │
         ▼
[Paso 2: Calibración F2 Simétrica]
    Implementar función de optimización de umbral F2 en train_cv.py y train_all_models.py.
         │
         ▼
[Paso 3: Validación Cruzada & SMOTE]
    Verificar ImbPipeline por pliegue y correr prueba con y sin SMOTE.
         │
         ▼
[Paso 4: Re-ejecución de Modelos]
    Re-entrenar y exportar cv_metrics_results.json y curvas PR.
         │
         ▼
[Paso 5: Estudio de Ablación]
    Ejecutar run_ablation_study.py y generar ablation_study_results.json.
         │
         ▼
[Paso 6: Auditoría GenAI]
    Ejecutar audit_genai_protocol.py sobre los 100 escenarios normativos.
         │
         ▼
[Paso 7: Benchmark de Hardware]
    Correr benchmark_hardware_profiler.py y extraer perfil de latencia y FPS.
         │
         ▼
[Paso 8: Actualización del Manuscrito]
    Con los archivos JSON consolidados, actualizar Tablas 2, 4 y 6 y conclusiones en Word.
```

---

## 5. Resumen de Entregables de Software

Al concluir este plan, el repositorio contará con los siguientes artefactos verificables:

| Artefacto / Archivo generado | Propósito metodológico | Hallazgo que resuelve |
| :--- | :--- | :--- |
| `cv_metrics_results.json` | Métricas con umbral $F_2$ simétrico para todos los modelos | `FON-01` |
| `ablation_study_results.json` | Variación real de métricas al remover subsistemas | `FON-04` |
| `genai_audit_results.json` | Tasa de alucinación documentada con IC 95% ($N \ge 100$) | `FON-06` |
| `hardware_specs_benchmark.json` | Registro auditable de CPU, GPU, RAM y latencia P95 | `FON-10` |
| `requirements.txt` | Reproducibilidad de paquetes Python | Sección 10 |
