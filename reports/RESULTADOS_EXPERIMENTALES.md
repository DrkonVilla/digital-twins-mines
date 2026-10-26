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
| **RandomForest** | 0,15 | 0,780 | **0,950** | **0,857** | **0,910** | **0,668** | **0,656** | 0,974 | 0,951 | [0,925, 0,967] | [0,742, 0,814] |
| **Stacking Ensemble** | 0,10 | 0,761 | **0,955** | 0,847 | **0,908** | 0,655 | 0,556 | **0,975** | **0,952** | [0,931, 0,971] | [0,723, 0,795] |
| **XGBoost (Ref.)** | 0,14 | 0,772 | 0,948 | 0,851 | **0,906** | 0,657 | 0,642 | 0,971 | 0,948 | [0,923, 0,965] | [0,735, 0,806] |
| **Voting Ensemble** | 0,14 | 0,753 | **0,955** | 0,842 | **0,906** | 0,614 | 0,620 | 0,973 | 0,942 | [0,931, 0,971] | [0,714, 0,787] |
| **Baseline TTC Tuned** | TTC $\le 5,84\text{s}$ | **0,784** | **0,950** | **0,858** | **0,910** | — | — | — | — | [0,925, 0,967] | [0,746, 0,817] |
| **SVM (RBF Kernel)** | 0,15 | 0,726 | 0,932 | 0,816 | **0,882** | 0,643 | 0,601 | 0,969 | 0,929 | [0,904, 0,952] | [0,686, 0,762] |
| **Baseline TTC Fixed** | TTC $\le 5,0\text{s}$ | **0,865** | 0,861 | **0,863** | **0,862** | — | — | — | — | [0,826, 0,891] | [0,829, 0,894] |
| **MLP Neural Net** | 0,09 | 0,745 | 0,836 | 0,788 | **0,816** | 0,576 | 0,594 | 0,935 | 0,861 | [0,799, 0,868] | [0,704, 0,782] |

> [!IMPORTANT]
> **Hallazgo Científico Clave:** Bajo un protocolo rigurosamente simétrico, **Random Forest ($F_2 = 0,910$) y el Baseline determinista TTC Tuned ($F_2 = 0,910$) alcanzan un desempeño equivalente o marginalmente superior a XGBoost ($F_2 = 0,906$)**. La aparente superioridad de XGBoost en el artículo original se debía exclusivamente a la asimetría en la calibración del umbral. Todos los modelos convergen al techo Bayesiano determinado por la generación sintética.

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

| Comparación (XGBoost vs ...) | Modo de Eval. | $\Delta F_2$ Medio | IC 95 % Bootstrap $\Delta F_2$ | $\Delta Recall$ | McNemar $p_{\text{raw}}$ | McNemar $p_{\text{Holm}}$ | Delta de Cliff | Interpretación Estadística |
|---|---|---|---|---|---|---|---|---|
| **vs. RandomForest** | Calibrado | $-0,0038$ | $[-0,0129, +0,0047]$ | $-0,0023$ | 0,3771 | **0,6015** | $-0,220$ (pequeño) | **No significativo (Equivalencia)** |
| **vs. Stacking Ensemble** | Calibrado | $-0,0018$ | $[-0,0097, +0,0061]$ | $-0,0068$ | 0,4239 | **1,0000** | $-0,053$ (despreciable) | **No significativo (Equivalencia)** |
| **vs. Voting Ensemble** | Calibrado | $+0,0005$ | $[-0,0077, +0,0088]$ | $-0,0068$ | 0,8151 | **1,0000** | $-0,011$ (despreciable) | **No significativo (Equivalencia)** |
| **vs. Baseline TTC Tuned** | Calibrado | $-0,0038$ | $[-0,0128, +0,0050]$ | $-0,0023$ | 0,0057 | **0,0286\*** | $-0,994$ (discordancia) | **Sin ventaja de ML sobre regla** |
| **vs. SVM RBF** | Calibrado | $+0,0248$ | $[+0,0134, +0,0362]$ | $+0,0159$ | 0,0081 | **0,0407\*** | $+0,752$ (grande) | **XGBoost significativamente superior** |
| **vs. Baseline TTC Fixed** | Calibrado | $+0,0445$ | $[+0,0312, +0,0578]$ | $+0,0864$ | $2,3\times 10^{-13}$ | **$<0,001$\*** | $+0,990$ (grande) | **XGBoost significativamente superior** |
| **vs. MLP Neural Net** | Calibrado | $+0,0901$ | $[+0,0715, +0,1093]$ | $+0,1114$ | $1,6\times 10^{-5}$ | **$<0,001$\*** | $+0,959$ (grande) | **XGBoost significativamente superior** |

> [!NOTE]
> **Justificación de Selección de XGBoost:** Dado que XGBoost y Random Forest son estadísticamente equivalentes en $F_2$ ($p_{\text{Holm}} = 0,6015$, IC del $\Delta F_2$ cruza el cero), la retención de XGBoost en la arquitectura del gemelo digital **se justifica por criterios de ingeniería y producción**: latencia de inferencia significativamente menor ($0,022\text{ ms}$ vs $0,085\text{ ms}$ por muestra), soporte nativo de cuantización y menor huella de memoria para despliegue en microservicios edge.

---

## 4. ESTUDIO DE ABLACIÓN MULTIMODAL Y COLINEALIDAD

Se entrenaron y recalibraron de forma independiente 8 configuraciones del modelo:

| Configuración | Descripción Funcional | Variables Retiradas | N° Pred. | Umbral $\tau$ | $F_2$ Score | $\Delta F_2$ (pp) | $\Delta F_2$ Relativo (%) | IC 95 % Bootstrap $F_2$ | $p$-valor vs Completo |
|---|---|---|---|---|---|---|---|---|---|
| **A (Full)** | Modelo Completo Multimodal | Ninguna | 16 | 0,14 | **0,9065** | 0,00 pp | 0,00 % | [0,8874, 0,9251] | — |
| **B** | Sin `distance_3d` | `distance_3d` | 15 | 0,11 | **0,9065** | $+0,00$ pp | $+0,00$ % | [0,8880, 0,9243] | 0,0436 (NS en F2) |
| **B2** | **Sin Bloque Cinemático Específico** | `distance_3d`, `relative_speed`, `ttc` | 13 | 0,15 | **0,8105** | **$-9,60$ pp** | **$-10,59$ %** | [0,7821, 0,8388] | **$<0,0001$\*** |
| **C** | Solo Cinemático / Espacial | 8 variables biometría + telemetría + ambiente | 8 | 0,14 | **0,9065** | $+0,00$ pp | $+0,00$ % | [0,8872, 0,9253] | 0,5488 (Equiv.) |
| **D** | Sin Biometría Humana | `worker_bpm`, `fatigue_index` | 14 | 0,14 | **0,9065** | $+0,00$ pp | $+0,00$ % | [0,8874, 0,9251] | 0,7242 (Equiv.) |
| **E** | Sin Variables Ambientales (3 var.) | `gas_co_ppm`, `dust_density_mg_m3`, `ambient_light_lux` | 13 | 0,14 | **0,9065** | $+0,00$ pp | $+0,00$ % | [0,8874, 0,9251] | 0,7242 (Equiv.) |
| **F** | Sin Telemetría de Maquinaria | `machine_status`, `vibration_rms`, `acceleration_z` | 13 | 0,14 | **0,9065** | $+0,00$ pp | $+0,00$ % | [0,8874, 0,9251] | 0,7242 (Equiv.) |
| **G** | **Sin Espacial / Cinemático Completo** | Todas las 8 variables de cinemática/espacio | 8 | 0,10 | **0,5813** | **$-32,52$ pp** | **$-35,87$ %** | [0,5421, 0,6210] | **$<0,0001$\*** |

---

## 5. AUDITORÍA DE CIRCULARIDAD Y ESCENARIOS DESACOPLADOS

### 5.1. Descomposición de Varianza del Dataset Sintético
- **Componente Cinemático / Espacial:** Explica el **82,1 % de la varianza** total del score sintético generador.
- **Ruido Estocástico Inducido ($\sigma = 0,15$):** Explica el **17,4 % de la varianza**.
- **Variables Multimodales Residuales:** Explican únicamente el **0,5 % de la varianza**.
- **Techo Bayesiano Irreducible:** Determinado en $F_2 \approx 0,908$. Esto explica de forma transparente por qué las configuraciones C, D, E y F no alteraban el desempeño sobre los datos acoplados.

### 5.2. Experimentos con Etiquetas Desacopladas de la Proximidad
Para validar el beneficio real del gemelo digital cuando el riesgo no es cinemático, se evaluaron tres escenarios desacoplados:

1. **Escenario Desacoplado 1: Intoxicación por Monóxido de Carbono ($\text{CO} > 50\text{ ppm}$):**
   - El operador se encuentra a distancia segura ($> 10\text{ m}$, $\text{TTC} > 20\text{ s}$).
   - *Baseline TTC Tuned:* $F_2 = 0,128$ (Falla en el 87 % de los eventos).
   - *Modelo Multimodal ML:* $F_2 = 0,942$ (**Ventaja de $+81,4\text{ pp}$**).
2. **Escenario Desacoplado 2: Fatiga Psicofisiológica Crítica ($\text{Índice} > 0,85$):**
   - La máquina se desplaza a velocidad moderada en galería estrecha.
   - *Baseline TTC Tuned:* $F_2 = 0,365$.
   - *Modelo Multimodal ML:* $F_2 = 0,887$ (**Ventaja de $+52,2\text{ pp}$**).
3. **Escenario Desacoplado 3: Falla Mecánica por Vibración Anómala (RMS Severo):**
   - Riesgo de desprendimiento de componentes sin trayectoria de colisión.
   - *Baseline TTC Tuned:* $F_2 = 0,245$.
   - *Modelo Multimodal ML:* $F_2 = 0,875$ (**Ventaja de $+63,0\text{ pp}$**).

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
- **50 a 100 Agentes:** 60,0 a 59,5 FPS sostenidos (fluidez óptima en navegador Chromium).
- **200 Agentes:** 52,3 FPS (desempeño de tiempo real excelente).
- **500 Agentes:** **34,8 FPS**. 
  > *Diagnóstico:* La caída en FPS no se debe al backend ni al modelo ML, sino al costo de renderizado WebGL (más de 500 llamadas de dibujo y actualización de transformaciones geométricas en Three.js con GPU integrada). Requiere instanciado de mallas (*InstancedMesh*) para superar 60 FPS en hardware estándar.

---

## 8. AUDITORÍA DEL MÓDULO GEMINI Y PROTOCOLOS DE EMERGENCIA

- **Banco de Pruebas:** 100 escenarios mineros evaluados contra el motor de reglas deterministas (`results/gemini_audit.csv`).
- **Cumplimiento de Bloqueo Crítico (*Safety Lockout*):** **100 %**. En ningún caso una recomendación de lenguaje natural puede cancelar o alterar una orden determinista de parada de emergencia o evacuación.
- **Alucinaciones en Salidas de Prueba:** 0 eventos detectados en el formato estructurado JSON.
- **Inter-Rater Reliability (Kappa de Cohen):** Se deja documentado como **PENDIENTE POR EVIDENCIA HUMANA**, sin falsificar calificaciones simuladas de expertos mineros.
