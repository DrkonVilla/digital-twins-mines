# DECLARACIÓN TRANSPARENTE DE LIMITACIONES PENDIENTES DEL SISTEMA M-11

**Proyecto:** Implementación de un gemelo digital para la alerta temprana de riesgos de interacción hombre-máquina en frentes de extracción subterránea  
**Manuscrito Destino:** *Acta Montanistica Slovaca*  
**Edición Normativa de Referencia:** D.S. 024-2016-EM (Edición Oficial MINEM)  
**Principio Rector:** Rigor metodológico, honestidad científica y reproducibilidad conforme al estándar COPE y políticas editoriales de Scopus Q1/Q2.  

---

## 1. INTRODUCCIÓN Y MARCO DE ACREDITACIÓN CIENTÍFICA

Cualquier aspecto que requiera experimentación de campo en túnel físico, telemetría de red subterránea real o validación subjetiva humana ha sido clasificado formalmente en este documento como **PENDIENTE POR EVIDENCIA**, **EVALUACIÓN HISTÓRICA DE PROTOTIPO** o **LIMITACIÓN METODOLÓGICA DEL ESTUDIO**.

Esta categorización explícita distingue de manera inequívoca:
1. **Resultados reproducidos y verificados con código ejecutable:** Circularidad del target sintético (82,1 % varianza espacial), calibración simétrica de XGBoost vs. TTC, evaluación en 7 escenarios desacoplados y verificación de invariantes del interbloqueo determinista (17/17 tests unitarios y 100/100 escenarios conformes).
2. **Implementaciones y resultados disponibles con reejecución automatizada:** Comparación de 6 clasificadores en 5-fold CV anidada (`train_cv.py`), bootstrap pareado e inferencia McNemar-Holm, estudio de ablación multimodal A–G (`run_ablation_study.py`) y explicabilidad TreeSHAP (`run_shap_and_collinearity.py`).
3. **Resultados históricos de prototipo y pruebas de concepto (PoC):** Benchmarks de renderizado cliente Three.js (34,8 FPS a 500 agentes con GPU integrada Intel UHD 620) y evaluación experimental en lenguaje natural de Google Gemini.

---

## 2. INVENTARIO DE LIMITACIONES TÉCNICAS, METODOLÓGICAS Y NORMATIVAS

### 2.1. Criterios de Diseño Preventivo vs. Límites Ocupacionales Ponderados (TWA)
- **Estado:** Delimitación conceptual y normativa resuelta.
- **Fundamento Legal:** En la edición oficial del Reglamento de Seguridad y Salud Ocupacional en Minería (D.S. 024-2016-EM):
  - El **Anexo 15** establece los Límites de Exposición Ocupacional a Agentes Químicos, fijando para el monóxido de carbono (CO) un valor límite de $25\text{ ppm}$ como concentración media ponderada en el tiempo para una jornada laboral de 8 horas (**TWA**).
  - El **Art. 111** contempla la paralización inmediata de actividades y retiro de personal cuando se superen los Límites Permisibles de material particulado y agentes químicos en subterráneo (estableciendo $3\text{ mg/m}^3$ para polvo respirable en 8 horas).
- **Implicancia en el Software M-11:** Las alarmas instantáneas emitidas por el gemelo digital ante detecciones puntuales (e.g. $\text{CO} \ge 25\text{ ppm}$, polvo $\ge 3\text{ mg/m}^3$) constituyen **criterios de diseño preventivo propios del prototipo para alerta temprana**, inspirados en dichos umbrales de referencia, y **no una reproducción ni sustitución literal de mediciones dosimétricas TWA ponderadas en la jornada**.

### 2.2. Seguridad Lógica Verificada vs. Seguridad Funcional Certificada (SIL / IEC 61508)
- **Estado:** Delimitación de alcance industrial.
- **Descripción:** El componente `DeterministicSafetyInterlock` superó 17 pruebas unitarias de software automatizadas en `pytest` y validó la totalidad de las directivas operacionales sobre un banco de 100 escenarios sintéticos.
- **Implicancia Científica:** Esta verificación acredita **consistencia lógica interna y ausencia de falsos positivos cruzados en el software**. Sin embargo, **no constituye una certificación funcional de seguridad (SIL-2/SIL-3 bajo IEC 61508 o ISO 13849)** ni sustituye el enclavamiento físico de relés cableados o sistemas PLC/SCADA de maquinaria pesada. El gemelo digital actúa como un *motor asesor de directivas de seguridad operacional*.

### 2.3. Módulo Gemini GenAI: Asistencia en Lenguaje Natural sin Confiabilidad Humana Simulada
- **Estado:** PENDIENTE POR EVALUACIÓN HUMANA INDEPENDIENTE.
- **Descripción:** El módulo LLM genera directivas complementarias y explicaciones para el operador de mina. En el repositorio se dispone del banco formal de 100 escenarios (`results/genai_audit_bank.json`) y la plantilla de revisión ciega (`results/genai_audit_review_sheet.csv`).
- **Postura Ética y Rigor:** Se retiraron del manuscrito definitivo métricas no trazables (cumplimiento 69 %, concordancia 93,3 %, $\kappa = 0,85$, alucinación 13,3 %). Se declara formalmente que **el cálculo del coeficiente Kappa de Cohen entre supervisores humanos independientes queda abierto para fases de validación con personal de mina en operación**. La arquitectura garantiza que ninguna salida del LLM puede relajar o anular las directivas deterministas (`override_allowed_by_llm = False`).

### 2.4. Precisión Conceptual de la Estimación del Generador vs. «Techo de Bayes»
- **Estado:** Corregido y fundamentado.
- **Descripción:** Mediante `bayes_ceiling_f2()` se simuló un valor de $F_2 \approx 0,9005$ bajo el supuesto de un score continuo con ruido Gaussiano ($\sigma = 3,8$).
- **Implicancia Metodológica:** En la evaluación empírica con holdout del 20 %, XGBoost alcanza $F_2 = 0,9058$ y el Baseline TTC calibrado alcanza $F_2 = 0,9103$. Dado que ambos clasificadores superan levemente dicha cifra, **resulta matemáticamente impropio clasificar $0,9005$ como un "techo de Bayes formal" o límite superior insuperable**. Debe presentarse como una *estimación analítica aproximada del desempeño esperado bajo la función generadora sintética*.

### 2.5. Delimitación Estricta de Configuraciones en el Estudio de Ablación
- **Estado:** Corregido e individualizado.
- **Descripción:** Se clarifica formalmente la distinción entre dos experimentos que en redacciones preliminares se aludían bajo la etiqueta ambigua de "cinemática":
  1. **Configuración B2 (Retiro del bloque cinemático específico: 3 variables: `distance_3d`, `relative_speed`, `ttc`):** Genera una caída controlada de **$-9,60\text{ pp}$** (de $0,9065$ a $0,8105$).
  2. **Configuración G (Retiro del bloque espacial completo: 8 variables espaciales y cinemáticas):** Provoca un colapso de **$-32,52\text{ pp}$** (de $0,9065$ a $0,5813$), aproximándose al clasificador trivial Siempre-ALTO ($0,5851$).

### 2.6. Rigor en la Inferencia Estadística: No Rechazo de $H_0$ vs. Equivalencia
- **Estado:** Formalizado conforme a estadística inferencial.
- **Descripción:** La diferencia observada entre XGBoost ($F_2 = 0,9058$) y el Baseline determinista TTC calibrado ($F_2 = 0,9103$) es de $\Delta F_2 = -0,0045$.
- **Implicancia Metodológica:** El remuestreo bootstrap pareado (1 000 repeticiones) arroja un IC 95 % $[-0,0129, +0,0047]$ que contiene al cero, y la prueba pareada de McNemar con corrección Holm-Bonferroni entrega $p_{\text{Holm}} = 0,6015 > 0,05$. Este resultado se declara formalmente como **"sin diferencia estadísticamente significativa detectada" (no rechazo de la hipótesis nula $H_0$)**, evitando afirmar equivalencia absoluta sin haber formulado un test de equivalencia TOST (*Two One-Sided Tests*) con margen delta predefinido.

### 2.7. Naturaleza Sintética del Dataset Benchmark
- **Estado:** Identificada y declarada.
- **Descripción:** El estudio emplea un conjunto de datos híbrido de 10 000 registros estructurado a partir del repositorio UCI AI4I 2020 con adición de variables biomecánicas, ambientales y cinemáticas generadas por simulación estocástica.
- **Implicancia Científica:** Los registros no provienen de telemetría de campo directa (UWB en roca mineralizada ni buses CAN J1939 reales). Acredita viabilidad arquitectónica y algorítmica en nivel de madurez tecnológica TRL 4 (validación en laboratorio), requiriendo validación en faena para escalar a TRL 7.

### 2.8. Rendimiento de Renderizado Cliente Three.js en Flotas Densas
- **Estado:** Identificada y auditada.
- **Descripción:** El visor 3D web sostiene 60 FPS con flotas de hasta 100 agentes concurrentes, pero desciende a 52,3 FPS con 200 agentes y a 34,8 FPS con 500 agentes al procesar mallas independientes en GPU integrada Intel UHD 620.
- **Implicancia Científica:** El cuello de botella es estrictamente de llamadas de dibujo WebGL (*draw calls*) en el navegador del cliente. La generalización del visor para frentes masivos con cientos de operarios y equipos requerirá migrar a geometrías instanciadas (`THREE.InstancedMesh`).

---

## 3. ALINEAMIENTO NORMATIVO CON EL D.S. 024-2016-EM (MINEM)

Para preservar la rigurosidad jurídica del artículo y del software, las directivas de seguridad se vinculan estrictamente con la edición oficial del reglamento:

| Peligro Identificado | Fundamento Normativo Oficial MINEM | Criterio Operacional del Prototipo |
|---|---|---|
| **Colisión y Peligro Inminente** | **Arts. 38 y 40(d)**; PETS Operacional | Paralización preventiva de energía motriz e inmovilización por derecho de retiro y detención ante peligro inminente de colisión en galería. |
| **Monóxido de Carbono (CO)** | **Arts. 110, 252 y 254; Anexo 15**; Art. 40(d) | Evacuación hacia labor ventilada y verificación de aforos ante emisiones diésel anómalas (alerta preventiva instantánea $\ge 25\text{ ppm}$). |
| **Fatiga y Somnolencia** | **Art. 273** | Programa obligatorio de prevención y control de fatiga/somnolencia: relevo preventivo del operador de equipo móvil. |
| **Polvo Respirable y Visibilidad** | **Arts. 110 y 111**; PETS Tránsito | Monitoreo de agentes químicos y material particulado; paralización de actividades al superarse límites y activación de supresores/humectación. |
| **Falla Mecánica Grave** | Procedimiento Interno LOTO / PETS; **Art. 38** | Detención de maquinaria e inspección técnica obligatoria previa a la reanudación de marcha. |

> **Nota Exclusoria:** Quedan expresamente descartadas las citas erróneas detectadas en borradores preliminares (Art. 105 que regula congelamiento, Art. 138 que regula listas de telecomunicaciones, Art. 253 que prohíbe motores gasolineros, Art. 274 relativo a minería de carbón y Art. 367 sobre espaciamiento de tuberías/cables).
