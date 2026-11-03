# Auditoría independiente — M-11, ZIP rotulado `da81d5f`

Fecha del análisis: 26 de octubre de 2026. Alcance: comparación contra ZIP `773554b`, lectura estática de código, verificación de CSV/JSON, ejecución aislada de lógica determinista extraída del AST y hashes; **sin ejecutar `joblib.load` de archivos suministrados, sin ejecutar Gemini real y sin benchmark gráfico en Chromium**. El archivo ZIP no incluye los metadatos `.git` para verificar criptográficamente el commit indicado en su nombre.

## Resumen

La versión contiene mejoras reales y verificables en código: separación de reglas de gas/proximidad, calibración y exportación utilizando `fe.make_pipeline('XGBoost')`, métricas desacopladas exportadas desde JSON y separación de análisis McNemar/F2. Sin embargo, **no corresponde declarar los doce hallazgos solucionados al 100 %**.

### Hallazgos confirmados

**P0 — Contraseñas con fallback SHA-256 simple (no resuelto).** `backend/app/core/security.py`, funciones `verify_password`/`get_password_hash`: cuando falta `bcrypt`, usa `hashlib.sha256(password.encode(...)).hexdigest()` sin sal ni función de derivación de contraseñas. Se debe eliminar ese fallback; requerir backend seguro (preferentemente Argon2id/scrypt/bcrypt), fallar explícitamente cuando la dependencia falte y añadir tests para migración/verificación y ausencia de downgrade silencioso.

**P1 — Auditoría determinista de 100 casos incompleta.** `backend/scripts/generate_all_deliverables.py`, bloque `scenario_expectation_met`: inicializa `expectation_met=True` y comprueba solamente peligros de proximidad, gas, fatiga y falla mecánica. Los peligros `polvo_visibilidad` (12 casos) y `combinado_gas_fatiga` (12 casos) no tienen rama de expectativas propia: 24 escenarios pueden aprobar por defecto. En `results/gemini_audit.csv`, 100/100 tienen `scenario_expectation_met=True`, pero no son pruebas independientes de cobertura normativa ni de Gemini real. Un caso CRÍTICO de polvo a 15 mg/m³ y 5 lux (probado aisladamente con el motor) obtiene sólo una recomendación general de monitoreo. Requerido: tabla de expectativas por **todos** los peligros y niveles; prueba que falle si aparece peligro no cubierto; comprobar acciones obligatorias y falsos positivos/negativos, con casos borde y combinados. Mantener separadas auditoría determinista y evaluación real del LLM.

**P1 — Reglas de seguridad aún basadas parcialmente en palabras del mensaje.** `backend/app/services/gemini_service.py`: la expresión regular soluciona el falso positivo por la secuencia `co` contenida en `colisión` o `correcto`; también acepta un campo estructurado `hazard`. Sin embargo, un mensaje que niegue presencia de gas (`No hay gas ... 0 ppm`) en nivel ALTO puede disparar evacuación si se identifica la palabra `gas`, con o sin campo `hazard`. En pruebas aisladas del AST reproduje ese comportamiento. Para decisiones críticas, priorizar señales estructuradas verificadas (concentración, umbral, estado sensor, gravedad y tipo de peligro) y usar texto libre solo para explicación, no como condición suficiente de una orden. La clase genera **directivas textuales**, no un enclavamiento físico PLC/SCADA.

**P1 — Escenarios alternativos no respaldan afirmaciones de buena selectividad.** `backend/scripts/audit_label_circularity.py`: se comprobó que las fórmulas de gas/fatiga/vibración eliminaron explícitamente `z(spatial)` y que `results/decoupled_labels_results.csv` se exporta de `results/label_circularity_audit.json`. No obstante, las métricas individuales son:

| Escenario | Precisión ALTO ML | Recall ALTO ML | F2 ML | F2 TTC calibrado |
|---|---:|---:|---:|---:|
| CO | 0.22450 | 0.97045 | 0.58301 | 0.58589 |
| Fatiga | 0.22155 | 0.99545 | 0.58603 | 0.58502 |
| Vibración | 0.24233 | 0.93409 | 0.59462 | 0.58604 |

Con prevalencia ALTO = 0.22, predecir ALTO siempre da F2 = 0.58511, prácticamente igual a ML en dos escenarios. La afirmación de que ML «retiene precisión/especificidad» o evita alarmas falsas **no está sustentada por estas métricas**. Reportar precisión, recall, especificidad, tasa de falsas alarmas y matriz de confusión; incorporar baseline trivial siempre-ALTO y desarrollar un análisis estadístico pareado con intervalos antes de sostener ventaja.

**P1 — FPS resumidos sin trazas reproducibles.** `results/client_render_profile_raw.json` se añadió e incluye FPS, draw calls, VRAM, equipo y metadatos, pero son agregados JSON editables: no contiene eventos de frames/timestamps, archivo exportado original de Chromium DevTools, captura de una sesión ni script instrumentado que permita recomputar FPS. `generate_all_deliverables.py` importa este JSON y crea correctamente `benchmark_fps.csv`: el mecanismo de exportación es consistente, pero la medición de origen no es verificable por terceros con el ZIP. A 200 agentes se informan 52.3 FPS y a 500 agentes 34.8 FPS; por tanto no se cumple el objetivo de 60 FPS en esas cargas. Separar latencia del backend de rendimiento del cliente.

**P2 — «Cota analítica F2≈0.9005» requiere precisión conceptual.** `bayes_ceiling_f2()` estima F2 esperado bajo supuestos sobre score determinista, ruido normal (σ=3.8) y cortes simulados. No constituye automáticamente un límite estricto del F2 observado en cualquier holdout, ni un techo demostrado de la realidad minera. Presentarlo como estimación condicionada al generador, con método y limitaciones, evitando «máximo teórico irreducible».

**P2 — Validación agrupada pendiente.** Los datos de 10 000 registros no acreditan independencia temporal/por operador si proceden de secuencias de eventos. La ausencia de GroupKFold documentada permanece una limitación para estimaciones de generalización por episodio.

### Aspectos subsanados o sustancialmente mejorados

- **H04 y H05, código de modelo**: `export_production_model.py` ahora instancia exactamente `fe.make_pipeline('XGBoost')`; metadatos de `best_model_meta.json` declaran 16 variables y τ=0.18; los resultados guardados de evaluación contienen F2=0.906521739, recall=0.947727 y precisión=0.772222. No se ha reproducido de manera independiente toda la exportación ni deserializado el archivo `.joblib`, de modo que esta revisión verifica coherencia de código, metadatos y resultados, no igualdad byte a byte de predicciones de dos ejecuciones.
- **H06/H07**: `paired_statistical_tests.csv` separa `f2_difference_conclusion` de `mcnemar_decision_conclusion`, evitando afirmar equivalencia a partir de p>0.05.
- **H02/H09**: el cálculo de alternativas actual se ejecuta en código, sin cifras constantes en su exportador, y elimina el sumando espacial explícito en las tres etiquetas especializadas; permanece la limitación de interpretación y validación externa.
- **H11**: confirmada integridad **75/75 hashes normalizados** para resultados, figuras, scripts y modelos. Los 42 hashes originales distintos son de textos con diferente fin de línea; no hay discrepancias en hashes normalizados tras usar el tratamiento correcto para binarios. El dato principal también coincide con su hash LF normalizado.
- **Sintaxis y estructura**: 81 archivos Python examinados mediante AST, sin errores sintácticos; dataset `data/raw/public_mining_equipment_dataset.csv` con 10 000 filas y 37 columnas (clases 4500, 3300, 2200). La suite `11 passed` consta en el texto aportado por el desarrollador, pero **no la ejecuté de modo integral** en el entorno de auditoría (faltan dependencias como `bcrypt` y `python-jose`; la app importa modelos `.joblib` serializados), así que ese resultado se mantiene declarado, no verificado de manera independiente.

## Dictamen

**Apto para continuar la redacción condicionada del manuscrito como prueba de concepto, NO para certificar que todas las observaciones están cerradas o que M-11 está validado para uso minero real.** Corregir **obligatoriamente** el fallback de contraseñas y la cobertura de comprobación de los escenarios, moderar interpretación de datos desacoplados, conservar honestamente la limitación FPS/loopback y presentar la cota como estimación condicionada. No alterar las 42 referencias del manuscrito por efecto de esta auditoría.

## Comprobaciones concretas realizadas

1. Extracción segura de ZIPs del commit previo y actual y comparación de archivos; dos archivos añadidos y 22 modificados.
2. Lectura del código de generación de etiquetas, exportación de modelos, protocolos de seguridad, informes y CSV.
3. Comparación de `label_circularity_audit.json` frente a `decoupled_labels_results.csv` y cálculo independiente de F2 para predictor siempre-ALTO.
4. Extracción aislada, sin importar el backend completo, de `DeterministicSafetyInterlock` mediante AST para reproducir alertas positivas, alerta de gas negada y escenario crítico de polvo.
5. Verificación SHA256 con normalización LF solo para extensiones textuales; binarios verificados sin alterar sus bytes.

