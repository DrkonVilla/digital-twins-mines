# Auditoría diferencial independiente del repositorio M-11

**Versión auditada:** ZIP `digital-twins-mines-773554b7b6ac62937c3a19d0ae96635ccd136284.zip` (nombre del archivo; el hash de Git no se puede acreditar de modo independiente porque el ZIP no contiene `.git`).  
**Comparador:** `digital-twins-mines-feature-statistical-reports-validation.zip`.  
**Objeto:** comprobar los hallazgos H01–H12 frente a código fuente y artefactos almacenados.  
**Alcance:** lectura de código y artefactos; comparación de SHA-256; inferencia del modelo XGBoost persistido sobre el holdout suministrado; tres pruebas del módulo de paridad; prueba aislada de reglas deterministas. No se ejecutó todo `run_all_experiments.py`, no se evaluó el navegador Chromium y no se invocó Gemini en vivo. El resultado `9 passed` comunicado por el autor **no fue reproducido integralmente** en este entorno (faltan dependencias de API, autenticación y LangChain; se constató `ModuleNotFoundError: bcrypt`).

## Dictamen

**Revisión adicional necesaria antes de congelar las tablas para Acta Montanistica Slovaca.** La nueva versión corrige problemas de correspondencia y añade trazabilidad, pero persisten defectos verificables, algunos en componentes de seguridad y en inferencias científicas.

### Cambio respecto de la versión anterior

- **4 archivos incorporados**: `export_production_model.py`, `test_model_parity.py`, `test_safety_interlock.py` y una copia del informe de auditoría anterior.
- **23 archivos existentes modificados**, incluidos `model_loader.py`, `gemini_service.py`, `audit_label_circularity.py`, `generate_all_deliverables.py`, el modelo persistido, CSV y JSON de resultados.
- Los hashes `sha256_raw` y `sha256_normalized_lf` almacenados en `results/reproducibility_manifest.json` coinciden con los archivos del ZIP: **1 archivo de datos, 24 archivos de resultados, 7 figuras y 27 scripts** examinados. La verificación confirma integridad interna del ZIP; **no demuestra** que los resultados hayan sido medidos originalmente ni reproducidos de extremo a extremo.

## Estado H01–H12

| ID | Estado independiente | Evidencia y explicación |
|---|---|---|
| **H01 FPS** | **Parcial, no subsanado experimentalmente** | `backend/scripts/generate_all_deliverables.py`, aprox. líneas 509–571, conserva los valores numéricos literales 60.0, 59.5, 52.3, 34.8 y 59.0 FPS. La nueva columna `measurement_type` indica «manual en Chromium DevTools», pero no hay registros brutos, trazas, instrucciones o captura verificable que sustenten las mediciones. `automated_headless_fps` queda nulo. Se añade también 62.4 ms para una red sintética como literal. P3 no cumple 60 FPS a 200/500 agentes. |
| **H02/H09 métricas desacopladas** | **Corregida la exportación; validez científica pendiente** | `audit_label_circularity.py`, líneas 166–188, calcula siete juegos de etiquetas y sus métricas; `generate_all_deliverables.py`, líneas 459–479, los exporta del JSON, ya no de valores inventados en el exportador. Sin embargo, los escenarios son etiquetas sintéticas derivadas de los mismos predictores, con una sola partición, una semilla y CV interna de 3 pliegues; no constituyen validación externa. Los escenarios específicos de gas, fatiga y vibración **no muestran una ventaja relevante contra TTC calibrado**, contradiciendo la narrativa del informe previo. |
| **H03 auditoría Gemini** | **No resuelto como evaluación** | `generate_all_deliverables.py`, líneas 579–594, escribe `deterministic_rule_passed: True` incondicionalmente para los 100 casos. No verifica expectativas por escenario, no registra respuesta del LLM y deja los 100 estados `EVALUACION_HUMANA_PENDIENTE`. El CSV certifica solo que se generaron directivas, no que se superó una auditoría de seguridad. |
| **H04 umbral TTC** | **Corregido** | El exportador lee el umbral del JSON maestro (`fair_comparison_results.json`); los artefactos examinados consignan 3.0 s, no 5.84 s. |
| **H05 modelo productivo** | **Parcial** | El modelo persistido sí carga 16 variables, aplica umbral 0.18 y se pudo evaluar sobre el holdout. Sin embargo `export_production_model.py`, líneas 62–87, usa `StandardScaler/OneHotEncoder` + **SMOTE sobre datos transformados**; el protocolo científico de `fair_eval.py`, líneas 129–146, usa **SMOTENC antes del preprocesamiento**. No son el mismo entrenamiento ni producen exactamente las mismas predicciones. El exportador tampoco forma parte de la lista del script maestro `run_all_experiments.py`. El modelo de producción registra F2=0.905718, frente a 0.906522 de la evaluación científica. |
| **H06 equivalencia** | **Principalmente corregido** | El CSV de pruebas pareadas utiliza «Sin diferencia estadísticamente significativa detectada» en vez de equivalencia formal. Quedan frases ambiguas en `reports/RESULTADOS_EXPERIMENTALES.md` que aún hablan de resultados «equivalentes o marginalmente superiores» sin una prueba de equivalencia. |
| **H07 McNemar frente a F2** | **Parcial** | Las notas aclaran que McNemar compara decisiones binarias, pero `statistically_significant_p05` y `scientific_conclusion` se deciden usando **p de McNemar ajustado**, lo cual puede contradecir el IC bootstrap de ΔF2. Ejemplo XGBoost vs Voting: ΔF2=+0.004222, IC 95 % [−0.004065, +0.012394], contiene cero; sin embargo CSV registra `SI` porque p(McNemar, Holm)=0.019666. No debe presentarse como diferencia significativa de F2. |
| **H08 hiperparámetros** | **Corregido en la documentación** | `model_hyperparameters.csv` ahora declara arquitecturas fijadas a priori y distingue esa elección de calibración de umbrales por probabilidades OOF. Esta es una corrección de transparencia, no una nueva búsqueda de hiperparámetros. |
| **H10 circularidad y límite Bayes** | **Parcial** | La descomposición se lee del JSON: espacial 82.0693 %, multimodal 0.4818 %, covarianza 0.0155 %, ruido 17.4334 %. `audit_label_circularity.py`, líneas 52–74, obtiene F2=0.90049 bajo **supuestos de distribución normal y percentiles estimados**. Es una estimación de F2 óptimo esperado condicionada al generador, no una cota matemática demostrada sobre las muestras; el informe insiste en denominarlo «techo teórico» pese a resultados mayores. |
| **H11 integridad SHA-256** | **Corregido para archivos incluidos** | Coinciden hashes de archivo bruto o normalizado LF para los 59 recursos examinados. Aún conviene incorporar hash del `.joblib` de producción y su JSON de metadatos, que no figuran entre las categorías enumeradas por el manifiesto. |
| **H12 interbloqueo determinista** | **No demostrado como barrera operacional; presenta falsos positivos** | `gemini_service.py`, líneas 117–200, agrega un bloque de recomendaciones en lenguaje natural, pero no se observa una llamada a un controlador/actuador que inmovilice físicamente maquinaria. Además, la regla `"co" in msg` (línea 140) identifica el texto «colisión» como gas CO y obliga a evacuación gaseosa aunque no exista alarma de gas. Un mensaje BAJO que contenga «equipo correcto» también puede activar esa regla. `deterministic_rule_passed=True` es incondicional. Las 3 pruebas unitarias declaradas no abarcan estos casos. |

## Resultados nuevos de escenarios desacoplados

Se verificó que `results/decoupled_labels_results.csv` corresponde a las cifras de `results/label_circularity_audit.json` (siete escenarios). A continuación se compara con **TTC calibrado**, el comparador justo:

| Escenario | XGBoost F2 | TTC calibrado F2 | Diferencia aproximada, pp |
|---|---:|---:|---:|
| Original | 0.9058 | 0.9103 | −0.45 |
| Sólo multimodal | 0.6408 | 0.5851 | +5.57 |
| Sólo espacial | 0.6050 | 0.6316 | −2.66 |
| Balanceado 50/50 | 0.6330 | 0.5847 | +4.83 |
| Gas CO | 0.5834 | 0.5841 | −0.07 |
| Fatiga | 0.5823 | 0.5851 | −0.28 |
| Vibración | 0.5873 | 0.5864 | +0.09 |

**No usar** las cifras anteriores de F2=0.942/0.887/0.875 como resultados vigentes: no corresponden a las salidas del commit examinado. Los nombres «CO > 50 ppm» y «fatiga crítica» en la tabla son descripciones narrativas del exportador: las etiquetas alternativas se crean mediante scores continuos con ruido y percentiles globales, no con esos umbrales de evento explícitos. Las etiquetas de gas, fatiga y vibración incluso incluyen un término `0.5 * z(spatial)`, por lo que tampoco están totalmente desacopladas del componente espacial.

## Comprobaciones realizadas

1. **Diferencial del ZIP:** 4 entradas nuevas y 23 modificadas, sin archivos eliminados entre ambos ZIP.
2. **Verificación sintáctica:** 58 scripts Python de `backend/scripts` y `backend/app` analizados sin errores sintácticos.
3. **Inferencia reproducida sobre holdout del ZIP:** modelo persistido de 16 variables/umbral 0.18: F2 = **0.905718**, precisión = **0.781544**, recall = **0.943182**. Registro científico: F2 = **0.906522**, precisión = **0.772222**, recall = **0.947727**. Aviso de versiones de pickle porque el entorno local tiene `scikit-learn 1.8.0` y el modelo fue serializado con 1.7.2.
4. **Pruebas unitarias del modelo:** `PYTHONPATH=backend pytest -q backend/tests/test_model_parity.py` → **3 passed**.
5. **Suite total:** la recolección de `backend/tests/test_api.py` se interrumpió por `ModuleNotFoundError: bcrypt`; por ello **no se afirma** haber reproducido los `9 passed` informados por otro entorno.
6. **Prueba aislada de interlock:** el mensaje MEDIO «Se detectó colisión entre vehículos» desencadena también el protocolo de gas CO; es un falso positivo comprobado por ejecución de la clase con AST aislado.
7. **Auditoría del CSV Gemini:** 100 filas, las 100 con `deterministic_rule_passed=True` y las 100 marcadas con `EVALUACION_HUMANA_PENDIENTE`; 97 marcadas con `safety_lockout_active=True`. Esas tasas no constituyen una prueba de eficacia ni de cumplimiento regulatorio.
8. **Manifiesto:** hashes correctos de 1 dataset, 24 resultados, 7 imágenes y 27 scripts. Los valores de FPS y aprobaciones de reglas siguen sin procedencia de medición independiente aunque sus hashes coincidan.

## Prioridades para cerrar la auditoría

**P0 — Antes de usar resultados como evidencia experimental**

- **FPS:** sustituir literales por registros manuales trazables (exportación DevTools, captura de sesión, equipo/GPU, duración, semilla/carga), o retirar cifras no verificables. No cambiar el estado de P3 para aparentar cumplimiento de 60 FPS.
- **Gemini y seguridad:** no establecer `deterministic_rule_passed=True` por defecto; introducir expectativas individuales verificables y pruebas positivas/negativas; reemplazar detección de gases por campos estructurados y umbrales numéricos, no por coincidencia de subcadenas; denominar «motor de recomendaciones» salvo conexión efectiva a actuadores.
- **Paridad ML:** exportar exactamente el pipeline `fair_eval.make_pipeline` ya entrenado en desarrollo, con calibración guardada; dejar evidencia de paridad de probabilidades/predicciones sobre el mismo holdout; incorporar exportación y hash del modelo al runner de reproducción.
- **Estadística:** separar explícitamente la columna de significación de McNemar de la evidencia bootstrap de ΔF2, usando el criterio del análisis correspondiente; corregir la fila Voting.
- **Escenarios desacoplados:** retirar interpretación de superioridad general del ML. Documentar scores, ruido, distribución, umbrales, replicaciones/IC, comparador TTC calibrado y la persistencia de un término espacial de 0.5; reportar los nuevos resultados, aunque sean negativos.

**P1 — Antes del manuscrito definitivo**

- Renombrar F2 = 0.9005 como estimación dependiente de supuestos o justificar formalmente el cálculo como cota; suprimir «saturación del techo teórico» no demostrada.
- Repetir experimentos con diferentes semillas y documentar ausencia de grupos/episodios.
- Revisar correspondencia de afirmaciones técnicas y normativas; no prometer control físico real ni seguridad operacional demostrada.
- Confirmar en entorno con dependencias y versiones declaradas todas las pruebas unitarias, integración y reproducción de scripts.

## Decisión de auditoría

**Estado: correcciones parciales; todavía no congelar tablas ni enviar versión definitiva.** Es viable actualizar la sección metodológica como borrador con resultados identificados como provisionales y sin inventar evidencias; no es defendible presentar el software como «completamente estabilizado», «validación inatacable» o «seguridad garantizada». La próxima iteración debe ser focalizada y basada en los archivos/funciones indicados, sin rediseñar toda la plataforma.
