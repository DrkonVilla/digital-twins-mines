## INFORME DE REVISIÓN POR PARES

### 1. Nota de alcance

Se revisó el archivo `M11_Manuscrito_AMS_2026_Espanol_Sin_Nuevas_Referencias.docx` completo: resumen, texto principal, Tablas 1–6, Figuras 1–3, declaraciones, Anexos A–B y 42 referencias. Se inspeccionaron visualmente las tres figuras de contenido. El mensaje no incluyó prompt maestro adicional, por lo que la revisión se rige por las instrucciones de evaluación. No se verificó el repositorio GitHub citado, el código, los datos crudos, el diccionario de variables (el propio Anexo A declara que no se adjuntó), los DOI, las URL ni la indexación. No se recalcularon resultados. Las conclusiones sobre tablas se limitan a su coherencia interna.

El archivo no está corrupto y las tablas son legibles. Sin embargo, el texto contiene marcadores de borrador y lenguaje de proceso interno (“guía”, “dossier”, “versión previa”), secciones anunciadas sin resultados (SHAP, auditoría de Gemini) y un diccionario de variables ausente. Por eso la evaluación de reproducibilidad y de validez del conjunto de datos es necesariamente parcial. La novedad externa no se comprobó.

### 2. Identificación del manuscrito

| Campo                                 | Contenido                                                                                                                                                                                                                                                                                                                                                                                                                                      |
| ------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Título                                | Implementación de un gemelo digital para la alerta temprana de riesgos de interacción hombre-máquina en frentes de extracción subterránea (M-11)                                                                                                                                                                                                                                                                                               |
| Autores                               | Favian Enrique Villa Valdiviezo (autor de correspondencia); Marck Alessandro Hermenegildo Pacheco                                                                                                                                                                                                                                                                                                                                              |
| Afiliación                            | Universidad Nacional de Trujillo, Trujillo, Perú. Correos y teléfono: “pendiente de consignar”                                                                                                                                                                                                                                                                                                                                                 |
| Revista objetivo                      | Acta Montanistica Slovaca (plantilla 2026). Normas editoriales: No consta / No verificable                                                                                                                                                                                                                                                                                                                                                     |
| Área / subárea                        | Seguridad en minería subterránea; sistemas ciberfísicos y aprendizaje automático aplicado; interacción hombre-máquina, alerta de colisión                                                                                                                                                                                                                                                                                                      |
| Tipo de contribución                  | Prueba de concepto basada en simulación (arquitectura de software + evaluación computacional). Contribución aplicada/de ingeniería                                                                                                                                                                                                                                                                                                             |
| Problema                              | Colisiones vehículo-persona e ingreso a zonas restringidas en frentes subterráneos; gestión de seguridad reactiva                                                                                                                                                                                                                                                                                                                              |
| Objetivo general                      | “Diseñar, implementar y evaluar M-11 como una arquitectura ciberfísica de alerta temprana basada en un gemelo digital” para reducir el riesgo de interacción hombre-máquina                                                                                                                                                                                                                                                                    |
| Objetivos específicos                 | No consta (solo P1–P3)                                                                                                                                                                                                                                                                                                                                                                                                                         |
| Preguntas / hipótesis                 | P1: rendimiento de clasificadores frente a TTC. P2: significancia estadística y tamaño del efecto. P3: 60 FPS, 5 Hz y latencia P95 < 200 ms. Sin hipótesis formales                                                                                                                                                                                                                                                                            |
| Método                                | Arquitectura de 4 capas (dispositivo, borde, nube, presentación). Partición 80/20 estratificada (semilla 42). Umbral F2 por predicciones OOF de CV de 5 pliegues. SMOTENC dentro de pliegues. XGBoost, RF, SVM-RBF, MLP, stacking y voting frente a 2 reglas TTC. Bootstrap (1 000), McNemar, Holm, delta de Cliff. Ablación por grupos de variables. Benchmark WebSocket en loopback. TreeSHAP y auditoría de Gemini descritos sin resultados |
| Dataset                               | Híbrido de 10 000 registros y 37 variables: UCI AI4I 2020 + cinemática, biometría y ambiente simulados. Clases 45 / 33 / 22 % (BAJO/MEDIO/ALTO). Etiqueta `risk_level` sintetizada. Diccionario no disponible                                                                                                                                                                                                                                  |
| Resultados declarados                 | Holdout (n = 2 000): XGBoost F2 = 0.907, recall ALTO 94.8 %, precisión 77.2 %, AUC-ROC 0.971, AUC-PR 0.944. RF 0.910; stacking 0.909; TTC calibrado 0.910. Ablación: sin subsistema espacial/cinemático F2 = 0.581. P95 = 13.9 ms (200 agentes) y 27.9 ms (500 agentes)                                                                                                                                                                        |
| Contribuciones reivindicadas          | Integración de posicionamiento, telemetría, geovallado, riesgo explicable y visualización 3D en una arquitectura web; evaluación estadística reproducible; módulo de protocolo de emergencia con LLM                                                                                                                                                                                                                                           |
| Limitaciones reconocidas              | Sin validación de campo; etiqueta potencialmente circular; latencias en loopback; 60 FPS no medidos en concurrencia; SHAP no recalculado; kappa y alucinación de Gemini pendientes; no extrapolable a trabajadores o turnos independientes                                                                                                                                                                                                     |
| Revista objetivo / normas editoriales | Acta Montanistica Slovaca. Idioma y requisitos de formato: No verificable (el manuscrito está en español)                                                                                                                                                                                                                                                                                                                                      |

### 3. Inconsistencias principales

- **Texto de proceso editorial dentro del manuscrito.** Aparecen “la guía de actualización”, “el dossier”, “versión previa”, “antiguo 94 %” y “no incorporado al dossier entregado” (Datos, Desarrollo del modelo, Explicabilidad, Anexo A). Anexo A cierra con “Pendiente antes del envío editorial: insertar la exportación verificable del diccionario”. El texto no es una versión de envío.
- **Placeholders y artefactos de plantilla.** “Correo: pendiente de consignar”, “DOI por asignar”, enlace GitHub duplicado en Disponibilidad de datos y código.
- **Título y objetivo frente a la evidencia.** El título afirma “Implementación de un gemelo digital”, y el objetivo general dice “reducir el riesgo”. El resumen aclara “prueba de concepto basada en simulación” y “no la eficacia de seguridad”. No hay activo físico ni bucle físico-virtual-físico, y no se mide ninguna reducción de riesgo. Fig. 1 declara “flujo bidireccional de telemetría/inferencia”, pero es un flujo de software.
- **Límite de Bayes incoherente (Amenazas a la validez).** Se reporta una referencia estimada de F2 = 0.900 para el límite de Bayes. Los resultados observados “F2 = 0.907–0.910 sobrepasan esa cifra”. Si el límite fuese real, el resultado indicaría fuga o reproducción determinista de la etiqueta. La frase “no se la interpreta como cota matemática” deja la cifra sin función.
- **Equivalencia.** El texto dice “La falta de significación no demuestra equivalencia formal”, pero la Tab. 4 rotula tres filas como “Despreciable (equivalentes)”.
- **TTC calibrado.** Es el comparador más fuerte (F2 = 0.910, Tab. 2) y se destaca en el resumen. No se describe cómo se calibró el umbral de 11 s ni con qué datos. Tampoco aparece en la Tab. 4.
- **Explicabilidad.** Título, resumen y palabras clave dicen “explicable”; la Introducción afirma “También se usan… TreeSHAP”. Los resultados reconocen que “no se dispone… de valores SHAP recalculados”.
- **Métricas anunciadas y no reportadas.** La Introducción menciona F1, pero no se reporta F1. El resumen cita la validación cruzada de cinco pliegues, pero no se presentan métricas de CV.
- **Multimodalidad.** En la Tab. 6, la configuración G (sin espacio/cinemática) tiene AUC = 0.489 y precisión 21.9 %, equivalente a azar frente a una prevalencia de 22.0 %. Biometría (D: F2 sube a 0.908) y telemetría de máquina (F: −0.02 pp) no aportan. Ambiente aporta −0.75 pp (E). Esto contradice el rótulo “híbrido multimodal” y la integración como contribución.
- **Conteo de variables.** Tab. 1: 16 predictores. Anexo A nombra 14 señales operativas. En Tab. 6 (fila E), “Sin ambiental (gases, polvo)” resta 3 variables (13), pero solo se nombran 2.
- **Variables de fallo.** El Anexo A lista `failure_flag`, `TWF`, `HDF`, `PWF`, `OSF` como “campos de maquinaria”. No se declara si son predictores. Si lo fueran, serían variables post-evento.
- **Origen de la telemetría.** Métodos: “trazas CAN J1939 de máquinas LHD”. Datos: la maquinaria proviene de UCI AI4I 2020. No se indica de dónde salen las trazas CAN. El texto presenta UWB/RFID y CAN como recolección en la capa de dispositivo y luego como “interfaces propuestas… sin reportar un despliegue”.
- **AI4I descrito como real.** Se habla de “benchmarks reales de equipos industriales” y “par motor real”. La documentación pública habitual del AI4I lo describe como sintético. Los autores deben confirmarlo y declararlo (no verificado externamente aquí).
- **Fig. 1 frente al texto.** La figura asigna al borde “Fusión de características” y “cálculo de TTC”, mientras el texto limita el borde a ingesta, normalización y búfer. Aparecen sensores PPG/IMU/gas-polvo y “UCI AI4I” en la capa de dispositivos, sin respaldo textual.
- **Fig. 2.** Los ejes muestran una galería de 40 × 8 × 5 m, frente a 500 × 300 m y −800 m en el texto. Hay etiquetas superpuestas (“Equipo L…”, “Cono de colisión”). Parece un gráfico 3D estático, no una captura del visor Three.js, y esto no es verificable.
- **P3 parcialmente sin evidencia.** Se pregunta por 60 FPS concurrentes, pero el texto reconoce que no hay medición sincronizada ni identificación de GPU.
- **Terminología.** “Gemelo digital” se usa como sinónimo de simulación con visualización. “Tiempo real” se usa sin garantía temporal (Python sobre Windows, loopback, sin análisis de jitter). “CRISPR-DM” no aparece. El término “aprendizaje automático” está bien aplicado, pues hay algoritmos de ML.
- **Estilo y formato numérico.** Registro coloquial (“o sea”, “salen de”, “así que”), errores gramaticales (“se gestiona este proceso”, “mientras y un vehículo”, “se derivan”, “asi”, “mas”). Separadores decimales mezclados (“0.907” frente a “45,0 %”, “96,7 %”, “1,5 s”).

### 4. Resumen ejecutivo

**Fortaleza y contribución potencial.** El trabajo es transparente sobre sus límites: se declara prueba de concepto, se reconoce la circularidad de la etiqueta, se evita atribuir métricas humanas no verificadas al asistente generativo y se advierte que las latencias en loopback no predicen redes mineras. El diseño de evaluación tiene buenas prácticas (umbral por OOF sin tocar el holdout, SMOTENC dentro de pliegues, comparación simétrica con línea base determinista, inferencia pareada con Holm, ablación con reoptimización del umbral). La arquitectura puede servir como banco de pruebas computacional para estudiar alertas de proximidad en minería subterránea.

**Debilidades críticas.** (i) La etiqueta es sintética y generada en gran parte por el mismo componente cinemático-espacial que usa la regla TTC (82.1 % de la varianza). Por eso el aprendizaje automático no supera una regla de un solo parámetro, y las métricas no informan sobre desempeño real. (ii) El generador de etiquetas, la fusión AI4I-simulación, el diccionario de 16 predictores y los hiperparámetros no están documentados, de modo que no puede descartarse fuga ni reproducir el resultado central. (iii) Se anuncian explicabilidad (SHAP) y auditoría de Gemini sin resultados. (iv) El benchmark de latencia es limitado y no sostiene “tiempo real”. (v) El documento contiene lenguaje de proceso interno y marcadores pendientes. (vi) El alcance nominal (“gemelo digital”, “multimodal”, “alerta temprana”, “reducir el riesgo”) excede lo demostrado.

**Riesgo científico: moderado**, y alto para las afirmaciones de valor añadido multimodal y explicabilidad. **Recomendación editorial preliminar: Major revisions.** Si no se resuelven la circularidad (con un análisis de etiquetas desacopladas totalmente documentado), la documentación del dataset y la eliminación del contenido incompleto, procedería una decisión más severa (**Reject and resubmit**).

### 5. Valoración general

El artículo aporta una arquitectura integrada (adquisición propuesta, cálculo de TTC y geovallado, clasificación, visualización 3D y módulo asistido por LLM) y una evaluación computacional con protocolo estadístico más cuidadoso de lo habitual en trabajos aplicados. Su valor principal es de ingeniería y metodológico-exploratorio, no empírico: no hay datos de mina, y el aporte de modelado se limita a mostrar que con etiquetas sintéticas derivadas de la cinemática, un clasificador y una regla TTC rinden igual.

La principal fortaleza es la honestidad sobre el alcance y la inclusión de una línea base determinista calibrada. La principal limitación es que la validez de constructo de la variable objetivo no se sostiene: sin verdad de terreno independiente, los valores de F2, AUC y la ablación describen el generador, no el riesgo operacional. El alcance declarado en el título y el objetivo general está sobredimensionado. Las conclusiones del texto sí están moderadas (“viabilidad computacional bajo simulación”), pero el título, el nombre “gemelo digital” y la promesa de “reducir el riesgo” no lo están.

### 6. Evaluación de fondo

| Criterio                                      | Nota (0–20) | Evidencia examinada                                               | Deficiencia detectada                                                                                                                                                                                                                                | Justificación de la nota                                                                | Acción recomendada                                                                                                       |
| --------------------------------------------- | ----------- | ----------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------ |
| Novelty y originalidad (15 %)                 | 8           | Introducción (brecha); Tab. 2; Tab. 6; Anexo B                    | La brecha se enuncia sin comparación sistemática; el ML no supera a TTC; integración sin elemento técnico diferencial demostrado                                                                                                                     | La novedad es de integración de software; el aporte analítico se anula por circularidad | Contrastar con sistemas de detección de proximidad y anticolisión; definir qué valor añade el ML (Anexo B desarrollado)  |
| Relevancia y contribución (10 %)              | 13          | Resumen; Introducción; Discusión                                  | Tema relevante; contribución limitada a prueba de concepto                                                                                                                                                                                           | Relevancia alta, evidencia de contribución baja-moderada                                | Reformular título y contribución como banco de pruebas                                                                   |
| Estado del arte (10 %)                        | 11          | Introducción (“Análisis del problema”); 42 referencias            | Muchas citas tangenciales (construcción, grúas torre, tunelización). Faltan literatura de proximidad/anticolisión, medidas sustitutas de seguridad (TTC) y validez de datos sintéticos                                                               | Actual (74 % de 2024–2026), pero poco enfocado en el problema específico                | Añadir revisión focalizada y tabla comparativa                                                                           |
| Rigor metodológico (15 %)                     | 8           | Datos; Desarrollo del modelo; Tab. 1–3; Anexo A                   | Generador de etiquetas no descrito; diccionario ausente; unidad de observación y dependencia temporal sin tratar; variables posiblemente post-evento; hiperparámetros omitidos                                                                       | Buen esqueleto de validación, pero sobre un dato opaco                                  | Documentar generador y diccionario; partición agrupada; auditoría de fuga                                                |
| Reproducibilidad (10 %)                       | 8           | Disponibilidad de datos y código; Resultados (versiones); Anexo A | Repositorio no verificable; sin commit/DOI; diccionario, predicciones y scripts “deben vincularse”                                                                                                                                                   | Hay semilla y versiones, pero no el generador ni los hiperparámetros                    | Publicar versión archivada con checklist                                                                                 |
| Análisis estadístico (15 %)                   | 10          | Tab. 2, 4, 6; texto de Resultados                                 | McNemar aplicado a diferencias de F2; delta de Cliff sin definición para decisiones pareadas; “equivalentes” sin prueba; TTC calibrado fuera de Tab. 4; ablación con p sin método ni IC; sin resultados de CV; una sola semilla y una sola partición | Buenas prácticas (bootstrap pareado, Holm) con elecciones inferenciales mal ajustadas   | Rehacer inferencia con bootstrap pareado de ΔF2 para todos los comparadores; TOST con margen; repetir partición/semillas |
| Discusión, limitaciones y conclusiones (10 %) | 14          | Discusión; Amenazas a la validez; Conclusiones                    | Cita de límite de Bayes incoherente; Anexo B sin protocolo; algunas afirmaciones sin respaldo (“conos de colisión… alertas más graduales”)                                                                                                           | Limitaciones bien reconocidas; conclusiones moderadas                                   | Eliminar o derivar el límite de Bayes; sustentar afirmaciones operativas                                                 |
| Estructura (4 %)                              | 8           | Secciones y anexos                                                | Lenguaje de proceso; subsecciones de Resultados mezclan métodos; “Análisis del problema” como revisión; anexos con pendientes                                                                                                                        | Estructura reconocible pero no de envío                                                 | Reestructurar según IMRyD y limpiar                                                                                      |
| Redacción (4 %)                               | 9           | Todo el texto                                                     | Registro coloquial, errores gramaticales y de acentuación, separadores decimales mezclados                                                                                                                                                           | Comprensible pero irregular                                                             | Revisión de estilo integral                                                                                              |
| Tablas y figuras (3 %)                        | 10          | Tab. 1–6; Fig. 1–3                                                | Tab. 1 sin nombres; Tab. 4 contradictoria; Tab. 6 con precisión desigual; Fig. 1 y 2 inconsistentes; Fig. 3 sin dispersión                                                                                                                           | Tablas legibles, contenido parcialmente inconsistente                                   | Corregir inconsistencias y añadir variabilidad                                                                           |
| Referencias (4 %)                             | 11          | Referencias; auditoría de §9                                      | Sin citas faltantes ni huérfanas, pero hay correspondencias dudosas y faltan fuentes metodológicas                                                                                                                                                   | Bibliografía cerrada, pero con ajustes necesarios                                       | Revisar correspondencia; completar metadatos                                                                             |

No se ajustaron los pesos sugeridos.

### 7. Comparación con trabajos próximos

La tabla se basa únicamente en lo que el manuscrito dice de cada referencia y en sus títulos. No fue verificada externamente.

| Trabajo relacionado                                                     | Problema abordado                                         | Método                                                    | Datos y contexto                   | Limitaciones identificadas                        | Diferencia respecto del manuscrito                                    | Evidencia de novedad                                                   |
| ----------------------------------------------------------------------- | --------------------------------------------------------- | --------------------------------------------------------- | ---------------------------------- | ------------------------------------------------- | --------------------------------------------------------------------- | ---------------------------------------------------------------------- |
| Ebad et al. (2026); Galagedarage Don et al. (2025); Liang et al. (2026) | Panorama de gemelos digitales en minería                  | Revisiones                                                | Minería en general                 | No verificables (solo título/uso)                 | M-11 propone una implementación concreta de proximidad hombre-máquina | Débil: no hay mapeo sistemático de la brecha frente a estas revisiones |
| Cacciuttolo et al. (2025)                                               | Marco conceptual multicapa de gemelo digital subterráneo  | Marco conceptual                                          | Minería subterránea                | No verificables                                   | M-11 añade implementación y clasificación                             | Parcial; sin comparación explícita de capas                            |
| Cacciuttolo et al. (2024)                                               | Red LoRaWAN de sensores para monitoreo subterráneo        | IoT/comunicaciones                                        | Mina subterránea                   | No verificables; citado para propagación de señal | M-11 no evalúa comunicaciones reales                                  | No aplicable                                                           |
| Jin et al. (2026)                                                       | Visualización de riesgo con interoperabilidad 3Dmine-3DEC | Interoperabilidad de datos y visualización                | Procesos mineros                   | No verificables                                   | M-11 usa visualización de proximidad en tiempo cuasi-real simulada    | No comparable de forma directa                                         |
| Cheng y Luo (2026)                                                      | Alerta de seguridad en túneles con BIM e IoT              | Fusión de datos nube-borde-dispositivo (según manuscrito) | Construcción de túneles            | No verificables                                   | Arquitectura similar de capas; dominio distinto                       | Débil: la arquitectura de 4 capas no se contrasta                      |
| Mousavi et al. (2025)                                                   | Monitoreo de riesgo ambiental con fusión IoT-Bayes        | Modelo probabilístico                                     | Minería subterránea y construcción | No verificables                                   | M-11 clasifica riesgo de proximidad, no ambiental                     | No contrastada la ventaja del ML                                       |
| Jiang et al. (2024)                                                     | Estado de mineros con sistema IoT                         | Monitoreo IoT                                             | Minería subterránea                | No verificables                                   | M-11 incluye biometría simulada sin aporte medido                     | Débil                                                                  |
| Yang M. et al. (2022)                                                   | LSTM explicable para colaboración IA-trabajadores         | Aprendizaje profundo explicable                           | No verificable                     | No verificables                                   | M-11 usa XGBoost + TreeSHAP (sin resultados SHAP)                     | No sostenida mientras falten los resultados SHAP                       |

La novedad externa permanece parcialmente sin comprobar.

### 8. Evaluación de forma

| Criterio                         | Nota (0–20) | Evidencia examinada     | Deficiencia detectada                                                                                                                                                      | Justificación                                | Acción recomendada                                                |
| -------------------------------- | ----------- | ----------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | -------------------------------------------- | ----------------------------------------------------------------- |
| Estructura y organización        | 8           | Secciones; anexos       | Meta-texto de proceso; “Análisis del problema” como revisión; resultados con contenido metodológico; pendientes en anexos                                                  | Estructura no apta para envío                | Reordenar en IMRyD y mover protocolos a Métodos                   |
| Redacción académica              | 9           | Introducción; Discusión | Registro coloquial; errores de concordancia y acentuación; decimales mezclados; frases largas con múltiples ideas                                                          | Comprensible, pero con errores frecuentes    | Revisión de estilo; unificar convención numérica                  |
| Tablas y figuras                 | 10          | Tab. 1–6; Fig. 1–3      | Tab. 1 no nombra variables; Tab. 4 contradice el texto; Fig. 1 discrepa del texto; Fig. 2 con escala y etiquetas defectuosas; Fig. 3 sin barras de variabilidad            | Informativas pero con errores                | Corregir; incluir rótulos completos                               |
| Referencias                      | 11          | Lista de 42; citas      | Metadatos incompletos (Hafez; Chen; Yang y Li; Zhu 2026; MINEM sin URL); sin fuentes metodológicas; formatos mezclados                                                     | Cerrada, pero mejorable                      | Normalizar formato; completar metadatos                           |
| Título, resumen y palabras clave | 11          | Portada                 | Título sobredimensiona (“gemelo digital”, “alerta temprana”); resumen largo y denso en cifras; “explicable” no respaldado; palabras clave con IA explicable sin resultados | El resumen es honesto en alcance, pero denso | Título más ajustado; resumen más corto; palabras clave coherentes |

### 9. Auditoría bidireccional de referencias

#### A. Citas presentes en el texto, ausentes de la bibliografía

Todas las citas autor-año del texto tienen entrada en la bibliografía. Se detectan fuentes mencionadas sin entrada:

| Elemento mencionado                                                | Ubicación                        | Observación                                                                                     |
| ------------------------------------------------------------------ | -------------------------------- | ----------------------------------------------------------------------------------------------- |
| OSHA 29 CFR 1926.651                                               | Explicabilidad y auditoría GenAI | Norma citada sin entrada; el propio texto reconoce que corresponde a construcción, no a minería |
| SMOTENC, XGBoost, TreeSHAP, McNemar, Holm, delta de Cliff          | Métodos / Resultados             | Técnicas sin cita a la fuente original                                                          |
| UWB/RFID, CAN J1939, Langflow, Gemini 2.5 Flash, FastAPI, Three.js | Arquitectura                     | Sin cita ni especificación técnica                                                              |
| Dataset UCI AI4I 2020                                              | Datos                            | Se cita el artículo (Matzka, 2020), no el repositorio del dataset                               |

#### B. Referencias no citadas

No se detectaron referencias huérfanas: las 42 entradas se citan al menos una vez en el texto.

#### C. Errores de correspondencia

Los casos siguientes son dudas basadas en el título de cada obra y no se verificaron externamente.

| Cita en el texto                                                      | Afirmación que sustenta                                                          | Problema                                                                                |
| --------------------------------------------------------------------- | -------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------- |
| X. Yang et al. (2024), DEMATEL-ISM                                    | Elección de F2 / ningún algoritmo superior en todas las métricas                 | El título (factores de colaboración hombre-máquina) no respalda una decisión de métrica |
| Yang et al. (2022), BiLSTM explicable                                 | No equiparar importancia explicativa con causalidad                              | Correspondencia no evidente                                                             |
| Yan et al. (2025), riesgo de terreno voxelizado                       | Filtrado de polvo con precisión media ≈ 96,7 %                                   | El título no sugiere filtrado de polvo; no verificable                                  |
| Wu et al. (2026), fatiga en operadores de grúa torre                  | Fatiga compromete distancias seguras en LHD                                      | Transferencia de contexto (construcción → subterráneo) sin salvedad                     |
| Jin et al. (2026), interoperabilidad 3Dmine-3DEC                      | Interacción en tiempo real entre modelos digitales y minas físicas               | El título sugiere interoperabilidad de datos y visualización                            |
| Hafez y Joerger (2024); Vahs et al. (2023)                            | Evolución de modelos de seguridad; futura integración de monitoreo de integridad | Localización de robots y funciones de barrera: aplicabilidad indirecta                  |
| Nevskaya et al. (2025), lógica difusa                                 | Mejora sobre “reglas fijas y difusas”                                            | Es un método difuso; se cita en el mismo bloque que se supone que lo supera             |
| Cacciuttolo et al. (2024), LoRaWAN                                    | Reflejos, Fresnel, línea de vista (relevante a UWB)                              | Tecnología distinta de UWB                                                              |
| Bloques repetidos (Mousavi; Santhoshkumar; Vahs; Yang 2022; Nevskaya) | Dos párrafos de la Introducción                                                  | Misma cita en grupo para afirmaciones distintas                                         |

#### D. Calidad y actualidad bibliográfica

| Aspecto                     | Observación                                                                                                                                                           |
| --------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Actualidad                  | 31 de 42 referencias (74 %) son de 2024–2026; solo 3 anteriores a 2022                                                                                                |
| Concentración editorial     | Aproximadamente 18 de 42 son MDPI (conteo del revisor según nombre de revista)                                                                                        |
| Fuentes de baja visibilidad | Dos IJRASET (Katkar 2024; Renuka 2022), una conferencia 2026 (Santhoshkumar) y una revista de 2026 (Cheng y Luo): calidad no verificable                              |
| Pertinencia                 | Muchas obras sobre carbón, túneles y construcción; escasas sobre LHD/minería metálica y detección de proximidad                                                       |
| Lagunas                     | Sin literatura de sistemas anticolisión comerciales, medidas sustitutas de seguridad (TTC), validación de datos sintéticos ni fuentes metodológicas de ML/estadística |
| Metadatos                   | Faltan volumen/páginas (Hafez; Chen; Yang y Li; Zhu 2026); MINEM sin URL; formato mixto autor-año/IEEE                                                                |
| Norma peruana               | No se indica vigencia ni modificatorias del D.S. 024-2016-EM (no verificado)                                                                                          |

### 10. Tabla consolidada de puntuaciones

| Criterio                               | Peso      | Nota | Contribución ponderada | Observación principal                              | Prioridad |
| -------------------------------------- | --------- | ---- | ---------------------- | -------------------------------------------------- | --------- |
| Novedad y originalidad                 | 15 %      | 8    | 1.20                   | ML iguala a TTC; novedad de integración            | Alta      |
| Relevancia y contribución              | 10 %      | 13   | 1.30                   | Tema relevante; solo prueba de concepto            | Media     |
| Estado del arte                        | 10 %      | 11   | 1.10                   | Falta literatura de proximidad/TTC                 | Media     |
| Rigor metodológico                     | 15 %      | 8    | 1.20                   | Generador y diccionario no documentados            | Alta      |
| Reproducibilidad                       | 10 %      | 8    | 0.80                   | Elementos clave pendientes                         | Alta      |
| Análisis estadístico                   | 15 %      | 10   | 1.50                   | Pruebas mal ajustadas; sin CV reportada            | Alta      |
| Discusión, limitaciones y conclusiones | 10 %      | 14   | 1.40                   | Limitaciones honestas; límite de Bayes incoherente | Media     |
| Estructura                             | 4 %       | 8    | 0.32                   | Meta-texto y pendientes                            | Alta      |
| Redacción                              | 4 %       | 9    | 0.36                   | Registro coloquial y errores                       | Media     |
| Tablas y figuras                       | 3 %       | 10   | 0.30                   | Inconsistencias en Tab. 4, Fig. 1 y 2              | Media     |
| Referencias                            | 4 %       | 11   | 0.44                   | Correspondencias dudosas                           | Media     |
| **Total**                              | **100 %** |      | **9.92**               |                                                    |           |

- **Nota final: 9.9/20.**
- **Nivel: Regular** (bandas de referencia usadas: < 8 Deficiente; 8–11.9 Regular; 12–15.9 Bueno; 16–18.4 Muy bueno; ≥ 18.5 Excelente).
- La decisión editorial no se deriva mecánicamente de la nota.

### 11. Hallazgos críticos y mayores

| ID     | Gravedad | Ubicación / evidencia                                                  | Problema e impacto                                                                                                            | Acción correctiva                                                                    | Prioridad  |
| ------ | -------- | ---------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------ | ---------- |
| FON-01 | Crítica  | Datos; Amenazas; Anexo B: “82.1 % de la varianza… cinemático-espacial” | Etiqueta sintética circular: el ML no supera a TTC (0.907 frente a 0.910); métricas no informan desempeño real                | Verdad de terreno independiente o análisis de etiquetas desacopladas completo con IC | Alta       |
| FON-02 | Crítica  | Tab. 1; Anexo A: “no se adjuntó”; “16 predictores”                     | Dataset, fusión AI4I-simulación y predictores no identificados; posible variable post-evento (`failure_flag`, TWF…)           | Publicar diccionario y generador; auditar fuga                                       | Alta       |
| FON-03 | Mayor    | Desarrollo del modelo: partición estratificada 80/20                   | Unidad de observación y dependencia temporal (5 Hz) sin tratar; posible fuga entre entrenamiento y holdout                    | Partición agrupada por episodio/trabajador/turno                                     | Alta       |
| FON-04 | Mayor    | Amenazas: “F2 = 0.900… resultados 0.907–0.910 sobrepasan”              | Límite de Bayes incoherente; Anexo B sin protocolo ni IC                                                                      | Derivar formalmente o eliminar; documentar Anexo B                                   | Alta       |
| FON-05 | Mayor    | Tab. 4; texto: “no implica equivalencia”                               | McNemar no mide F2; delta de Cliff no definido; “equivalentes” sin TOST; TTC calibrado ausente                                | Bootstrap pareado de ΔF2 con todos los comparadores; TOST con margen                 | Alta       |
| FON-06 | Mayor    | Tab. 2: “TTC calibrado (<11 s)”; “no se reproducen… hiperparámetros”   | Calibración de TTC y tuning no descritos; “XGBoost (propuesto)” sin justificación de selección                                | Describir calibración en datos de desarrollo; tabla de hiperparámetros               | Alta       |
| FON-07 | Mayor    | Resumen: “validación cruzada de cinco pliegues”                        | Sin resultados de CV; una sola partición y semilla                                                                            | Reportar CV y repetir con semillas                                                   | Alta       |
| FON-08 | Mayor    | Tab. 6 (E: p = 0.02; G: AUC = 0.489)                                   | Ablación sin procedimiento, IC ni método de p; conteos inconsistentes; multimodalidad no sostenida                            | Describir procedimiento; IC; corregir conteos; reformular “multimodal”               | Alta       |
| FON-09 | Mayor    | Introducción vs “no se dispone… valores SHAP”                          | Explicabilidad anunciada y no demostrada                                                                                      | Calcular SHAP en el pipeline final o retirar “explicable”                            | Alta       |
| FON-10 | Mayor    | Explicabilidad y auditoría GenAI                                       | Auditoría de Gemini sin resultados; LLM en dominio de seguridad crítica; norma OSHA inadecuada                                | Reportar resultados o desplazar a trabajo futuro                                     | Media-alta |
| FON-11 | Mayor    | Tab. 5; Fig. 3; P3                                                     | E2E sin definición; loopback; sin repeticiones, P99 ni IC; 60 FPS no medidos; “tiempo real” sin garantía                      | Definir E2E; repeticiones con IC; separar render de backend                          | Alta       |
| FON-12 | Mayor    | Título; objetivo general                                               | “Gemelo digital”, “alerta temprana” y “reducir el riesgo” sin sustento                                                        | Reetiquetar como banco de pruebas de simulación                                      | Alta       |
| FON-13 | Mayor    | Tab. 2; Introducción (“F1”)                                            | Sin métricas de alerta temprana (anticipación, falsas alarmas por hora), sin matriz de confusión ni clase MEDIO; F1 anunciado | Añadir métricas operativas y de 3 clases                                             | Alta       |
| FON-14 | Moderada | Datos: “benchmarks reales”; AI4I                                       | Dataset descrito como real; relación AI4I-colisión no justificada                                                             | Confirmar naturaleza del dataset; justificar uso                                     | Media      |
| FON-15 | Moderada | Introducción                                                           | Brecha no contrastada con sistemas de proximidad existentes                                                                   | Revisión focalizada y tabla comparativa                                              | Media      |
| FON-16 | Moderada | Sesgo, privacidad y adopción                                           | Seudonimización declarada sin evidencia                                                                                       | Describir mecanismo o presentar como requisito                                       | Media      |
| FOR-01 | Mayor    | Anexo A: “Pendiente antes del envío editorial”; “dossier”; “guía”      | Texto de proceso y pendientes dentro del manuscrito                                                                           | Depurar y completar                                                                  | Alta       |
| FOR-02 | Mayor    | Fig. 1, 2                                                              | Inconsistencias con el texto; escala de Fig. 2                                                                                | Rehacer figuras                                                                      | Media      |
| FOR-03 | Moderada | Referencias                                                            | Correspondencias dudosas; metadatos incompletos; falta de fuentes metodológicas                                               | Revisar y completar                                                                  | Media      |
| FOR-04 | Moderada | Todo el texto                                                          | Registro coloquial; errores; decimales mezclados                                                                              | Revisión de estilo                                                                   | Media      |
| FOR-05 | Moderada | Disponibilidad de datos y código                                       | Sin commit/DOI; datos no archivados; enlace duplicado                                                                         | Versión archivada con DOI                                                            | Alta       |
| FOR-06 | Menor    | Portada; encabezado                                                    | Idioma y normas de la revista no verificados; correos pendientes; “DOI por asignar”                                           | Revisar normas y completar datos                                                     | Baja       |

### 12. Plan detallado de correcciones

#### Correcciones de fondo

**FON-01 (circularidad).**

- *Ubicación:* Datos; Amenazas a la validez; Anexo B.
- *Problema:* la etiqueta se genera con un score dominado por distancia, TTC y zona restringida.
- *Solución:*&#x20;
  1. Describir el score generador completo (fórmula, pesos, umbrales BAJO/MEDIO/ALTO, σ = 3.8 con unidades).
  2. Construir etiquetas alternativas independientes del TTC (por ejemplo, derivadas de eventos simulados de contacto o cuasi-colisión con simulación física).
  3. Reevaluar todos los modelos y TTC con IC.
  4. Mover Anexo B al cuerpo con protocolo y semillas.
- *Ejemplo:* “Con etiquetas desacopladas (n = …), XGBoost obtuvo F2 = … [IC 95 %] y TTC F2 = … [IC 95 %]; la diferencia pareada fue …”.

**FON-02 (dataset y diccionario).**

- *Ubicación:* Tab. 1; Anexo A.
- *Problema:* 16 predictores y 37 columnas no identificados; posibles variables post-evento.
- *Solución:*&#x20;
  1. Publicar tabla con nombre, tipo, rol, transformación y fuente de cada columna.
  2. Declarar explícitamente qué variables de AI4I están en el vector de entrada.
  3. Excluir `failure_flag` y los modos TWF, HDF, PWF y OSF si fueran predictores.
  4. Confirmar la naturaleza (real o sintética) del AI4I y justificar su vínculo con el escenario de LHD.

**FON-03 (partición y dependencia temporal).**

- *Ubicación:* Desarrollo del modelo.
- *Problema:* registros de 5 Hz de episodios continuos pueden aparecer en entrenamiento y holdout.
- *Solución:*&#x20;
  1. Definir qué es un “registro” (frame, episodio, trabajador-máquina).
  2. Usar GroupKFold/partición por episodio y trabajador.
  3. Repetir con varias semillas y reportar media y dispersión.

**FON-04 (límite de Bayes y Anexo B).**

- *Ubicación:* Amenazas a la validez; Anexo B.
- *Solución:*&#x20;
  1. Eliminar la cifra de 0.900 o derivarla de forma reproducible a partir del proceso generador conocido.
  2. Si se mantiene, explicar por qué resultados mayores no la invalidan.
  3. Añadir IC y conjunto de prueba al contraste desacoplado.

**FON-05 (inferencia).**

- *Ubicación:* Tab. 4; texto de Resultados.
- *Solución:*&#x20;
  1. Reemplazar McNemar por bootstrap pareado de ΔF2 (y ΔAUC-PR) para todos los comparadores, incluido TTC calibrado.
  2. Definir sobre qué se calcula el delta de Cliff o eliminarlo.
  3. Para sostener “equivalencia”, fijar margen a priori y aplicar TOST.
  4. Cambiar “equivalentes” por “sin diferencia detectada”.
- *Ejemplo:* “No se detectó diferencia entre XGBoost y RF (ΔF2 = −0.003; IC 95 % [−0.010, +0.004])”.

**FON-06 (calibración y selección del modelo).**

- *Solución:*&#x20;
  1. Describir cómo se calibró el umbral de 11 s del TTC (solo con datos de desarrollo).
  2. Añadir tabla de hiperparámetros y método de búsqueda (anidado o no).
  3. Justificar “XGBoost (propuesto)” por criterios externos al holdout (latencia, SHAP nativo), no por F2.
  4. Reportar también TTC como score continuo (AUC-ROC y AUC-PR) para comparación justa.

**FON-07 (CV y repetición).**

- *Solución:* reportar media ± DE de la CV de 5 pliegues por modelo; repetir con semillas distintas; informar si SMOTENC altera conclusiones (Tab. 3 incluye solo 2 modelos).

**FON-08 (ablación).**

- *Ubicación:* Tab. 6.
- *Solución:*&#x20;
  1. Describir si se reentrenó y se reoptimizó el umbral en cada configuración.
  2. Añadir IC de ΔF2 con bootstrap pareado y la prueba que da p = 0.02 y p < 0.001, con corrección de multiplicidad.
  3. Corregir conteo de variables (fila E).
  4. Presentar matriz de correlación o VIF para sustentar la colinealidad.
  5. Reformular: con AUC = 0.489 sin el bloque espacial/cinemático, el modelo es esencialmente unimodal en este generador.

**FON-09 (SHAP).** Calcular TreeSHAP sobre el modelo final con valores y gráficos, discutir con cautela la causalidad y la colinealidad, o retirar “explicable” del título, resumen y palabras clave.

**FON-10 (GenAI).** Presentar resultados del banco de 100 escenarios con IC y kappa de Cohen, o mover el módulo a trabajo futuro. Aclarar que no se evalúa seguridad real y retirar OSHA 29 CFR 1926.651 como referencia normativa o justificar su inclusión.

**FON-11 (latencia).**

- *Solución:*&#x20;
  1. Definir los puntos de inicio y fin del E2E y si incluye inferencia, serialización y render.
  2. Reportar duración, repeticiones, calentamiento, P99, máximo e IC.
  3. Reemplazar “tiempo real” por “tiempo cuasi-real simulado” o justificar con análisis de jitter.
  4. Medir FPS en la misma sesión que la carga.
  5. Documentar la GPU.

**FON-12 (denominación y alcance).**

- *Ejemplo de título:* “M-11: banco de pruebas de alerta de colisión basado en simulación y visualización 3D para minería subterránea”.
- *Ejemplo de objetivo:* “Diseñar y evaluar computacionalmente un prototipo de banco de pruebas… sin evaluar eficacia de seguridad”.

**FON-13 (métricas operativas).**

- *Solución:*&#x20;
  1. Añadir matriz de confusión de tres clases y F1/macro-F1 (o retirar F1 de la Introducción).
  2. Medir anticipación (segundos antes del evento simulado) y falsas alarmas por unidad de tiempo.
  3. Discutir que una precisión de ≈ 77 % implica alrededor de una de cada cuatro alertas falsas.

**FON-14 a FON-16.**

- *FON-14:* describir el vínculo físico entre el dataset AI4I y el escenario LHD.
- *FON-15:* añadir tabla comparativa de sistemas de proximidad y anticolisión y de estudios de TTC como medida sustituta de seguridad.
- *FON-16:* describir cómo se implementa la seudonimización, o plantearla como requisito.

#### Correcciones de forma

**FOR-01 (meta-texto y pendientes).**

- *Ubicación:* Datos, Desarrollo, Explicabilidad, Anexo A.
- *Solución:*&#x20;
  1. Eliminar toda referencia a “guía”, “dossier” y “versiones previas”.
  2. Completar el diccionario en lugar de dejar el aviso.
  3. Redactar los límites como limitaciones del estudio.
- *Ejemplo:* en lugar de “La guía no proporciona el registro completo de hiperparámetros”, incluir la tabla de hiperparámetros.

**FOR-02 (figuras).**

- *Solución:*&#x20;
  1. Fig. 1: alinear capas con el texto (qué hace el borde, dónde está AI4I).
  2. Fig. 2: usar captura real del visor o rotular como esquema, con la escala de la galería simulada y sin etiquetas superpuestas.
  3. Fig. 3: añadir bandas de dispersión, número de repeticiones y señalar el umbral de 200 ms.

**FOR-03 (referencias).**

- *Solución:*&#x20;
  1. Revisar las correspondencias de §9C; citar la fuente que respalda cada afirmación.
  2. Completar volumen, páginas y URL (incluida la de MINEM).
  3. Añadir fuentes de SMOTENC, XGBoost, TreeSHAP, pruebas estadísticas y el repositorio del dataset.
  4. Unificar el formato.

**FOR-04 (redacción).**

- *Solución:* eliminar coloquialismos (“o sea”, “así que”, “salen de”), corregir concordancias y acentos, unificar punto/coma decimal.
- *Ejemplo:* “En M-11, la arquitectura de cuatro capas gestiona este proceso mediante…”.

**FOR-05 (disponibilidad).** Archivar el código y los datos con DOI y commit identificable (por ejemplo, un repositorio de archivo permanente) e incluir predicciones del holdout, scripts de ablación y de latencia; eliminar el enlace duplicado.

**FOR-06 (portada y normas).** Completar correos y datos de contacto, confirmar el idioma y los requisitos de la revista, y retirar el DOI “por asignar” y el texto de plantilla.

### 13. Evaluación de reproducibilidad

**Clasificación: Baja-moderada.** El protocolo de evaluación, la semilla y las versiones de software están declarados, pero faltan el generador de etiquetas, el diccionario, los hiperparámetros y las predicciones. El repositorio existe según el texto, pero su contenido no pudo verificarse.

| Aspecto            | Estado                   | Evidencia                                                   | Acción requerida                                                      |
| ------------------ | ------------------------ | ----------------------------------------------------------- | --------------------------------------------------------------------- |
| Dataset            | Insuficiente             | Tab. 1; Anexo A: diccionario “no se adjuntó”                | Publicar dataset y diccionario                                        |
| Código             | Parcial / no verificable | URL GitHub; “presencia pública íntegra no pudo verificarse” | Versión archivada con commit                                          |
| Licencia           | Declarada (MIT)          | “licencia indicada por el proyecto: MIT”                    | Confirmar licencias de datos (AI4I)                                   |
| Semillas           | Parcial                  | Semilla 42 en preprocesamiento y partición                  | Documentar semillas de modelos y SMOTENC; repetir                     |
| Versiones          | Parcial                  | Python 3.10.11, XGBoost 3.2.0, scikit-learn 1.7.2           | Añadir imbalanced-learn, SHAP, Node y Three.js                        |
| Hiperparámetros    | Ausente                  | “no se reproducen aquí las configuraciones”                 | Tabla completa y método de búsqueda                                   |
| Artefactos         | Ausente / no verificable | Predicciones y scripts “deben vincularse”                   | Archivar modelos, predicciones y scripts                              |
| Tablas y figuras   | Parcial                  | Tab. 1–6; Fig. 3                                            | Script que regenere cada tabla y figura                               |
| Validación externa | Ausente                  | Solo datos híbridos                                         | Datos de campo o simulación independiente                             |
| Declaración de IA  | Presente                 | Sección “Uso de IA”                                         | Especificar herramientas y alcance de uso en redacción y en el módulo |

### 14. Decisión editorial recomendada

**Major revisions.**

La contribución es potencialmente valiosa como banco de pruebas computacional y el manuscrito modera correctamente sus conclusiones, pero la evidencia no sostiene el valor del componente de aprendizaje automático, la explicabilidad ni la multimodalidad. Además, el texto es una versión incompleta.

- **Subsanables con cambios de redacción:** título y denominación (“gemelo digital”, “tiempo real”, “multimodal”); eliminación de meta-texto y pendientes; corrección de Tab. 4 (“equivalentes”), conteos de variables, estilo y referencias.
- **Requieren análisis adicionales o nuevos experimentos:** documentación y auditoría del generador y del diccionario; partición agrupada; resultados de CV y repeticiones; inferencia rehecha con TTC calibrado incluido; ablación con IC; SHAP; auditoría de Gemini; benchmark de latencia ampliado; métricas de alerta temprana.
- **Afectan la validez central:** la circularidad de la etiqueta (FON-01) y la opacidad del dataset (FON-02). Si no se resuelven con un análisis desacoplado documentado, el aporte analítico del manuscrito queda sin sustento y procedería **Reject and resubmit**.

### 15. Conclusión final

M-11 es una prueba de concepto útil como arquitectura y banco de pruebas, con un protocolo de evaluación cuidadoso en su diseño y honesto en sus límites. Su potencial depende de convertir la evaluación en algo informativo. Para ello se necesitan como mínimo etiquetas con verdad de terreno independiente (o un análisis desacoplado completo), un dataset documentado, resultados reales de SHAP y de la auditoría de Gemini, una inferencia estadística corregida, un benchmark de latencia más robusto, y un manuscrito depurado de lenguaje de proceso. El título y la denominación deben ajustarse a lo realmente demostrado.

### 16. Declaración de alcance y limitaciones de la revisión

Se inspeccionaron el texto completo, las seis tablas, las tres figuras de contenido, los anexos y las 42 referencias del archivo `.docx` proporcionado. No se verificaron el repositorio, el código, los datos, el diccionario, los DOI, las URL ni la indexación, y no se recalcularon resultados. Las afirmaciones sobre la naturaleza del dataset AI4I y sobre la correspondencia de referencias se basan en títulos y descripciones del propio manuscrito, y deben confirmarse. La novedad externa permanece parcialmente sin comprobar. Las conclusiones sobre reproducibilidad y validez del dataset están limitadas por la ausencia del diccionario, del generador de etiquetas y de los hiperparámetros.