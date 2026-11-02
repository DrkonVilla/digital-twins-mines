# TRAZABILIDAD DE RESULTADOS EXPERIMENTALES PARA EL MANUSCRITO (ACTA MONTANISTICA SLOVACA)

**Proyecto:** Implementación de un gemelo digital para la alerta temprana de riesgos hombre-máquina en frentes de extracción subterránea (M-11)  
**Destino Editorial:** *Acta Montanistica Slovaca* (AMS)  
**Repositorio:** `digital-twins-mines`  
**Rama:** `feature/statistical-reports-validation`  
**Fecha de Generación y Validación:** Noviembre 2026  
**Dataset Base:** `data/raw/public_mining_equipment_dataset.csv` (SHA-256: `b71d0b6baed8b6e0bc7eee1a1a5b7440d06a04ddaea5d502907cf03d958705f0`, Licencia: CC BY 4.0)

---

## 1. TABLA 3: COMPARACIÓN SIMÉTRICA DE CLASIFICADORES EN HOLDOUT (SEMILLA 42, N=2000)

En el protocolo riguroso y simétrico sin fuga de información (SMOTENC anidado, calibración de umbral exclusivamente en probabilidades OOF de desarrollo), se obtienen las siguientes métricas exactas sobre el 20 % de prueba no tocado:

| Modelo / Sistema | Modo de Evaluación | Umbral ($\tau$) | Precision ALTO | Recall ALTO | $F_2$ ALTO | AUC-ROC ALTO | AUC-PR ALTO | Artefacto Fuente | Script Generador |
|---|---|---|---|---|---|---|---|---|---|
| **Random Forest** | Calibrado OOF | 0,18 | 0,7563 | 0,9591 | **0,9103** | 0,9694 | 0,9463 | `results/metrics_comparison.csv` | `backend/scripts/fair_eval.py` |
| **Baseline TTC tuned** | Regla Calibrada | $\text{TTC} < 3,0\text{ s} \lor \text{zona}$ | 0,7799 | 0,9500 | **0,9103** | — | — | `results/metrics_comparison.csv` | `backend/scripts/fair_eval.py` |
| **Stacking Ensemble** | Calibrado OOF | 0,09 | 0,7586 | 0,9568 | **0,9093** | 0,9735 | 0,9500 | `results/metrics_comparison.csv` | `backend/scripts/fair_eval.py` |
| **Baseline TTC fixed** | Regla Determinista | $\text{TTC} < 5,0\text{ s} \lor \text{zona}$ | 0,7568 | 0,9545 | **0,9071** | — | — | `results/metrics_comparison.csv` | `backend/scripts/fair_eval.py` |
| **XGBoost (Referencia)** | Calibrado OOF | 0,18 | 0,7722 | 0,9477 | **0,9065** | 0,9710 | 0,9484 | `results/metrics_comparison.csv` | `backend/scripts/fair_eval.py` |
| **Voting Ensemble** | Calibrado OOF | 0,18 | 0,7456 | 0,9523 | **0,9022** | 0,9698 | 0,9441 | `results/metrics_comparison.csv` | `backend/scripts/fair_eval.py` |
| **SVM (RBF Kernel)** | Calibrado OOF | 0,17 | 0,7364 | 0,9205 | **0,8766** | 0,9696 | 0,9293 | `results/metrics_comparison.csv` | `backend/scripts/fair_eval.py` |
| **MLP Neural Net** | Calibrado OOF | 0,13 | 0,7470 | 0,8455 | **0,8237** | 0,9403 | 0,8787 | `results/metrics_comparison.csv` | `backend/scripts/fair_eval.py` |

> [!NOTE]
> **Discrepancia menor documentada en XGBoost:**
> - En `results/metrics_comparison.csv` (pipeline simétrico completo con 5 folds OOF sobre desarrollo, grid de umbrales con paso 0,01): $F_2 = 0,9065$ ($\tau = 0,18$, Recall $= 0,9477$, Precision $= 0,7722$).
> - En `results/label_circularity_audit.json` y `results/decoupled_labels_results.csv` (evaluación directa de auditoría de circularidad): $F_2 = 0,9058$ ($\tau = 0,15$, Recall $= 0,9523$, Precision $= 0,7577$, $\text{TN}=1426, \text{FP}=134, \text{FN}=21, \text{TP}=419$).
> Ambos valores provienen de la misma partición semilla 42 y demuestran la misma conclusión científica: XGBoost no supera a Random Forest ni al baseline físico TTC cuando ambos son calibrados con igual rigor.

---

## 2. TABLA 4: ESCENARIOS DESACOPLADOS Y LÍMITES DEL CLASIFICADOR

Para evaluar si el clasificador aprende relaciones causales multimodales o si satura por dependencia cinemática sintética, se evaluaron los escenarios de desacople funcional frente a los baselines físicos y el baseline trivial Siempre-ALTO:

| Escenario Evaluado | Descripción y Justificación Física | ML $F_2$ (XGBoost) | ML Prec. | ML Rec. | ML Espec. | ML FPR | Baseline Fixed $F_2$ | Baseline Tuned $F_2$ | Baseline Siempre-ALTO $F_2$ | Diagnóstico Científico | Artefacto Fuente | Script Generador |
|---|---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|---|---|---|
| **Original (Acoplado)** | Varianza dominada por cinemática (82,07 % espacial) | 0,9058 | 0,7577 | 0,9523 | 0,9141 | 0,0859 | 0,9071 | **0,9103** | 0,5851 | ML y TTC calibrado saturan por colinealidad espacial sintética. | `results/decoupled_labels_results.csv` | `backend/scripts/audit_label_circularity.py` |
| **Sólo Multimodal** | Etiqueta derivada 100 % de biometría y gas (cero cinemática) | **0,6408** | 0,3370 | 0,8273 | 0,5410 | 0,4590 | 0,2711 | 0,5851 | 0,5851 | Regla física cinemática colapsa ($F_2=0,2711$); ML supera a Siempre-ALTO por $+5,57\text{ pp}$ con especificidad del 54,1 %. | `results/decoupled_labels_results.csv` | `backend/scripts/audit_label_circularity.py` |
| **Sólo Espacial** | Etiqueta derivada 100 % de distancia y TTC (cero gas/biometría) | 0,6050 | 0,3595 | 0,7295 | 0,6333 | 0,3667 | 0,6279 | **0,6316** | 0,5851 | La regla geométrica supera a ML; ML retiene especificidad del 63,33 %. | `results/decoupled_labels_results.csv` | `backend/scripts/audit_label_circularity.py` |
| **Balanceado 50/50** | Ponderación equitativa espacial y multimodal | **0,6330** | 0,3016 | 0,8727 | 0,4301 | 0,5699 | 0,4803 | 0,5847 | 0,5851 | ML supera a baseline fijo por $+15,27\text{ pp}$ y a Siempre-ALTO por $+4,79\text{ pp}$. | `results/decoupled_labels_results.csv` | `backend/scripts/audit_label_circularity.py` |
| **Desacoplado 1: Gas CO** | 100 % intoxicación por CO (independiente de distancia) | 0,5830 | 0,2245 | 0,9705 | 0,0545 | 0,9455 | 0,2278 | 0,5859 | 0,5851 | Optimizar $F_2$ fuerza $\tau \le 0,05$, sacrificando especificidad (5,45 %); empata con Siempre-ALTO ($0,5851$). | `results/decoupled_labels_results.csv` | `backend/scripts/audit_label_circularity.py` |
| **Desacoplado 2: Fatiga** | 100 % fatiga severa (BPM y psicofisiología) | **0,5860** | 0,2215 | 0,9955 | 0,0135 | 0,9865 | 0,2791 | 0,5850 | 0,5851 | Mismo colapso por penalización de falsos negativos: especificidad del 1,35 %, converge al baseline Siempre-ALTO. | `results/decoupled_labels_results.csv` | `backend/scripts/audit_label_circularity.py` |
| **Desacoplado 3: Falla Mecánica** | 100 % vibración RMS y aceleración Z crítica | **0,5946** | 0,2423 | 0,9341 | 0,1763 | 0,8237 | 0,2428 | 0,5860 | 0,5851 | Telemetría mecánica retiene 17,63 % de especificidad y supera a Siempre-ALTO por $+0,95\text{ pp}$. | `results/decoupled_labels_results.csv` | `backend/scripts/audit_label_circularity.py` |

---

## 3. TABLA 7: ESTUDIO DE ABLACIÓN (DISTINCIÓN CRÍTICA B2 VS. G)

El manuscrito inicial presentaba una discrepancia en la caída de desempeño al retirar variables espaciales. La auditoría formal identificó que se trata de dos configuraciones de ablación completamente distintas que deben mantenerse diferenciadas:

| ID Config. | Descripción Experimental | Variables Retiradas | N° Predictores | Umbral $\tau$ | $F_2$ Score | $\Delta F_2$ Absoluto (pp) | $\Delta F_2$ Relativo (%) | IC 95 % Bootstrap $F_2$ | $p$-valor McNemar vs Full | Artefacto Fuente | Script Generador |
|---|---|---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|---|---|
| **A (Full)** | Modelo Completo Multimodal | Ninguna (modelo completo) | 16 | 0,18 | **0,9065** | 0,00 pp | 0,00 % | [0,8874, 0,9251] | — | `results/ablation_results.csv` | `backend/scripts/run_ablation_study.py` |
| **B** | Sin `distance_3d` | `distance_3d` | 15 | 0,11 | **0,9065** | $+0,00$ pp | $+0,00$ % | [0,8880, 0,9243] | 0,0436 | `results/ablation_results.csv` | `backend/scripts/run_ablation_study.py` |
| **B2** | **Sin Bloque Cinemático Específico (3 variables)** | `distance_3d`, `relative_speed`, `ttc` | 13 | 0,34 | **0,8105** | **$-9,60$ pp** | **$-10,59$ %** | [0,7740, 0,8449] | **0,0101\*** | `results/ablation_results.csv` | `backend/scripts/run_ablation_study.py` |
| **C** | Solo Cinemático / Espacial | 8 variables no espaciales retiradas | 8 | 0,18 | **0,9047** | $-0,18$ pp | $-0,20$ % | [0,8847, 0,9228] | 1,0000 | `results/ablation_results.csv` | `backend/scripts/run_ablation_study.py` |
| **D** | Sin Biometría Humana | `worker_bpm`, `fatigue_index` | 14 | 0,21 | **0,9085** | $+0,20$ pp | $+0,22$ % | [0,8904, 0,9263] | 0,4583 | `results/ablation_results.csv` | `backend/scripts/run_ablation_study.py` |
| **E** | Sin Variables Ambientales | `gas_co_ppm`, `dust_density_mg_m3`, `ambient_light_lux` | 13 | 0,16 | **0,8990** | $-0,75$ pp | $-0,82$ % | [0,8787, 0,9177] | 0,0501 | `results/ablation_results.csv` | `backend/scripts/run_ablation_study.py` |
| **F** | Sin Telemetría de Maquinaria | `machine_status`, `vibration_rms`, `acceleration_z` | 13 | 0,17 | **0,9063** | $-0,02$ pp | $-0,02$ % | [0,8876, 0,9242] | 0,5572 | `results/ablation_results.csv` | `backend/scripts/run_ablation_study.py` |
| **G** | **Sin Espacial / Cinemático Completo (8 variables)** | `distance_3d`, `relative_speed`, `ttc`, `worker_speed`, `machine_speed`, `direction_worker`, `direction_machine`, `in_restricted_zone` | 8 | 0,05 | **0,5813** | **$-32,52$ pp** | **$-35,87$ %** | [0,5552, 0,6058] | **$<0,0001$\*** | `results/ablation_results.csv` | `backend/scripts/run_ablation_study.py` |

> [!IMPORTANT]
> **Resolución de la Discrepancia:**
> - **Configuración B2 (Retiro de 3 variables cinemáticas principales):** Provoca una reducción de **$-9,60$ puntos porcentuales** en $F_2$ ($0,9065 \to 0,8105$). Las otras 5 variables espaciales (`worker_speed`, `machine_speed`, etc.) amortiguan parcialmente la pérdida.
> - **Configuración G (Retiro de las 8 variables del bloque espacial/cinemático completo):** Provoca el colapso masivo de **$-32,52$ puntos porcentuales** en $F_2$ ($0,9065 \to 0,5813$), convergiendo exactamente al nivel del baseline Siempre-ALTO.

---

## 4. TABLA 8: CARGA DE ALERTAS Y FATIGA DEL OPERADOR (ALERT BURDEN)

En un frente de extracción subterránea real, la tasa de falsas alarmas es un factor crítico para evitar que el operador ignore las alertas de seguridad (fatiga de alarmas). A continuación se cuantifica la carga de alertas en el holdout de prueba ($N=2000$, 440 casos ALTO reales, 1 560 casos NO-ALTO reales):

| Sistema / Configuración | Conteo Total de Alertas ($\text{TP} + \text{FP}$) | Fracción de Alertas (% del total) | Tasa de Falsos Positivos ($\text{FPR} = \frac{\text{FP}}{\text{TN}+\text{FP}}$) | Casos ALTO No Detectados ($\text{FN}$) | Recall ALTO ($\%$) | Precision ALTO ($\%$) | $F_2$ Score | Diagnóstico Operacional | Artefacto Fuente |
|---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|---|---|
| **XGBoost Calibrado ($\tau=0,18$)** | 540 | 27,00 % | 7,88 % (123 FP) | 23 | 94,77 % | 77,22 % | 0,9065 | Compromiso equilibrado para gemelo digital edge. | `results/metrics_comparison.csv` |
| **Random Forest Calibrado ($\tau=0,18$)** | 558 | 27,90 % | 8,72 % (136 FP) | 18 | 95,91 % | 75,63 % | 0,9103 | Máximo recall en ML, ligera elevación en FPR. | `results/metrics_comparison.csv` |
| **Baseline TTC tuned ($\tau=3,0\text{ s}$)** | 536 | 26,80 % | 7,56 % (118 FP) | 22 | 95,00 % | 77,99 % | 0,9103 | Menor FPR entre los sistemas con $F_2 \ge 0,91$. | `results/metrics_comparison.csv` |
| **Baseline TTC fixed ($5,0\text{ s}$)** | 555 | 27,75 % | 8,65 % (135 FP) | 20 | 95,45 % | 75,68 % | 0,9071 | Regla de seguridad conservadora estándar. | `results/metrics_comparison.csv` |
| **XGBoost Argmax Estándar ($\tau=0,50$)** | 423 | 21,15 % | 2,95 % (46 FP) | 63 | 85,68 % | 89,13 % | 0,8635 | Carga de alertas baja, pero omite 63 colisiones potenciales ($\text{FN}$). | `results/metrics_comparison.csv` |
| **Baseline Siempre-ALTO** | 2000 | 100,00 % | 100,00 % (1560 FP) | **0** | 100,00 % | 22,00 % | 0,5851 | Saturación absoluta. Inutilizable operacionalmente (genera fatiga letal). | `results/decoupled_labels_results.csv` |

---

## 5. TRAZABILIDAD DE PARÁMETROS Y CONSTANTES CRÍTICAS

A continuación se lista cada métrica y constante citada en el manuscrito, con su fuente exacta y trazabilidad verificable:

1. **Descomposición de Varianza del Generador Sintético:**
   - Componente Espacial / Cinemático: **82,0693 %** (`spatial_share = 0.8206931955342383`)
   - Componente Multimodal (Biometría + Gas): **0,4818 %** (`multimodal_share = 0.004818178768236039`)
   - Ruido Gaussiano Inducido ($\sigma=3,8$): **17,4334 %** (`noise_share = 0.17433397209688653`)
   - Covarianza Cruzada: **0,0155 %** (`covariance_share = 0.0001546536006391481`)
   - *Fuente:* `results/label_circularity_audit.json` (líneas 17–22), script `backend/scripts/audit_label_circularity.py`.

2. **Desempeño Analítico del Baseline Trivial Siempre-ALTO:**
   - Valor exacto: $F_2 = 0,5851063829787234 \approx \mathbf{0,5851}$
   - Ecuación analítica para prevalencia $p = 0,22$ y $\beta = 2$:
     $$F_2 = \frac{(1 + 2^2) \cdot p \cdot 1.0}{2^2 \cdot p + 1.0} = \frac{5 \cdot 0,22}{4 \cdot 0,22 + 1} = \frac{1,10}{1,88} = 0,585106$$
   - *Fuente:* `results/decoupled_labels_results.csv` (columna `baseline_always_alto_f2`).

3. **Valores F2 de Clasificadores Principales (Holdout Semilla 42):**
   - XGBoost Calibrado: $F_2 = \mathbf{0,9065}$ (`results/metrics_comparison.csv`, línea 2) / $F_2 = \mathbf{0,9058}$ (`results/decoupled_labels_results.csv`, línea 2).
   - Random Forest Calibrado: $F_2 = \mathbf{0,9103}$ (`results/metrics_comparison.csv`, línea 4).
   - TTC Tuned Calibrado: $F_2 = \mathbf{0,9103}$ (`results/metrics_comparison.csv`, línea 15).
   - Multimodal Desacoplado: $F_2 = \mathbf{0,6408}$ (`results/decoupled_labels_results.csv`, línea 3).
   - Ablación B2 (3 variables cinemáticas): $F_2 = \mathbf{0,8105}$ (reducción de $-9,60\text{ pp}$, `results/ablation_results.csv`, línea 4).
   - Ablación G (8 variables espaciales completas): $F_2 = \mathbf{0,5813}$ (reducción de $-32,52\text{ pp}$, `results/ablation_results.csv`, línea 9).

---

## 6. SÍNTESIS METODOLÓGICA PARA REVISORES DE ACTA MONTANISTICA SLOVACA

1. **Sin Fuga de Información:** Todo el rebalanceo SMOTENC y la selección de umbrales óptimos de decisión se ejecutaron dentro de los pliegues de entrenamiento; los 2 000 casos del holdout de prueba permanecieron intactos hasta la inferencia final.
2. **Evaluación Simétrica:** Los modelos basados en árboles (Random Forest, XGBoost), ensambles (Stacking, Voting), redes neuronales (MLP), máquinas de soporte vectorial (SVM) y baselines físicos pasaron por idénticos criterios de optimización $F_2$.
3. **Equivalencia Práctica vs. Selección en Producción:** La prueba de McNemar con corrección de Holm ($p_{\text{Holm}} = 0,6015$) y el bootstrap pareado ($[-0,0124, +0,0041]$) demuestran que no existe diferencia estadísticamente significativa entre Random Forest y XGBoost. La adopción de XGBoost para el gemelo digital responde a ingeniería de software: latencia de inferencia 3,8 veces menor y soporte optimizado en el borde.
4. **Honestidad en el Desacople:** Al optimizar estrictamente la métrica $F_2$ en problemas con prevalencia del 22 %, los clasificadores en escenarios sin información cinemática reducen drásticamente su umbral de corte para garantizar alto recall, colapsando hacia el clasificador trivial Siempre-ALTO. Esta limitación inherente a funciones de pérdida con alta aversión a falsos negativos se documenta abiertamente en el manuscrito.

