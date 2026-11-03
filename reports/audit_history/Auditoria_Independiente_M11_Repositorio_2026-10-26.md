# Auditoría independiente del repositorio M-11 — 26 de octubre de 2026

**Archivo examinado:** `digital-twins-mines-feature-statistical-reports-validation.zip`.
**Alcance:** revisión estática del código, cotejo de artefactos existentes, verificaciones aritméticas y pruebas rápidas controladas. No se ejecutó íntegramente `run_all_experiments.py`, no se instrumentó un navegador ni se consultó Gemini. Las métricas contenidas en artefactos preexistentes se identifican como *reportadas*, no como reproducidas independientemente.

## Dictamen ejecutivo

**Estado: aprobación condicionada / NO apto aún para consolidación definitiva del manuscrito.** El repositorio incluye un pipeline válido de evaluación sin SMOTENC global, un dataset de 10 000 × 37 y artefactos de comparación útiles. Sin embargo, contiene cifras fijas etiquetadas como experimentales, metadatos incongruentes con los resultados y una desconexión entre el clasificador de investigación y el que emplea el backend en inferencia. Son fallas sustantivas de trazabilidad experimental que deben resolverse antes de la redacción científica definitiva.

## Evidencia comprobada

| ID | Prioridad | Hallazgo verificado | Prueba/evidencia | Acción |
|---|---|---|---|---|
| H01 | Crítica | FPS exportados desde literales, no desde instrumentación del navegador | `backend/scripts/generate_all_deliverables.py` líneas 455–507 coloca 60.0, 59.5, 52.3, 34.8 y 59.0 en `benchmark_fps.csv`; `backend/scripts/benchmark_hardware_profiler.py` declara `frontend_fps=None` | Implementar captura de `requestAnimationFrame` o telemetría del renderizador y persistir sesiones, hardware, muestras y método |
| H02 | Crítica | Resultados separados de gas/fatiga/falla mecánica codificados manualmente | `generate_all_deliverables.py` líneas 382–425 fija F2=0.942, 0.887, 0.875 sin importar registros de esos tres experimentos | Ejecutar experimentos específicos reproducibles o retirar esas cifras de los resultados |
| H03 | Crítica | La auditoría Gemini no fue ejecutada sobre 100 respuestas | `results/gemini_audit.csv`: 100 escenarios, 0 respuestas no vacías, `auto_fully_compliant=0` para los 100; faltan `genai_audit_raw.jsonl` y `genai_audit_results.json` | No afirmar 100 % de cumplimiento; ejecutar el modo real si está habilitado y obtener revisión humana auténtica |
| H04 | Alta | Umbrales reportados incompatibles con la evaluación | XGBoost 0.18 en `metrics_comparison.csv` vs 0.14 en `model_hyperparameters.csv`; RF 0.18 vs 0.15; en `fair_comparison_results.json` TTC calibrado = **3.0 s**, mientras el CSV exporta 5.84 s | Generar hiperparámetros y umbrales directamente de `fair_comparison_results.json`, sin constantes manuales |
| H05 | Crítica | Sistema productivo no usa demostrablemente el clasificador calibrado de los experimentos | `backend/app/ml/model_loader.py` carga `best_risk_model.joblib`, ejecuta `self.model.predict()` en lugar de `apply_threshold(proba, threshold_F2)`. `train_cv.py` exporta métricas y particiones pero no reexporta un artefacto de inferencia junto con umbral; `best_model_meta.json` conserva métricas 0.9985 de fecha 2026-09-05 | Versionar el modelo científico seleccionado, el preprocesador, la lista de características y el umbral; añadir prueba de paridad entre evaluación offline y endpoint |
| H06 | Alta | Inferencia estadística rotulada incorrectamente como equivalencia | `paired_statistical_tests.csv` contiene «Equivalente (sin diferencia significativa)»; no se implementa una prueba de equivalencia con margen predefinido | Cambiar a «no se detectó diferencia» o justificar y ejecutar prueba de equivalencia |
| H07 | Alta | «Significativo en F2» puede reflejar una prueba sobre aciertos, no sobre F2 | XGBoost-vs-Voting tiene ΔF2 IC95% [-0.004065, +0.012394] que incluye 0, mientras p Holm McNemar ≈ 0.0197 y fila indica significación | Separar pruebas de decisiones y contrastes de ΔF2; no inferir una diferencia significativa de F2 desde McNemar |
| H08 | Alta | Parámetros de selección anunciados pero sin búsqueda real visible en pipeline oficial | `fair_eval.py` fija estimadores; no utiliza `GridSearchCV`/`RandomizedSearchCV`/equivalente. El exportador escribe espacios de búsqueda en literales | Documentar los hiperparámetros como prefijados o implementar búsqueda y guardar resultados reales |
| H09 | Alta | El análisis de etiquetas alternas real no coincide con los tres escenarios anunciados | `label_circularity_audit.json` incluye `label_multimodal_only`: F2 XGB≈0.640845, TTC fijo≈0.271098, TTC calibrado≈0.585106. Los tres escenarios anunciados por gas/fatiga/falla son valores literales independientes | Identificar explícitamente el comparador (fijo o calibrado) y reproducir los tres experimentos antes de alegar superioridad |
| H10 | Media | CSV de circularidad contiene cifras y unidades codificadas manualmente | `generate_all_deliverables.py` líneas 347–375 codifica 82.1/17.4/0.5%, «sigma_ruido=0.15» y F2=0.908. El análisis `audit_label_circularity.py` usa sigma=3.8 y guarda descomposición con más precisión | Construir el CSV desde `label_circularity_audit.json` y corregir la inconsistencia de sigma |
| H11 | Media | Manifiesto SHA256 no verifica el ZIP byte a byte sin normalización de fin de línea | Se observaron 22 discrepancias de hash en 24 archivos de `results/` y una en datos raw; todas se resuelven al convertir LF→CRLF. Las 7 figuras coinciden sin transformación | Regenerar hashes sobre los archivos distribuidos o documentar la normalización y suministrar un verificador multiplataforma. No atribuirlo a adulteración sin más pruebas |
| H12 | Alta | Barreras duras para Gemini no verificadas en el servicio operativo | `audit_genai_protocol.py` contiene un comprobador textual para pruebas, pero no la clase `DeterministicRuleEngine` declarada; `app/services/gemini_service.py` devuelve texto del LLM, sin evidencia de interlock operacional | Implementar reglas independientes del LLM en el backend real y probar su no-anulación; no equiparar el banco vacío con control de seguridad |

## Fortalezas verificadas

- Dataset: `data/raw/public_mining_equipment_dataset.csv` contiene **10 000 registros, 37 columnas** y reparto de clases 4500/3300/2200.
- Los **16 predictores** definidos por `fair_eval.FEATURES` existen en el dataset, sin nulos en esos predictores.
- El diccionario `results/feature_dictionary.csv` efectivamente contiene 37 registros.
- `fair_eval.make_pipeline()` ubica `SMOTENC`, `ColumnTransformer` y clasificador en `imblearn.pipeline.Pipeline`, con entrenamiento dentro del pliegue en `oof_evaluate`.
- Prueba controlada independiente: entrenamiento de `XGBoost` sobre 960 de los primeros 1 200 registros y predicción de 240 registros, finalizada correctamente (`proba` 240×3, F2 argmax ≈ 0.8922); **no es una réplica del benchmark oficial**.
- `audit_genai_protocol.py --selftest` finaliza con `SELFTEST OK`. Esto valida los casos internos del verificador, no a Gemini.
- Los 26 scripts Python en `backend/scripts/` superaron validación sintáctica con `ast.parse`.
- El archivo `fair_comparison_results.json` y `metrics_comparison.csv` son internamente consistentes en F2 de XGBoost ≈0.9065, RF ≈0.9103, TTC calibrado ≈0.9103. No se repitió todavía el entrenamiento completo para certificar esos números.

## Limitaciones importantes de la evaluación

- No se ejecutó el pipeline completo, dado que involucra múltiples entrenamientos, renderizado y servicios opcionales. Ningún resultado de `results/` fue certificado de nuevo mediante réplica de la corrida completa.
- No hay identificadores de episodios/trayectorias para comprobar independencia temporal mediante validación agrupada del dataset principal.
- Sin captura del navegador no hay evidencia independiente de FPS reales.
- Sin respuestas de Gemini ni revisión humana no hay tasa de cumplimiento, alucinaciones ni kappa verificadas.
- Los hashes discrepantes parecen deberse a normalización de finales de línea en el empaquetado, no a evidencia de alteración deliberada.

## Correcciones prioritarias antes del manuscrito

1. Eliminar números literales de FPS, escenarios desacoplados, circularidad y calibración. Sustituirlos por exportaciones trazables desde ejecuciones verificadas; si faltan mediciones, exportar `not_measured`/`null` con justificación.
2. Ejecutar o descartar los tres escenarios específicos de gas, fatiga y falla; documentar generador de etiquetas, splits, configuraciones y tamaño de muestra, con comparación frente a TTC fijo **y calibrado**.
3. Corregir toda la tabla `model_hyperparameters.csv`; añadir prueba automática de consistencia frente a `fair_comparison_results.json`.
4. Asegurar que el modelo, 16 características, transformador y umbral usados por el endpoint coincidan con el pipeline científico final o diferenciar explícitamente dos modelos y sus alcances.
5. Rectificar los rótulos de equivalencia estadística y separar los p-valores de McNemar de las diferencias de F2.
6. No afirmar que Gemini ha superado 100/100 mientras el CSV no contiene respuestas; completar ejecución real o declararlo pendiente.
7. Establecer medición real y automatizada de FPS, con FPS por percentil, 5 Hz, carga de agentes y latencia sincronizadas; contrastar objetivo de 60 FPS.
8. Mantener registro de datos sintéticos, bloqueo de corpus, manifest multiplataforma, limitaciones de independencia de observaciones y evidencia verificable por revisores.

## Decisión para el artículo AMS 2026

**No consolidar todavía las Tablas 2, 4, 5, 6 ni las afirmaciones cuantitativas de escenarios desacoplados, FPS y GenAI con los números de este informe.** Las bases del pipeline son aprovechables. Una vez corregidas las discrepancias, elaborar el manuscrito en español, preservando la redacción original y las 42 referencias si esa es la decisión editorial del autor, con todo resultado debidamente reproducido. El dictamen aquí es técnico, no una predicción de aceptación editorial.
