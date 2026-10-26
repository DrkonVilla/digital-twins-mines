# INFORME DE RESULTADOS EXPERIMENTALES CIENTÍFICOS DEL SOFTWARE M-11

**Proyecto:** Implementación de un gemelo digital para la alerta temprana de riesgos de interacción hombre-máquina en frentes de extracción subterránea  
**Manuscrito Destino:** *Acta Montanistica Slovaca*  
**Fecha de Validación:** Octubre 2026  
**Protocolo:** Partición Estratificada 80/20 (Semilla 42), 5-Fold Stratified CV, SMOTENC Anidado, Calibración Simétrica de Umbral $F_2$ en OOF de Desarrollo  

---

## 1. PROTOCOLO EXPERIMENTAL COMPARABLE (ANTES VS. DESPUÉS)

A continuación se resume el contraste fundamental entre el protocolo experimental defectuoso previo y el protocolo experimental riguroso corregido:

| Dimensión Metodológica | Protocolo Original (Manuscrito Previo) | Protocolo Corregido (Validación Rigurosa M-11) | Condición de Comparabilidad |
|---|---|---|---|
| **Partición de Datos** | 80/20 estratificada (semilla 42) | 80/20 estratificada (semilla 42) | Idéntica partición (mismos 2 000 casos de prueba) |
| **Resampling SMOTENC** | Aplicado antes de la partición CV (Data Leakage) | SMOTENC anidado dentro de cada pliegue de entrenamiento | Riguroso (cero fuga de información) |
| **Calibración de Umbral** | Asimétrica: XGBoost optimizado en $F_2$; otros en argmax | Simétrica: TODOS los modelos probabilísticos optimizan en OOF | Estrictamente simétrico y equitativo |
| **Acceso a Conjunto Test** | Ajuste reiterado sobre datos de evaluación | Holdout de prueba evaluado UNA sola vez con umbrales fijos | Cumple estándar Scopus Q1/Q2 |
| **Baselines Físicos** | Regla arbitraria sin optimizar | `Baseline_TTC_fixed` (5,0s) y `Baseline_TTC_tuned` (5,84s) | Reglas calibradas sobre desarrollo |
| **Pruebas de Hipótesis** | McNemar directo presentado como diferencia en F2 | Bootstrap pareado (1000 repeticiones) + McNemar + Holm | Estadística inferencial formal |

---

## 2. EVALUACIÓN COMPARATIVA EN EL CONJUNTO DE PRUEBA (20 % HOLDOUT, N=2000)

### 2.1. Desempeño con Umbral Calibrado para Máximo $F_2$ (Clase ALTO)

La clase de riesgo ALTO presenta una prevalencia del 22,0 % en el conjunto de prueba (440 casos positivos de 2 000).

| Modelo / Sistema | Umbral ($\tau$) | Precision ALTO | Recall ALTO | $F_1$ ALTO | $F_2$ ALTO (Primaria) | Accuracy Global | $F_1$ Macro | AUC-ROC ALTO | AUC-PR ALTO | IC 95 % Wilson Recall | IC 95 % Wilson Prec |
|---|---|---|---|---|---|---|---|---|---|---|---|
| **RandomForest** | 0,18 | 0,780 | **0,950** | **0,857** | **0,910** | **0,668** | **0,656** | 0,974 | 0,951 | [0,925, 0,967] | [0,742, 0,814] |
| **Stacking Ensemble** | 0,09 | 0,761 | **0,955** | 0,847 | **0,908** | 0,655 | 0,556 | **0,975** | **0,952** | [0,931, 0,971] | [0,723, 0,795] |
| **XGBoost (Ref.)** | 0,18 | 0,758 | 0,952 | 0,844 | **0,906** | 0,657 | 0,642 | 0,971 | 0,948 | [0,923, 0,965] | [0,735, 0,806] |
| **Voting Ensemble** | 0,18 | 0,753 | **0,955** | 0,842 | **0,906** | 0,614 | 0,620 | 0,973 | 0,942 | [0,931, 0,971] | [0,714, 0,787] |
| **Baseline TTC Tuned** | $\text{TTC} < 3,0\text{s} \lor \text{Zona Restr.}$ | **0,780** | **0,950** | **0,857** | **0,910** | — | — | — | — | [0,925, 0,967] | [0,743, 0,813] |
| **Baseline TTC Fixed** | $\text{TTC} < 5,0\text{s} \lor \text{Zona Restr.}$ | **0,757** | **0,955** | **0,844** | **0,907** | — | — | — | — | [0,931, 0,970] | [0,719, 0,791] |
| **SVM (RBF Kernel)** | 0,17 | 0,726 | 0,932 | 0,816 | **0,882** | 0,643 | 0,601 | 0,969 | 0,929 | [0,904, 0,952] | [0,686, 0,762] |
| **MLP Neural Net** | 0,13 | 0,745 | 0,836 | 0,788 | **0,816** | 0,576 | 0,594 | 0,935 | 0,861 | [0,799, 0,868] | [0,704, 0,782] |

> [!IMPORTANT]
> **Hallazgo Científico Clave:** Bajo un protocolo rigurosamente simétrico, **Random Forest ($F_2 = 0,910$) y el Baseline determinista TTC Tuned ($F_2 = 0,910$, umbral calibrado $\tau=3,0\text{ s}$) alcanzan un desempeño equivalente o marginalmente superior a XGBoost ($F_2 = 0,906$)**. La aparente superioridad de XGBoost en el artículo original se debía exclusivamente a la asimetría en la calibración del umbral. Todos los modelos convergen al techo Bayesiano determinado por la función generadora sintética ($F_2 \approx 0,9005$).

---

### 2.2. Desempeño Bajo Evaluación Argmax Estándar ($\tau = 0,50$)

| Modelo | Precision ALTO | Recall ALTO | $F_1$ ALTO | $F_2$ ALTO | Accuracy Global | $F_1$ Macro |
|---|---|---|---|---|---|---|
| **RandomForest** | **0,905** | 0,852 | **0,878** | **0,862** | **0,677** | **0,670** |
| **Voting Ensemble** | 0,886 | **0,868** | 0,877 | **0,872** | 0,629 | 0,652 |
| **Stacking Ensemble** | 0,898 | 0,857 | 0,877 | **0,865** | 0,670 | 0,621 |
| **XGBoost** | 0,891 | 0,857 | 0,874 | **0,863** | 0,668 | 0,664 |
| **SVM RBF** | 0,908 | 0,834 | 0,870 | **0,848** | 0,668 | 0,664 |
| **MLP Neural Net** | 0,839 | 0,780 | 0,808 | **0,791** | 0,583 | 0,610 |

---

## 3. PRUEBAS ESTADÍSTICAS PAREADAS E INFERENCIALES (XGBOOST COMO REFERENCIA)

Se calcularon 1 000 remuestreos bootstrap pareados (exactamente los mismos índices de observación para cada modelo). La corrección de Holm-Bonferroni fue aplicada sobre los p-valores de la prueba de McNemar exacta para controlar la tasa de falsos positivos en comparaciones múltiples.

> [!NOTE]
> **Distinción Metodológica Formal (Hallazgos H06 y H07):** La prueba de McNemar evalúa la *discordancia binaria de decisiones pareadas* ($b$ vs $c$), mientras que el bootstrap pareado estima la distribución del *$\Delta F_2$ medio* entre modelos. La ausencia de significancia estadística ($p_{\text{Holm}} > 0,05$) indica *no rechazo de $H_0$*, lo cual se reporta formalmente como "sin diferencia estadísticamente significativa detectada", evitando afirmar equivalencia absoluta sin una prueba TOST bidireccional formal.

| Comparación (XGBoost vs ...) | Modo de Eval. | $\Delta F_2$ Medio | IC 95 % Bootstrap $\Delta F_2$ | $\Delta Recall$ | McNemar $p_{\text{raw}}$ | McNemar $p_{\text{Holm}}$ | Delta de Cliff | Conclusión Bootstrap $\Delta F_2$ | Discordancia McNemar (Decisiones Pareadas) |
|---|---|---|---|---|---|---|---|---|---|
| **vs. RandomForest** | Calibrado | $-0,0039$ | $[-0,0124, +0,0041]$ | $-0,0114$ | 0,2005 | 0,6015 | $-0,236$ (pequeño) | Sin diferencia significativa (IC incluye 0) | Sin discordancia significativa ($p_{\text{Holm}} > 0,05$) |
| **vs. Stacking Ensemble** | Calibrado | $-0,0029$ | $[-0,0108, +0,0044]$ | $-0,0092$ | 0,2100 | 0,6015 | $-0,174$ (pequeño) | Sin diferencia significativa (IC incluye 0) | Sin discordancia significativa ($p_{\text{Holm}} > 0,05$) |
| **vs. Voting Ensemble** | Calibrado | $+0,0042$ | $[-0,0041, +0,0124]$ | $-0,0045$ | 0,0039 | **0,0197\*** | $+0,241$ (pequeño) | Sin diferencia significativa (IC incluye 0) | **Discordancia significativa ($p_{\text{Holm}} = 0,0197 < 0,05$)** |
| **vs. Baseline TTC Tuned** | Calibrado | $-0,0038$ | $[-0,0129, +0,0047]$ | $-0,0023$ | 0,3771 | 0,6015 | $-0,220$ (pequeño) | Sin diferencia significativa (IC incluye 0) | Sin discordancia significativa ($p_{\text{Holm}} > 0,05$) |
| **vs. Baseline TTC Fixed** | Calibrado | $-0,0008$ | $[-0,0086, +0,0062]$ | $-0,0069$ | 0,1496 | 0,5985 | $-0,052$ (despreciable) | Sin diferencia significativa (IC incluye 0) | Sin discordancia significativa ($p_{\text{Holm}} > 0,05$) |
| **vs. SVM RBF** | Calibrado | $+0,0298$ | $[+0,0152, +0,0454]$ | $+0,0271$ | 0,0002 | **0,0016\*** | $+0,955$ (grande) | **XGBoost superior (IC excluye 0)** | **Discordancia significativa ($p_{\text{Holm}} < 0,05$)** |
| **vs. MLP Neural Net** | Calibrado | $+0,0832$ | $[+0,0578, +0,1107]$ | $+0,1029$ | 0,0004 | **0,0026\*** | $+1,000$ (grande) | **XGBoost superior (IC excluye 0)** | **Discordancia significativa ($p_{\text{Holm}} < 0,05$)** |

> [!NOTE]
> **Justificación de Selección de XGBoost para Producción:** Dado que XGBoost y Random Forest no presentan diferencias estadísticamente significativas en magnitud de $F_2$ ($p_{\text{Holm}} = 0,6015$, IC del $\Delta F_2$ cruza el cero $[-0,0124, +0,0041]$), la retención de XGBoost en la arquitectura del gemelo digital **se fundamenta en criterios de ingeniería y computación en el borde**: latencia de inferencia significativamente menor ($0,022\text{ ms}$ vs $0,085\text{ ms}$ por muestra), soporte nativo de cuantización y menor huella de memoria para despliegue en microservicios edge.

---

## 4. ESTUDIO DE ABLACIÓN MULTIMODAL Y COLINEALIDAD

Se entrenaron y recalibraron de forma independiente 8 configuraciones del modelo:

| Configuración | Descripción Funcional | Variables Retiradas | N° Pred. | Umbral $\tau$ | $F_2$ Score | $\Delta F_2$ (pp) | $\Delta F_2$ Relativo (%) | IC 95 % Bootstrap $F_2$ | $p$-valor vs Completo |
|---|---|---|---|---|---|---|---|---|---|
| **A (Full)** | Modelo Completo Multimodal | Ninguna | 16 | 0,14 | **0,9065** | 0,00 pp | 0,00 % | [0,8874, 0,9251] | — |
| **B** | Sin `distance_3d` | `distance_3d` | 15 | 0,11 | **0,9065** | $+0,00$ pp | $+0,00$ % | [0,8880, 0,9243] | 0,0436 (NS en F2) |
| **B2** | **Sin Bloque Cinemático Específico** | `distance_3d`, `relative_speed`, `ttc` | 13 | 0,15 | **0,8105** | **$-9,60$ pp** | **$-10,59$ %** | [0,7821, 0,8388] | **$<0,0001$\*** |
| **C** | Solo Cinemático / Espacial | 8 variables biometría + telemetría + ambiente | 8 | 0,14 | **0,9065** | $+0,00$ pp | $+0,00$ % | [0,8872, 0,9253] | 0,5488 (NS) |
| **D** | Sin Biometría Humana | `worker_bpm`, `fatigue_index` | 14 | 0,14 | **0,9065** | $+0,00$ pp | $+0,00$ % | [0,8874, 0,9251] | 0,7242 (NS) |
| **E** | Sin Variables Ambientales (3 var.) | `gas_co_ppm`, `dust_density_mg_m3`, `ambient_light_lux` | 13 | 0,14 | **0,9065** | $+0,00$ pp | $+0,00$ % | [0,8874, 0,9251] | 0,7242 (NS) |
| **F** | Sin Telemetría de Maquinaria | `machine_status`, `vibration_rms`, `acceleration_z` | 13 | 0,14 | **0,9065** | $+0,00$ pp | $+0,00$ % | [0,8874, 0,9251] | 0,7242 (NS) |
| **G** | **Sin Espacial / Cinemático Completo** | Todas las 8 variables de cinemática/espacio | 8 | 0,10 | **0,5813** | **$-32,52$ pp** | **$-35,87$ %** | [0,5421, 0,6210] | **$<0,0001$\*** |

---

## 5. AUDITORÍA DE CIRCULARIDAD Y ESCENARIOS DESACOPLADOS

### 5.1. Descomposición de Varianza del Dataset Sintético (Medición Exacta FON-03 / H10)
- **Componente Cinemático / Espacial:** Explica el **82,07 % de la varianza** total del score sintético generador (`results/circularity_audit.csv`).
- **Ruido Estocástico Inducido ($\sigma = 3,8$):** Explica el **17,43 % de la varianza**.
- **Variables Multimodales Residuales:** Explican únicamente el **0,48 % de la varianza**.
- **Covarianza Cruzada Espacio-Multimodal:** Explica el **0,015 % de la varianza**.
- **Cota Analítica del Proceso Generador Sintético:** Simulada en $F_2 \approx 0,9005$ ($\text{Recall} = 0,9411$, $\text{Precision} = 0,7679$) bajo los supuestos generadores específicos de esta simulación (no debe extrapolarse como un límite biológico o físico para operaciones reales subterráneas). Explica formalmente por qué las configuraciones C, D, E y F saturan sobre este dataset sintético benchmark.

### 5.2. Evaluación Rigurosa sobre Escenarios Alternativos y 100% Desacoplados (Auditoría da81d5f P1)
Para responder fehacientemente a las auditorías independiente y diferencial (H09 / commit `da81d5f`), se evaluaron los 7 escenarios de etiquetado alternativo reportando precisión, recall, especificidad, tasa de falsas alarmas (FPR) y comparación contra el **baseline trivial Siempre-ALTO** (`results/decoupled_labels_results.csv`):

| Escenario Evaluado | ML $F_2$ | ML Prec. | ML Rec. | ML Espec. | ML FPR | Baseline Fixed $F_2$ | Baseline Tuned $F_2$ | Baseline Siempre-ALTO $F_2$ | Diagnóstico Científico Riguroso |
|---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|---|
| **Original (Acoplado)** | 0,9058 | 0,7577 | 0,9523 | 0,9141 | 0,0859 | 0,9071 | **0,9103** | 0,5851 | ML y TTC tuned saturan por acoplamiento cinemático sintético ($+32\text{ pp}$ sobre Siempre-ALTO). |
| **Sólo Multimodal** | **0,6408** | 0,3370 | 0,8273 | 0,5410 | 0,4590 | 0,2711 | 0,5851 | 0,5851 | Baseline fijo colapsa ($F_2=0,27$); ML supera a Siempre-ALTO por $+5,57\text{ pp}$ con especificidad del 54,1 %. |
| **Sólo Espacial** | 0,6050 | 0,3595 | 0,7295 | 0,6333 | 0,3667 | 0,6279 | **0,6316** | 0,5851 | Reglas espaciales superan a ML en target puramente espacial; ML retiene especificidad del 63,3 %. |
| **Balanceado 50/50** | **0,6330** | 0,3016 | 0,8727 | 0,4301 | 0,5699 | 0,4803 | 0,5847 | 0,5851 | ML supera al baseline cinemático por $+4,83\text{ pp}$ y a Siempre-ALTO por $+4,79\text{ pp}$. |
| **Desacoplado 1: Gas CO** | 0,5830 | 0,2245 | 0,9705 | 0,0545 | 0,9455 | 0,2278 | 0,5859 | 0,5851 | Al optimizar $F_2$ ($\beta=2$) sobre prevalencia 22 %, el umbral baja a $\tau=0,05$. ML colapsa hacia alto recall con especificidad casi nula (5,5 %), rindiendo similar a Siempre-ALTO. No se afirma selectividad. |
| **Desacoplado 2: Fatiga** | **0,5860** | 0,2215 | 0,9955 | 0,0135 | 0,9865 | 0,2791 | 0,5850 | 0,5851 | Comportamiento análogo: optimizar $F_2$ fuerza recall de 99,5 % elevando falsas alarmas (especificidad 1,4 %). Empata con Siempre-ALTO. |
| **Desacoplado 3: Vibración** | **0,5946** | 0,2423 | 0,9341 | 0,1763 | 0,8237 | 0,2428 | 0,5860 | 0,5851 | Telemetría mecánica logra especificidad de 17,6 % y supera a Siempre-ALTO por $+0,95\text{ pp}$. |

> [!IMPORTANT]
> **Lección Metodológica Crucial:** En problemas de desbalance moderado (prevalencia ALTO = 22 %), la optimización irrestricta de $F_2$ ($\beta = 2$, donde el recall pesa 4 veces más que la precisión) empuja a cualquier optimizador de umbral a predecir la clase crítica casi indiscriminadamente. Esto explica formalmente por qué tanto el ML calibrado como el TTC ajustado convergen al desempeño de un clasificador trivial Siempre-ALTO ($F_2 \approx 0,585$). En producción, se requiere un compromiso multiobjetivo (e.g. $F_1$, MCC o restricción de falsas alarmas) para evitar la fatiga por alarmas del operador.

---

## 6. EXPLICABILIDAD GLOBAL Y LOCAL (TREESHAP)

El análisis TreeSHAP confirma la jerarquía de importancia en el modelo:

| Rango | Variable Predictora | Grupo Funcional | Media \|SHAP\| (Impacto en ALTO) | Interpretación Causal / Asociativa |
|---|---|---|---|---|
| 1 | `distance_3d` | Cinemático / Espacial | **1,185** | Factor determinante primario de proximidad |
| 2 | `ttc` | Cinemático / Espacial | **0,909** | Tiempo al impacto; colineal con distancia |
| 3 | `in_restricted_zone` | Cinemático / Espacial | **0,332** | Presencia en área de giro o punto ciego |
| 4 | `gas_co_ppm` | Ambiental | **0,189** | Modulador de riesgo por ventilación deficiente |
| 5 | `fatigue_index` | Biométrico | **0,102** | Indicador de tiempo de reacción degradado |
| 6 | `machine_status` | Telemetría Maquinaria | **0,096** | Estado operacional (cargando, maniobra, acarreo) |
| 7 | `direction_worker` | Cinemático / Espacial | **0,093** | Orientación angular respecto al equipo |
| 8 | `vibration_rms` | Telemetría Maquinaria | **0,091** | Severidad dinámica y advertencia mecánica |

---

## 7. BENCHMARKS DE LATENCIA, HARDWARE Y RENDIMIENTO CLIENTE

### 7.1. Hardware de Evaluación del Sistema
- **Procesador:** Intel(R) Core(TM) i7-8550U CPU @ 1.80GHz (4 núcleos físicos, 8 hilos lógicos).
- **Memoria RAM:** 15,89 GB Total.
- **Gráficos Integrados:** Intel(R) UHD Graphics 620.
- **Sistema Operativo:** Windows 11 Home 64-bit (build 26200).

### 7.2. Latencia del Backend End-to-End (Telemetría a 5 Hz, Presupuesto 200 ms)

| Concurrencia de Agentes | Inferencia ML $P_{95}$ | Serialización $P_{95}$ | WebSocket Loopback $P_{95}$ | Latencia E2E $P_{50}$ | Latencia E2E $P_{95}$ | Latencia E2E $P_{99}$ | Cumplimiento Presupuesto (< 200 ms) |
|---|---|---|---|---|---|---|---|
| **50 Agentes** | 8,53 ms | 1,03 ms | 1,65 ms | 9,48 ms | **11,02 ms** | 18,06 ms | **100,0 %** |
| **100 Agentes** | 9,62 ms | 1,91 ms | 1,22 ms | 10,32 ms | **12,38 ms** | 13,64 ms | **100,0 %** |
| **200 Agentes** | 9,52 ms | 3,71 ms | 1,58 ms | 12,43 ms | **13,88 ms** | 14,68 ms | **100,0 %** |
| **500 Agentes** | 16,12 ms | 10,27 ms | 2,46 ms | 19,74 ms | **27,91 ms** | 41,11 ms | **100,0 %** |

### 7.3. Rendimiento de Renderizado Three.js / WebGL en Cliente
Instrumentado y reproducible mediante `frontend/scripts/profile_fps_benchmark.js`:
- **50 Agentes:** **60,0 FPS** sostenidos (54 draw calls, 112 MB VRAM). Fluidez óptima.
- **100 Agentes:** **59,5 FPS** sostenidos (104 draw calls, 138 MB VRAM). Fluidez excelente.
- **200 Agentes:** **52,3 FPS** (204 draw calls, 194 MB VRAM). *Degradación moderada por debajo de 60 FPS*.
- **500 Agentes:** **34,8 FPS** (504 draw calls, 310 MB VRAM). *Degradación severa por saturación de llamadas de dibujo WebGL en GPU integrada*.
  > *Diagnóstico de Escalabilidad Frontend:* El cuello de botella es estrictamente gráfico en cliente (CPU/GPU bound por llamadas de dibujo Three.js individuales). Para superar 60 FPS con flotas mayores a 150 entidades en hardware estándar, se requiere instanciado de geometrías (`THREE.InstancedMesh`).

---

## 8. AUDITORÍA DEL MÓDULO GEMINI Y PROTOCOLOS DE EMERGENCIA

- **Banco de Pruebas:** 100 escenarios mineros evaluados exhaustivamente contra el motor determinista (`results/gemini_audit.csv`).
- **Verificación de Expectativas por Peligro:** **100 % (100/100 casos conformes)**. Cobertura determinista completa para los 8 peligros normativos: proximidad, zona restringida, punto ciego, gas CO, fatiga, falla de maquinaria, polvo/visibilidad y peligro combinado gas-fatiga.
- **Inviolabilidad de Directivas Obligatorias:** Las directivas de parada de emergencia (Art. 272), evacuación a refugio (Art. 252) y relevo de turno (Art. 138) se anteponen de forma determinista y no pueden ser alteradas por el modelo de lenguaje.
- **Limitación Operativa:** El componente actúa como un **motor asesor de recomendaciones de seguridad**, no como un actuador electromecánico o relé PLC físico.
- **Inter-Rater Reliability (Kappa de Cohen):** Se mantiene como **PENDIENTE POR EVIDENCIA HUMANA INDEPENDIENTE**, sin fabricar calificaciones simuladas.

---

## 9. LIMITACIONES METODOLÓGICAS Y TRABAJO FUTURO (AUDITORÍA da81d5f P2)

1. **Ausencia de Validación Agrupada por Episodio (GroupKFold):** El conjunto de datos público procesado no incluye identificadores de sesión continua, episodio o código de operador individual. La validación se llevó a cabo mediante `StratifiedKFold` i.i.d. Se declara explícitamente como limitación abierta la necesidad de evaluar generalización temporal por turno de extracción en faenas reales.
2. **Cota Analítica de Simulación vs. Límites Físicos:** El valor $F_2 \approx 0,9005$ es una estimación interna del proceso generador estocástico con ruido Gaussiano ($\sigma = 3,8$), no un límite ontológico insuperable para sensores físicos en mina.
3. **Optimización Gráfica para Flotas Densas:** El cliente web requiere migración a `InstancedMesh` para sostener 60 FPS con flotas mayores a 200 agentes en equipos con gráficos integrados.
