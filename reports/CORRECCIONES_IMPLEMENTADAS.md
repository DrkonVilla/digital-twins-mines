# REGISTRO DETALLADO DE CORRECCIONES IMPLEMENTADAS EN EL SOFTWARE M-11

**Proyecto:** Implementación de un gemelo digital para la alerta temprana de riesgos de interacción hombre-máquina en frentes de extracción subterránea  
**Manuscrito Destino:** *Acta Montanistica Slovaca*  
**Fecha:** Octubre 2026  
**Alcance:** Correcciones de código, pipelines experimentales, pruebas estadísticas e instrumentación ciberfísica  

---

## 1. RESUMEN GENERAL DE INTERVENCIONES

En estricto cumplimiento de las reglas del proyecto (sin alterar artificialmente resultados para favorecer al manuscrito y sin modificar el documento Word hasta completar la validación técnica), se implementó un conjunto de correcciones de nivel de producción sobre el software y los pipelines analíticos.

```
+---------------------------------------------------------------------------------------------------+
| MODIFICACIONES Y MEJORAS IMPLEMENTADAS EN EL SOFTWARE M-11                                        |
+------------------------------------+--------------------------------+-----------------------------+
| Módulo / Archivo Modificado        | Función / Componente           | Propósito Metodológico      |
+------------------------------------+--------------------------------+-----------------------------+
| backend/scripts/fair_eval.py       | make_pipeline()                | SMOTENC anidado por pliegue |
| backend/scripts/fair_eval.py       | find_f2_threshold()            | Calibración simétrica OOF   |
| backend/scripts/fair_eval.py       | paired_bootstrap_test()        | Bootstrap pareado (1000 it) |
| backend/scripts/fair_eval.py       | mcnemar_exact() + Holm         | Control de error Tipo I     |
| backend/scripts/fair_eval.py       | wilson_score_interval()        | Intervalos confianza al 95% |
| backend/scripts/fair_eval.py       | cliffs_delta()                 | Tamaño del efecto no param. |
| backend/scripts/train_cv.py        | run_cv_evaluation()            | Pipeline sin data leakage   |
| backend/scripts/run_ablation_study | Configuración B2               | Desacople de colinealidad   |
| backend/scripts/audit_label_circ.  | decompose_score_variance()     | Auditoría circularidad 82.1%|
| backend/scripts/audit_label_circ.  | evaluate_decoupled_scenarios() | Escenarios gas/fatiga/falla |
| backend/scripts/audit_genai_prot.  | DeterministicRuleEngine        | Barreras duras de seguridad |
| backend/scripts/benchmark_hardw.   | profile_latency_stages()       | Desglose E2E (inf/ser/ws)   |
| backend/scripts/run_shap_and_col.  | TreeSHAP + ubjson patch        | Atribución e interpretabil. |
| backend/scripts/generate_all_deliv | Master Export Pipeline         | Generación de CSVs y PNGs   |
+------------------------------------+--------------------------------+-----------------------------+
```

---

## 2. DETALLE DE CORRECCIONES METODOLÓGICAS Y DE SOFTWARE

### 2.1. Eliminación de Fuga de Información (*Data Leakage*) y SMOTENC Anidado
- **Archivo:** `backend/scripts/fair_eval.py` (Líneas 129–147)
- **Problema previo (FON-02 / FON-01 Rev 2):** En las versiones preliminares del repositorio, el sobremuestreo SMOTENC y la normalización se ejecutaban antes de dividir los pliegues de validación cruzada o sobre el conjunto de datos completo, contaminando la estimación con información sintética de validación.
- **Corrección técnica:** Se encapsuló el preprocesamiento (`StandardScaler` para 12 variables numéricas y `OneHotEncoder` para 4 variables categóricas) y el rebalanceo `SMOTENC` dentro de `imblearn.pipeline.Pipeline`. Cada pliegue de `StratifiedKFold(n_splits=5, shuffle=True, random_state=42)` ajusta el remuestreo **exclusivamente con los datos de entrenamiento del pliegue**, garantizando independencia absoluta del pliegue de validación y del 20 % de holdout de prueba.

### 2.2. Protocolo de Calibración Simétrica del Umbral $F_2$
- **Archivo:** `backend/scripts/fair_eval.py` (Líneas 157–185) y `backend/scripts/train_cv.py`
- **Problema previo (FON-01 / FON-04 Rev 2):** XGBoost se beneficiaba de una optimización post-hoc del umbral de decisión para la clase ALTO ($\tau \approx 0,14$), mientras que Random Forest, SVM y MLP eran evaluados con `predict()` estándar (`argmax` equivalente a $\tau = 0,50$). Esto inflaba la sensibilidad de XGBoost haciéndolo parecer superior sin mérito intrínseco.
- **Corrección técnica:** Se definió la función `find_f2_threshold()` que itera de forma determinista ($\tau \in [0,05, 0,95]$ a paso $0,01$) sobre las probabilidades *out-of-fold* (OOF) del conjunto de desarrollo (80 %) para TODOS los clasificadores probabilísticos. El umbral calibrado se congela y se aplica **una sola vez** sobre el 20 % de prueba. Se reporta el desempeño dual: con umbral calibrado y con argmax estándar.

### 2.3. Auditoría de Circularidad y Techo Bayesiano
- **Archivo:** `backend/scripts/audit_label_circularity.py`
- **Problema previo (FON-03 / FON-03 Rev 2):** La etiqueta `risk_level` procedía de una fórmula sintética que dependía casi exclusivamente de `distance_3d`, `ttc` y `in_restricted_zone`.
- **Corrección técnica:**
  1. Se implementó una descomposición cuantitativa de varianza en el score generador: el bloque espacial/cinemático explica el **82,1 % de la varianza**, el ruido aleatorio el **17,4 %**, y los sensores multimodales residuales solo el **0,5 %**.
  2. Se calculó el techo Bayesiano del clasificador ideal ($F_2 \approx 0,908$).
  3. Se crearon tres escenarios desacoplados donde el riesgo ALTO no depende de la proximidad física (intoxicación por CO > 50 ppm, fatiga extrema > 0,85, falla de vibración mecánica). En estos escenarios desacoplados, se demostró empíricamente la verdadera ventaja del gemelo digital multimodal sobre la regla cinemática TTC (ventaja de $+52$ a $+81$ pp en $F_2$).

### 2.4. Estudio de Ablación Robusto y Desacople de Colinealidad
- **Archivo:** `backend/scripts/run_ablation_study.py`
- **Problema previo (FON-04 / FON-08 Rev 2):** Al retirar `distance_3d` no había caída en $F_2$ ($+0,002$ pp) debido a que `ttc = distance_3d / relative_speed` mantenía la información de distancia. El artículo original interpretaba esto falsamente como "resiliencia algorítmica".
- **Corrección técnica:** Se introdujo la **Configuración B2** (*Sin el subsistema cinemático completo*: retiro simultáneo de `distance_3d`, `ttc` y `relative_speed`). Esta configuración reveló la verdadera dependencia física del modelo, con una caída drástica y estadísticamente significativa de $9,60$ pp ($0,907 \to 0,810$, $p = 0,002$). Todas las diferencias se estandarizaron separando puntos porcentuales ($\Delta\text{ pp}$) y variación relativa ($\Delta\%$).

### 2.5. Baselines Deterministas TTC Calibrados
- **Archivo:** `backend/scripts/fair_eval.py` (Líneas 80, 205–225)
- **Problema previo (FON-05 / FON-05 Rev 2):** Los baselines previos eran arbitrarios o no calibrados.
- **Corrección técnica:** Se implementaron dos reglas basadas en el estándar de la industria minera:
  1. `Baseline_TTC_fixed`: Umbral fijo a priori de $5,0\text{ s}$ ($F_2 = 0,907$).
  2. `Baseline_TTC_tuned`: Umbral empírico $\tau = 3,0\text{ s}$, optimizado estrictamente sobre las etiquetas de desarrollo del 80 % train ($F_2 = 0,910$). Se demostró con honestidad científica que, bajo la simulación original, el baseline TTC calibrado empíricamente empata con XGBoost ($F_2 = 0,906$ vs $0,910$, diferencia sin significancia estadística detectada), desmitificando la supuesta superioridad del ML en un entorno sintético circular.

### 2.6. Batería Estadística Inferencial No Paramétrica
- **Archivo:** `backend/scripts/fair_eval.py` (Líneas 240–340)
- **Problema previo (FON-06 / FON-06 Rev 2):** Pruebas de hipótesis inadecuadas y falta de corrección por multiplicidad.
- **Corrección técnica:**
  1. **Bootstrap Pareado:** 1000 muestras remuestreadas con reemplazo utilizando exactamente los mismos índices para todos los modelos, estimando intervalos de confianza al 95 % para $\Delta F_2$, $\Delta Recall$ y $\Delta Precision$.
  2. **Prueba de McNemar Exacta:** Evaluada sobre la matriz de contingencia de aciertos y desaciertos pareados en la detección de ALTO.
  3. **Corrección de Holm-Bonferroni:** Aplicada sobre el conjunto de 7 comparaciones múltiples contra XGBoost para controlar la tasa de error por familia (FWER).
  4. **Intervalos de Wilson al 95 %:** Calculados para proporciones binomiales ($Recall$ y $Precision$).
  5. **Delta de Cliff:** Calculado sobre las distribuciones bootstrap de $F_2$, documentando la magnitud del efecto.

### 2.7. Explicabilidad SHAP y Multicolinealidad
- **Archivo:** `backend/scripts/run_shap_and_collinearity.py`
- **Problema previo (FON-04 / FON-08 Rev 2):** Ausencia de TreeSHAP formal y falta de diagnóstico de colinealidad.
- **Corrección técnica:** Se calculó TreeSHAP sobre el pipeline de XGBoost (incorporando un parche de compatibilidad para la serialización UBJSON de `base_score` en XGBoost 2.x/3.x). Se confirmó que `distance_3d` (1,185), `ttc` (0,909) e `in_restricted_zone` (0,332) concentran la mayor atribución marginal, y se generó la matriz de correlación de Spearman (`figures/correlaciones.png`), probando la colinealidad intrínseca entre las variables de cinemática.

### 2.8. Banco de Pruebas Determinista y Barreras para Gemini GenAI
- **Archivo:** `backend/scripts/audit_genai_protocol.py` y `backend/app/services/gemini_service.py`
- **Problema previo (FON-12, FON-13 / FON-12, FON-13 Rev 2 / H12):** Ausencia de validación experimental del módulo de lenguaje natural y riesgo de alucinaciones en paradas de emergencia mineras.
- **Corrección técnica:**
  1. Se implementó en el backend el motor `DeterministicSafetyInterlock` (`backend/app/services/gemini_service.py`), obligando paradas de emergencia (D.S. 024-2016-EM Art. 272) y evacuaciones por gas CO (Art. 103/252) de forma independiente e inviolable por el LLM.
  2. Se construyó un banco de prueba determinista de **100 escenarios mineros** (`results/genai_audit_bank.json` y `results/gemini_audit.csv`).
  3. Se diseñó la plantilla de validación a doble ciego para supervisores humanos independientes (`results/genai_audit_review_sheet.csv`), estableciendo como limitación abierta que el índice Kappa de Cohen no debe simularse computacionalmente.

### 2.9. Benchmarking de Latencia y Desglose por Etapas
- **Archivo:** `backend/scripts/benchmark_hardware_profiler.py`
- **Problema previo (FON-10, FON-11 / FON-10, FON-11 Rev 2 / H01):** Reporte de latencia agregada sin desglose y afirmación indemostrable de 60 FPS en Three.js con 500 agentes.
- **Corrección técnica:**
  1. Se implementó el cronometraje de alta precisión (`time.perf_counter()`) separando: Preprocesamiento, Inferencia ML, Serialización JSON y Transporte WebSocket.
  2. Se auditó la máquina de ejecución: Intel Core i7-8550U @ 1.80GHz, 15.89 GB RAM, Windows 11.
  3. Se demostró que el backend cumple el 100 % de los ciclos dentro del presupuesto de tiempo real (< 200 ms a 5 Hz) hasta 500 agentes ($P_{95} = 27,9\text{ ms}$).
  4. Se documentó con rigor que los FPS corresponden a perfilado manual en cliente Chromium DevTools, y que la caída a 34,8 FPS con 500 agentes proviene del costo de llamadas de dibujo WebGL en Three.js con GPU integrada.

---

## 3. SUITE DE PRUEBAS AUTOMATIZADAS DE PRODUCCIÓN

Para garantizar que el software permanezca libre de regresiones técnicas y asegurar paridad matemática absoluta entre investigación y producción, se establecieron pruebas automatizadas con `pytest`:
1. `backend/tests/test_model_parity.py`:
   - Verifica la carga del modelo productivo `best_risk_model.joblib` entrenado con las 16 características.
   - Comprueba la aplicación estricta del umbral calibrado $\tau = 0,18$ documentado en `best_model_meta.json`.
   - Verifica la clasificación de casos de alto riesgo y casos seguros.
2. `backend/tests/test_safety_interlock.py`:
   - Verifica la parada de emergencia obligatoria por proximidad o colisión (D.S. 024-2016-EM Art. 272).
   - Verifica la evacuación inmediata hacia refugio minero ante concentraciones de CO superiores a 50 ppm (Art. 103/252).
   - Verifica la orden obligatoria de relevo ante fatiga crítica del operador (Art. 138).
3. `backend/tests/test_api.py`:
   - Verifica la conectividad, endpoints REST `/api/v1/predict/` y autenticación JWT.

---

## 4. SUBSANACIÓN INTEGRAL DE HALLAZGOS DE LA AUDITORÍA INDEPENDIENTE (H01 A H12)

| Hallazgo Auditado | Descripción del Hallazgo | Corrección Implementada en Código / Datos | Estatus |
|---|---|---|---|
| **H01** | Literales de FPS en generador contradicen profiler (`browser_render_fps_measured: null`). | En `benchmark_fps.csv` y figuras se declara explícitamente `measurement_type: Perfilado manual en cliente Chromium DevTools (no instrumentado headless)`. | **RESUELTO** |
| **H02** | Métricas de escenarios desacoplados hardcodeadas en CSV. | Se extraen dinámicamente de `circ_res["alternative_labels"]` en `generate_all_deliverables.py`. Cero literales fijos. | **RESUELTO** |
| **H03** | Gemini audit con 0 respuestas en CSV reportaba 100% cumplimiento. | Se etiquetó claramente como verificación del motor determinista de interbloqueo y se declaró la inferencia LLM como pendiente de `GEMINI_API_KEY`. | **RESUELTO** |
| **H04** | Discrepancia del umbral TTC tuned (5,84 s vs 3,0 s en JSON). | Se unificó extrayendo dinámicamente $\tau = 3,0\text{ s}$ desde `fair_comparison_results.json` en scripts y tablas. | **RESUELTO** |
| **H05** | Modelo de producción desfasado del pipeline de investigación (8 vs 16 variables). | Se creó `export_production_model.py`, exportando `best_risk_model.joblib` con 16 características y umbral calibrado $\tau=0,18$ integrado en `model_loader.py`. Suite `test_model_parity.py` pasa 100%. | **RESUELTO** |
| **H06** | Afirmación de equivalencia estadística sin prueba TOST. | Se sustituyó "Equivalente" por "Sin diferencia estadísticamente significativa detectada ($p_{\text{Holm}} > 0,05$)" (no rechazo de $H_0$). | **RESUELTO** |
| **H07** | Confusión entre discordancia de McNemar y diferencia de F2. | Se agregaron notas metodológicas aclarando que McNemar evalúa discordancia binaria de decisiones mientras bootstrap estima magnitud de $\Delta F_2$. | **RESUELTO** |
| **H08** | Hiperparámetros fijos presentados como optimizados. | Se etiquetaron como "Arquitectura fijada a priori según literatura de minería", aclarando que solo se calibró el umbral $\tau$. | **RESUELTO** |
| **H09** | Falta de ejecución de escenarios alternativos en script circular. | Se actualizaron los 6 escenarios en `audit_label_circularity.py` y se guardaron en `label_circularity_audit.json`. | **RESUELTO** |
| **H10** | CSV de circularidad no reflejaba varianza exacta de JSON (82,07%, $\sigma=3,8$). | Se vinculó dinámicamente a `variance_decomposition` y `noise_sensitivity` ($\sigma=3,8$, varianza espacial 82,07%). | **RESUELTO** |
| **H11** | Checksums SHA-256 sensibles a fin de línea (CRLF vs LF). | `generate_all_deliverables.py` genera en `reproducibility_manifest.json` tanto `sha256_raw` como `sha256_normalized_lf`. | **RESUELTO** |
| **H12** | Inexistencia de interbloqueo determinista en el backend. | Se implementó `DeterministicSafetyInterlock` en `backend/app/services/gemini_service.py` con pruebas unitarias en `test_safety_interlock.py`. | **RESUELTO** |
