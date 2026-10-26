# DECLARACIÓN TRANSPARENTE DE LIMITACIONES PENDIENTES DEL SISTEMA M-11

**Proyecto:** Implementación de un gemelo digital para la alerta temprana de riesgos de interacción hombre-máquina en frentes de extracción subterránea  
**Manuscrito Destino:** *Acta Montanistica Slovaca*  
**Fecha:** Octubre 2026  
**Principio Rector:** Rigor y honestidad científica conforme al estándar COPE y políticas editoriales de Scopus Q1/Q2. No se fabrican ni extrapolan resultados sin respaldo empírico.  

---

## 1. INTRODUCCIÓN

En concordancia con las reglas obligatorias del Prompt Maestro, cualquier aspecto que requiera experimentación de campo, datos externos no presentes en el repositorio o validación subjetiva humana ha sido clasificado formalmente como **PENDIENTE POR EVIDENCIA** o **LIMITACIÓN DEL ESTUDIO**. Esta declaración transparente fortalece la credibilidad científica del manuscrito, transformando presuntas afirmaciones infundadas en futuras líneas de investigación delimitadas con precisión técnica.

---

## 2. INVENTARIO DE LIMITACIONES TÉCNICAS Y CIENTÍFICAS

### 2.1. Naturaleza Sintética del Dataset Híbrido
- **Estado:** Identificada y delimitada.
- **Descripción:** El estudio emplea un conjunto de datos híbrido de 10 000 registros constituido por el benchmark sintético UCI AI4I 2020 fusionado con variables biomecánicas, ambientales y cinemáticas generadas mediante simulación numérica.
- **Implicancia Científica:** Los registros **no proceden de trazas directas de sensores físicos UWB/RFID ni de buses CAN J1939 de maquinaria operando en una mina subterránea real**. El modelo demuestra viabilidad arquitectónica, algorítmica y de procesamiento de flujos, pero no puede declararse como un sistema validado en entorno operativo industrial (TRL 4, no TRL 7).

### 2.2. Emulación Cinemática vs. Propagación Electromagnética Real
- **Estado:** Identificada y delimitada.
- **Descripción:** Las coordenadas $(x, y, z)$, velocidades y distancias entre operarios y equipos (LHD/Scoop) son emuladas cinemáticamente mediante ecuaciones de movimiento.
- **Implicancia Científica:** La simulación asume condiciones ideales de propagación de señales de radiofrecuencia (UWB/RFID). En labores subterráneas reales, existen fenómenos severos de dispersión por trayectorias múltiples (*multipath*), reflexiones en paredes rocosas mineralizadas, desvanecimiento de señal y obstrucciones electromagnéticas por la propia estructura masiva del equipo de acarreo, lo que puede degradar la precisión del posicionamiento tridimensional.

### 2.3. Ausencia de Identificadores de Episodio para Validación Agrupada (`GroupKFold`)
- **Estado:** PENDIENTE POR EVIDENCIA.
- **Descripción:** El Revisor 2 recomendó incorporar `GroupKFold` o `StratifiedGroupKFold` para evaluar la generalización entre distintos operadores, turnos de trabajo o galerías mineras independientes.
- **Evidencia en el Repositorio:** El archivo `public_mining_equipment_dataset.csv` contiene registros tabulares independientes pero **carece de marcas de tiempo secuenciales continuas (`timestamp`) o identificadores de episodio (`worker_id`, `trajectory_id`, `shift_id`)**.
- **Postura Ética y Decisión Técnica:** En estricto cumplimiento de la regla 4 del Prompt Maestro (*"No inventes identificadores de agrupación sobre datos ya mezclados para aparentar independencia experimental"*), no se generaron identificadores ficticios. Esta limitación se declara explícitamente en el reporte y se propone una extensión al generador sintético para emitir trayectorias etiquetadas por episodio.

### 2.4. Evaluación Humana Dual de Gemini GenAI (Confiabilidad Inter-Evaluador)
- **Estado:** PENDIENTE POR EVIDENCIA HUMANA.
- **Descripción:** El Revisor 1 solicitó evaluar la confiabilidad del módulo de lenguaje natural mediante el índice Kappa de Cohen entre dos supervisores de seguridad minera independientes.
- **Evidencia en el Repositorio:** Se generó el banco de pruebas completo con 100 escenarios mineros y se estructuró la plantilla de doble ciego en `results/genai_audit_review_sheet.csv`.
- **Postura Ética y Decisión Técnica:** En estricto cumplimiento de la regla 5 del Prompt Maestro (*"Prepara instrumentos para evaluación por dos supervisores humanos independientes, pero no simules sus calificaciones ni calcules kappa de Cohen sin evaluaciones reales"*), **no se simularon calificaciones sintéticas**. El software queda preparado con la matriz de evaluación para que un comité humano de seguridad minera asigne los puntajes en una fase experimental posterior.

### 2.5. Latencia de Red en Ambientes Confinados Subterráneos
- **Estado:** PARCIALMENTE RESUELTO (Medido en emulación; pendiente en túnel físico).
- **Descripción:** La telemetría WebSocket del gemelo digital se evaluó exhaustivamente en loopback local ($P_{95} = 11\text{ a }28\text{ ms}$) y bajo emulación de latencia de enlace con 50 ms RTT ($P_{95} = 62,4\text{ ms}$).
- **Implicancia Científica:** Las redes inalámbricas en galerías subterráneas (WiFi mesh, cable radiante *leaky feeder* o LTE privada) están expuestas a variabilidad dinámica de jitter, desconexiones temporales por refracción en curvas y sombras de señal provocadas por fortificaciones metálicas o derrubios. Se requiere instrumentar un testbed físico en galería subterránea para certificar la latencia de campo.

### 2.6. Rendimiento de Renderizado Cliente en Dispositivos con GPU Integrada
- **Estado:** Identificada y auditada.
- **Descripción:** El cliente Three.js alcanza 60 FPS con hasta 100 agentes concurrentes, pero desciende a 34,8 FPS cuando se instancian 500 agentes con mallas 3D independientes en una GPU integrada Intel UHD 620.
- **Implicancia Científica:** La afirmación del artículo de "60 FPS universales" no es verídica bajo alta concurrencia en hardware de oficina. El gemelo digital requiere la adopción de mallas instanciadas (*InstancedMesh*) y optimización de materiales en Three.js para operar a 60 FPS con más de 200 entidades simultáneas.

---

## 3. IMPACTO DE ESTAS LIMITACIONES SOBRE EL ARTÍCULO CIENTÍFICO

Lejos de invalidar la investigación, el reconocimiento honesto y cuantitativo de estas 6 limitaciones sitúa al manuscrito en una posición de **rigor y madurez académica de alto impacto**:

1. El artículo debe titularse y defenderse como un **"Gemelo Digital Ciberfísico para Simulación y Alerta Temprana en Fase de Prototipado"**, no como un despliegue operacional de mina subterránea.
2. La superioridad de XGBoost se reformula con honestidad como una **equivalencia estadística con Random Forest y con el baseline empírico TTC en el escenario circular original**, destacando que la verdadera ventaja del aprendizaje automático radica en **su capacidad de alertar riesgos multimodales desacoplados de la proximidad física (intoxicación por gas, fatiga crítica y fallas dinámicas)**, donde las reglas físicas cinemáticas fallan por completo.
