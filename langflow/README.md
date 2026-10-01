# 🏔️ M-11: Integración de Langflow con Modelos Predictivos de Riesgo Minero

Esta carpeta contiene la integración de **Langflow** con los modelos predictivos de Machine Learning (XGBoost / Voting Classifier) del sistema **M-11 Digital Twin**.

---

## 📐 Arquitectura del Flujo

```
[ Telemetría de Sensores ]
  (Distancia 3D, TTC, CO, Fatiga, Zona)
              │
              ▼
┌──────────────────────────────────────────────┐
│  MiningRiskPredictor (Custom Component)      │
│  - Carga: best_risk_model.joblib             │
│  - Inferencia: Riesgo ALTO / MEDIO / BAJO    │
│  - Detección de factores críticos detonantes │
└──────────────────────┬───────────────────────┘
                       │ (Diagnóstico + Telemetría)
                       ▼
┌──────────────────────────────────────────────┐
│  Prompt de Protocolo de Emergencia Minero    │
│  - Reglas D.S. 024-2016-EM / OSHA            │
└──────────────────────┬───────────────────────┘
                       │
                       ▼
┌──────────────────────────────────────────────┐
│  Google Gemini AI (LLM)                      │
│  - Generación de maniobras de maquinaria     │
│  - Plan de evacuación y alertas operacionales│
└──────────────────────┬───────────────────────┘
                       │
                       ▼
[ Protocolo de Emergencia Generado en Chat / API ]
```

---

## 📁 Contenido del Directorio

| Archivo / Carpeta | Descripción |
| :--- | :--- |
| `components/mining_risk_predictor.py` | **Componente Personalizado de Langflow** que envuelve el modelo `.joblib`. Expone los parámetros de los sensores (distancia, velocidad, gases, fatiga) y ejecuta la predicción. |
| `mining_risk_prediction_flow.json` | **Flujo completo listo para importar en Langflow**. Conecta el predictor con el prompt y Google Gemini. |
| `test_predictor_component.py` | Script de prueba rápida para validar la inferencia del componente sin abrir la interfaz web. |
| `run_langflow.bat` | Script de inicio automático de Langflow para Windows. |

---

## 🚀 Cómo Usarlo

### Paso 1: Probar el componente directamente en consola
Para verificar que el componente se conecta correctamente a tu modelo de machine learning:
```bash
python langflow/test_predictor_component.py
```

### Paso 2: Iniciar Langflow
Puedes hacer doble clic en `run_langflow.bat` o ejecutar en terminal:
```bash
pip install langflow
python -m langflow run
```
Abre en tu navegador: [http://localhost:7860](http://localhost:7860)

### Paso 3: Cargar el Componente en Langflow (Forma Recomendada)
Dado que Langflow gestiona esquemas de interfaz dinámicos, la forma más rápida y sin errores es usar un **Custom Component**:

1. En la pantalla inicial de Langflow, haz clic en **"New Flow"** (o **"Nuevo Flujo"**) y elige **"Blank Flow"**.
2. En el panel de componentes a la izquierda, arrastra al lienzo un **"Custom Component"** (bajo la categoría *Helpers* o *Custom*).
3. En la tarjeta del nodo que apareció en el lienzo, haz clic en el icono de código **`</>`** (*Edit Code*).
4. Borra el código de plantilla y pega todo el contenido del archivo [`mining_risk_predictor.py`](file:///c:/Users/villa/Downloads/Mining/digital-twins-mines/langflow/components/mining_risk_predictor.py).
5. Haz clic en **"Check & Save"**. 
   - *¡Langflow generará automáticamente todos los controles interactivos (distancia 3D, TTC, CO, fatiga) y los puertos de salida!*

### Paso 4: Conectar con Google Gemini (Opcional para flujo completo)
1. Desde la barra izquierda, agrega:
   - Un nodo **Prompt** (conecta la salida `diagnostic_message` del predictor a la variable `{telemetria}`).
   - Un nodo **Google Generative AI** (agrega tu API Key de Gemini y conecta el prompt).
   - Un nodo **Chat Output**.
2. Haz clic en **Playground** (esquina superior derecha) para probarlo en tiempo real modificando distancias o niveles de gas.
