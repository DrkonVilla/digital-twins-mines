 # M-11: Propuesta Técnica — Sistema de Alerta Temprana de Riesgo Humano
## Gemelo Digital de Interacción Hombre-Máquina en Frentes de Extracción Subterránea

---

## 1. Visión General del Sistema

M-11 es un sistema inteligente de monitoreo y alerta temprana diseñado para entornos de extracción subterránea. Su propósito es detectar, clasificar y anticipar situaciones de riesgo en la interacción entre trabajadores y maquinaria pesada, representando la información en tiempo real mediante un Gemelo Digital 3D interactivo.

---

## 2. Arquitectura del Sistema

### 2.1 Diagrama de Arquitectura (N-Capas)

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           CAPA DE PRESENTACIÓN                               │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  ┌─────────────────┐  │
│  │   Dashboard  │  │ Gemelo 3D    │  │  Reportes    │  │ Panel Admin     │  │
│  │   (React)    │  │ (Three.js)   │  │ (PDF/Excel)  │  │ (Usuarios/Roles)│  │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘  └────────┬────────┘  │
│         │                 │                 │                   │         │
│         └─────────────────┴─────────────────┴───────────────────┘         │
│                              WebSocket / HTTP                               │
├─────────────────────────────────────────────────────────────────────────────┤
│                           CAPA DE APLICACIÓN                                 │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                      API REST (FastAPI)                              │   │
│  │  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐  │   │
│  │  │Autentic. │ │ Predicc. │ │ Alertas  │ │ Reportes │ │ Gemini   │  │   │
│  │  │  (JWT)   │ │  (ML)    │ │ (WS)     │ │ (Gen)    │ │  (IA)    │  │   │
│  │  └──────────┘ └──────────┘ └──────────┘ └──────────┘ └──────────┘  │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
├─────────────────────────────────────────────────────────────────────────────┤
│                           CAPA DE SERVICIOS                                 │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐    │
│  │  ML Service  │  │ Alert Engine │  │  Report Gen  │  │  Gemini AI   │    │
│  │ (Scikit/XGB) │  │ (WebSocket)  │  │ (Doc/Excel)  │  │   Service    │    │
│  └──────────────┘  └──────────────┘  └──────────────┘  └──────────────┘    │
├─────────────────────────────────────────────────────────────────────────────┤
│                           CAPA DE DATOS                                     │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐    │
│  │  PostgreSQL  │  │   Redis      │  │  File Store  │  │  ML Models   │    │
│  │  (Relacional)│  │  (Caché/WS)  │  │  (Reportes)  │  │  (Artifacts) │    │
│  └──────────────┘  └──────────────┘  └──────────────┘  └──────────────┘    │
├─────────────────────────────────────────────────────────────────────────────┤
│                           CAPA DE INGESTA                                   │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐                    │
│  │ Sensores IoT │  │  Posicionam. │  │   Manual     │                    │
│  │   (MQTT)     │  │   (UWB/GPS)  │  │   (Form)     │                    │
│  └──────────────┘  └──────────────┘  └──────────────┘                    │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 2.2 Patrones Arquitectónicos

| Patrón | Aplicación |
|--------|-----------|
| **Microservicios ligeros** | Separación ML Service, Alert Engine, Report Service |
| **Event-Driven** | WebSocket para alertas en tiempo real |
| **Repository Pattern** | Abstracción de acceso a datos |
| **CQRS (parcial)** | Lecturas optimizadas para dashboard, escrituras para eventos |
| **Circuit Breaker** | Protección contra fallos de Gemini API |

---

## 3. Módulos del Sistema

### 3.1 Módulo de Autenticación y Autorización (M-AUTH)
- JWT con refresh tokens
- Roles: `ADMIN`, `SUPERVISOR`, `OPERADOR`, `AUDITOR`
- Control de acceso basado en roles (RBAC)
- Perfiles de usuario con permisos granulares

### 3.2 Módulo de Monitoreo en Tiempo Real (M-MON)
- Recepción de datos de posicionamiento (simulados en prototipo)
- Cálculo de métricas en tiempo real (distancia, TTC, velocidad relativa)
- Stream de datos hacia el Gemelo Digital vía WebSocket

### 3.3 Módulo de Predicción de Riesgo (M-ML)
- Preprocesamiento de features
- Inferencia con modelo entrenado
- Clasificación en BAJO / MEDIO / ALTO
- Explicabilidad básica (feature importance por predicción)

### 3.4 Módulo de Alertas (M-ALERT)
- Generación de alertas según nivel de riesgo
- Notificaciones WebSocket push
- Escalamiento automático (ALTO → inmediato, MEDIO → 5s, BAJO → log)
- Acknowledge de alertas por operadores

### 3.5 Módulo de Gemelo Digital 3D (M-DT)
- Representación 3D del frente de extracción
- Avatares de trabajadores y maquinaria
- Visualización de zonas restringidas
- Animación de trayectorias y estados de riesgo
- Colores por nivel de riesgo (Verde/Amarillo/Rojo)

### 3.6 Módulo de Historial y Eventos (M-HIST)
- Registro persistente de todas las interacciones
- Búsqueda y filtrado por fecha, trabajador, máquina, nivel de riesgo
- Timeline de eventos

### 3.7 Módulo de Reportes (M-REP)
- Generación de reportes en PDF, Word y Excel
- Reportes de incidentes, tendencias de riesgo, cumplimiento
- Templates configurables

### 3.8 Módulo de IA Generativa (M-GEMINI)
- Análisis de texto de alertas y eventos
- Generación de recomendaciones de seguridad
- Resumen ejecutivo de reportes
- Chatbot de consulta sobre normativa de seguridad minera

---

## 4. Flujo de Datos

### 4.1 Flujo Principal (Tiempo Real)

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   Fuente    │────▶│  FastAPI    │────▶│  ML Service │────▶│   Alert     │
│  de Datos   │     │  Endpoint   │     │  (Predict)  │     │   Engine    │
│  (Simulada) │     │  /predict   │     │             │     │             │
└─────────────┘     └─────────────┘     └──────┬──────┘     └──────┬──────┘
                                               │                     │
                                               ▼                     ▼
                                        ┌─────────────┐     ┌─────────────┐
                                        │ PostgreSQL  │     │  WebSocket  │
                                        │  (Eventos)  │     │  (Clientes) │
                                        └─────────────┘     └──────┬──────┘
                                                                   │
                                                                   ▼
                                                            ┌─────────────┐
                                                            │  Gemelo 3D  │
                                                            │  (React)    │
                                                            └─────────────┘
```

### 4.2 Flujo de Entrenamiento (Offline)

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│  Generación     │────▶│  Preprocesam.   │────▶│  Entrenamiento  │
│  Dataset Synth  │     │  (Feature Eng.) │     │  (RF/XGB/SVM)   │
│  (Python)       │     │                 │     │                 │
└─────────────────┘     └─────────────────┘     └────────┬────────┘
                                                         │
                              ┌────────────────────────┼────────────────────────┐
                              ▼                        ▼                        ▼
                        ┌─────────┐              ┌─────────┐              ┌─────────┐
                        │ Random  │              │ XGBoost │              │   SVM   │
                        │ Forest  │              │         │              │         │
                        └────┬────┘              └────┬────┘              └────┬────┘
                             │                        │                        │
                             └────────────────────────┼────────────────────────┘
                                                      ▼
                                               ┌─────────────┐
                                               │  Evaluación │
                                               │ (Metrics)   │
                                               └──────┬──────┘
                                                      ▼
                                               ┌─────────────┐
                                               │ Selección   │
                                               │   Mejor     │
                                               │   Modelo    │
                                               └──────┬──────┘
                                                      ▼
                                               ┌─────────────┐
                                               │  Serializ.  │
                                               │  (joblib)   │
                                               └─────────────┘
```

---

## 5. Diseño del Dataset Sintético

> **ADVERTENCIA IMPORTANTE**: Todos los datos generados para este prototipo son **completamente sintéticos y simulados**. No representan datos operacionales reales de ninguna mina, trabajador o equipo. Su propósito exclusivo es demostrar la viabilidad técnica del sistema M-11. En un despliegue productivo, estos datos deben ser reemplazados por datos reales capturados por sistemas de posicionamiento UWB/RFID, sensores IoT y registros operacionales validados.

### 5.1 Variables de Entrada (Features)

| # | Variable | Tipo | Descripción | Rango / Unidad |
|---|----------|------|-------------|----------------|
| 1 | `worker_x` | float | Posición X del trabajador | 0 - 500 m |
| 2 | `worker_y` | float | Posición Y del trabajador | 0 - 300 m |
| 3 | `worker_z` | float | Posición Z del trabajador (profundidad) | -50 - -800 m |
| 4 | `machine_x` | float | Posición X de la maquinaria | 0 - 500 m |
| 5 | `machine_y` | float | Posición Y de la maquinaria | 0 - 300 m |
| 6 | `machine_z` | float | Posición Z de la maquinaria | -50 - -800 m |
| 7 | `distance_3d` | float | Distancia euclidiana 3D | 0 - 500 m |
| 8 | `worker_speed` | float | Velocidad del trabajador | 0 - 2.5 m/s |
| 9 | `machine_speed` | float | Velocidad de la máquina | 0 - 15 m/s |
| 10 | `relative_speed` | float | Velocidad relativa (magnitud) | 0 - 17.5 m/s |
| 11 | `direction_worker` | int | Dirección del trabajador (8 cuadrantes) | 0 - 7 |
| 12 | `direction_machine` | int | Dirección de la máquina (8 cuadrantes) | 0 - 7 |
| 13 | `ttc` | float | Time To Collision estimado | 0 - 300 s |
| 14 | `in_restricted_zone` | int | Trabajador en zona restringida | 0 / 1 |
| 15 | `machine_status` | int | Estado de la máquina | 0=Detenida, 1=Operando, 2=Reversa, 3=Transporte |

### 5.2 Variable Objetivo (Target)

| Variable | Clases | Descripción |
|----------|--------|-------------|
| `risk_level` | `0: BAJO`, `1: MEDIO`, `2: ALTO` | Nivel de riesgo de la interacción |

### 5.3 Criterios de Clasificación del Target

La etiqueta `risk_level` se asigna mediante reglas expertas basadas en literatura de seguridad minera:

| Condición | Riesgo |
|-----------|--------|
| `distance_3d > 30m` AND `ttc > 60s` AND `in_restricted_zone = 0` | **BAJO (0)** |
| `distance_3d <= 30m` AND `distance_3d > 10m` AND `ttc > 15s` | **MEDIO (1)** |
| `distance_3d <= 10m` OR `ttc <= 15s` OR `in_restricted_zone = 1` AND `machine_speed > 0` | **ALTO (2)** |
| `distance_3d <= 5m` OR `ttc <= 5s` | **ALTO (2)** — crítico |

---

## 6. Estrategia de Generación de Datos Sintéticos

### 6.1 Metodología

Se utilizará una combinación de:
1. **Simulación física**: Movimiento browniano modificado para trabajadores, trayectorias lineales para maquinaria
2. **Reglas expertas**: Para garantizar distribuciones realistas
3. **Perturbación gaussiana**: Para introducir ruido realista

### 6.2 Parámetros de Simulación

```python
# Pseudocódigo de generación
N_SAMPLES = 50_000  # Registros sintéticos
N_WORKERS = 50      # Trabajadores simulados
N_MACHINES = 15     # Máquinas simuladas
TIME_STEPS = 100    # Pasos temporales por interacción

# Distribuciones
worker_speed ~ Normal(μ=0.8, σ=0.3)  # m/s (caminata)
machine_speed ~ Mixture(
    Detenida: 30%,
    Operando: Normal(μ=3.0, σ=1.0),
    Reversa: Normal(μ=1.5, σ=0.5),
    Transporte: Normal(μ=8.0, σ=2.0)
)

# Zonas restringidas (polígonos 3D simulados)
restricted_zones = [
    {"name": "Zona Carguío", "bounds": [(x1,y1,z1), ...]},
    {"name": "Zona Perforación", "bounds": [...]},
]
```

### 6.3 Balance de Clases

Se aplicará **SMOTE** (Synthetic Minority Over-sampling Technique) para balancear la clase ALTO, garantizando que el modelo no esté sesgado hacia BAJO. Distribución objetivo:
- BAJO: 40%
- MEDIO: 35%
- ALTO: 25%

---

## 7. Entrenamiento del Modelo ML

### 7.1 Preprocesamiento

```python
Pipeline:
1. Imputación de nulos (SimpleImputer - mediana)
2. Escalado de features numéricos (StandardScaler)
3. Codificación de categóricas (OneHotEncoder para direction_, machine_status)
4. Selección de features (SelectKBest - f_classif, k=12)
```

### 7.2 Algoritmos a Evaluar

| Algoritmo | Justificación |
|-----------|---------------|
| **Random Forest** | Buen baseline, maneja no-linealidades, robusto a outliers, interpretable |
| **XGBoost** | Estado del arte para clasificación tabular, regularización integrada, manejo de desbalance |
| **SVM (RBF)** | Buen desempeño en espacios de alta dimensionalidad, robusto con pocos datos |

### 7.3 Hiperparámetros (Grid Search)

```python
# Random Forest
{
    'n_estimators': [100, 200, 500],
    'max_depth': [10, 20, None],
    'min_samples_split': [2, 5, 10],
    'class_weight': ['balanced', 'balanced_subsample']
}

# XGBoost
{
    'n_estimators': [100, 200, 300],
    'max_depth': [3, 6, 9],
    'learning_rate': [0.01, 0.1, 0.3],
    'scale_pos_weight': ['balanced'],
    'subsample': [0.8, 1.0]
}

# SVM
{
    'C': [0.1, 1, 10, 100],
    'gamma': ['scale', 'auto', 0.001, 0.01],
    'kernel': ['rbf'],
    'class_weight': ['balanced']
}
```

### 7.4 Estrategia de Validación

- **Train/Test Split**: 80/20 estratificado
- **Cross-Validation**: Stratified K-Fold (k=5)
- **Métrica de optimización**: `recall_macro` con énfasis en recall de clase ALTO

---

## 8. Evaluación del Modelo

### 8.1 Métricas Clave

| Métrica | Objetivo | Justificación |
|---------|----------|---------------|
| **Accuracy** | > 85% | Desempeño general |
| **Precision (ALTO)** | > 80% | Minimizar falsos positivos innecesarios |
| **Recall (ALTO)** | > 90% | **CRÍTICO**: No perder ninguna situación de alto riesgo |
| **F1-Score (ALTO)** | > 85% | Balance precisión-recall |
| **Matriz de Confusión** | Visual | Identificar patrones de error |

### 8.2 Análisis de Recall de Clase ALTO

Dado que una falta de detección de riesgo ALTO puede resultar en accidentes graves:
- Se priorizará el **recall de la clase ALTO** sobre la precisión
- Se aceptará un mayor número de falsos positivos (alertas innecesarias) para no perder verdaderos positivos
- Se implementará un **threshold tuning** post-entrenamiento para maximizar recall de ALTO

### 8.3 Comparativa de Modelos

Se generará una tabla comparativa y gráficos de:
- Curvas ROC (One-vs-Rest)
- Curvas Precision-Recall por clase
- Feature Importance (para modelos basados en árboles)
- SHAP values (para XGBoost)

---

## 9. API REST (FastAPI)

### 9.1 Endpoints Principales

| Método | Endpoint | Descripción | Auth |
|--------|----------|-------------|------|
| POST | `/api/v1/auth/login` | Login JWT | No |
| POST | `/api/v1/auth/refresh` | Refresh token | Sí |
| POST | `/api/v1/auth/logout` | Logout | Sí |
| GET | `/api/v1/users/me` | Perfil actual | Sí |
| GET | `/api/v1/workers` | Listar trabajadores | Sí |
| GET | `/api/v1/workers/{id}` | Detalle trabajador | Sí |
| GET | `/api/v1/machines` | Listar maquinaria | Sí |
| GET | `/api/v1/machines/{id}` | Detalle máquina | Sí |
| POST | `/api/v1/predict` | Predecir riesgo | Sí |
| POST | `/api/v1/predict/batch` | Predicción batch | Sí |
| GET | `/api/v1/alerts` | Listar alertas | Sí |
| POST | `/api/v1/alerts/{id}/ack` | Acknowledge alerta | Sí |
| GET | `/api/v1/alerts/stream` | WebSocket alertas | Sí (WS) |
| GET | `/api/v1/events` | Historial de eventos | Sí |
| GET | `/api/v1/events/{id}` | Detalle evento | Sí |
| POST | `/api/v1/reports` | Generar reporte | Sí |
| GET | `/api/v1/reports/{id}/download` | Descargar reporte | Sí |
| POST | `/api/v1/gemini/analyze` | Análisis IA de evento | Sí |
| POST | `/api/v1/gemini/chat` | Chatbot seguridad | Sí |
| GET | `/api/v1/dashboard/stats` | KPIs dashboard | Sí |
| GET | `/api/v1/dashboard/risk-trend` | Tendencia de riesgo | Sí |

### 9.2 Esquema de Predicción

```json
// POST /api/v1/predict
{
  "worker_id": "W-001",
  "machine_id": "M-003",
  "features": {
    "worker_x": 125.4,
    "worker_y": 78.2,
    "worker_z": -320.5,
    "machine_x": 130.1,
    "machine_y": 80.0,
    "machine_z": -320.5,
    "distance_3d": 5.2,
    "worker_speed": 1.2,
    "machine_speed": 3.5,
    "relative_speed": 4.1,
    "direction_worker": 2,
    "direction_machine": 6,
    "ttc": 8.5,
    "in_restricted_zone": 1,
    "machine_status": 1
  }
}

// Response
{
  "prediction": "ALTO",
  "probability": {
    "BAJO": 0.05,
    "MEDIO": 0.15,
    "ALTO": 0.80
  },
  "risk_score": 0.80,
  "alert_triggered": true,
  "alert_level": "ALTO",
  "timestamp": "2026-08-27T21:23:00Z",
  "model_version": "xgb_v1.2.0",
  "explanation": {
    "top_features": ["distance_3d", "ttc", "in_restricted_zone"]
  }
}
```

### 9.3 WebSocket para Alertas en Tiempo Real

```json
// Mensaje de alerta (servidor → cliente)
{
  "type": "RISK_ALERT",
  "timestamp": "2026-08-27T21:23:05Z",
  "alert_id": "ALT-20260827-001",
  "worker": {
    "id": "W-001",
    "name": "Juan Pérez",
    "position": {"x": 125.4, "y": 78.2, "z": -320.5}
  },
  "machine": {
    "id": "M-003",
    "type": "LHD",
    "position": {"x": 130.1, "y": 80.0, "z": -320.5}
  },
  "risk_level": "ALTO",
  "risk_score": 0.85,
  "message": "Trabajador en zona restringida con maquinaria en operación",
  "recommended_action": "Detener operación y evacuar trabajador"
}
```

---

## 10. Estructura de Base de Datos (PostgreSQL)

### 10.1 Diagrama Entidad-Relación (Simplificado)

```
┌─────────────┐       ┌─────────────┐       ┌─────────────┐
│    users    │       │   workers   │       │  machines   │
├─────────────┤       ├─────────────┤       ├─────────────┤
│ id (PK)     │       │ id (PK)     │       │ id (PK)     │
│ email       │       │ worker_code │       │ machine_code│
│ password_hash│      │ full_name   │       │ type        │
│ role        │       │ role_job    │       │ model       │
│ is_active   │       │ area        │       │ status      │
│ created_at  │       │ is_active   │       │ created_at  │
└─────────────┘       └──────┬──────┘       └──────┬──────┘
                             │                     │
                             └─────────┬───────────┘
                                       │
                              ┌────────▼────────┐
                              │  interactions   │
                              ├─────────────────┤
                              │ id (PK)         │
                              │ worker_id (FK)  │
                              │ machine_id (FK) │
                              │ timestamp       │
                              │ distance_3d     │
                              │ ttc             │
                              │ worker_speed    │
                              │ machine_speed   │
                              │ relative_speed  │
                              │ in_restricted_zone│
                              │ machine_status  │
                              │ risk_level      │
                              │ risk_score      │
                              │ alert_triggered │
                              │ model_version   │
                              └────────┬────────┘
                                       │
                              ┌────────▼────────┐
                              │     alerts      │
                              ├─────────────────┤
                              │ id (PK)         │
                              │ interaction_id  │
                              │ alert_level     │
                              │ message         │
                              │ status          │
                              │ acknowledged_by │
                              │ acknowledged_at │
                              │ created_at      │
                              └─────────────────┘
```

### 10.2 Tablas Adicionales

| Tabla | Propósito |
|-------|-----------|
| `restricted_zones` | Definición geométrica de zonas restringidas (PostGIS) |
| `events_log` | Log de auditoría de todas las operaciones |
| `reports` | Metadatos de reportes generados |
| `model_versions` | Versionado de modelos ML desplegados |
| `gemini_interactions` | Log de interacciones con Gemini API |

---

## 11. Integración Modelo Entrenado con FastAPI

### 11.1 Estrategia de Carga

```python
# app/ml/model_loader.py
import joblib
from pathlib import Path

class MLModelService:
    def __init__(self):
        self.model = None
        self.scaler = None
        self.feature_names = None
        self.model_version = None
        self.thresholds = {"BAJO": 0.33, "MEDIO": 0.66, "ALTO": 1.0}
    
    def load_model(self, model_path: str):
        artifact = joblib.load(model_path)
        self.model = artifact["model"]
        self.scaler = artifact["scaler"]
        self.feature_names = artifact["feature_names"]
        self.model_version = artifact["version"]
    
    def predict(self, features: dict) -> dict:
        # Preprocesamiento
        X = self._preprocess(features)
        # Predicción
        probabilities = self.model.predict_proba(X)[0]
        # Aplicar threshold optimizado para recall de ALTO
        prediction_idx = self._apply_threshold(probabilities)
        # Mapear a etiquetas
        labels = ["BAJO", "MEDIO", "ALTO"]
        return {
            "prediction": labels[prediction_idx],
            "probabilities": dict(zip(labels, probabilities)),
            "risk_score": float(probabilities[2]),  # Score de ALTO
            "model_version": self.model_version
        }
```

### 11.2 Endpoint de Predicción

```python
# app/api/endpoints/predict.py
from fastapi import APIRouter, Depends
from app.ml.model_loader import ml_service
from app.schemas.prediction import PredictionRequest, PredictionResponse
from app.core.security import get_current_user

router = APIRouter()

@router.post("/predict", response_model=PredictionResponse)
async def predict_risk(
    request: PredictionRequest,
    current_user = Depends(get_current_user)
):
    result = ml_service.predict(request.features.dict())
    
    # Persistir interacción
    interaction = await save_interaction(request, result)
    
    # Generar alerta si corresponde
    if result["risk_score"] > 0.6:
        await alert_engine.create_alert(interaction.id, result)
    
    return PredictionResponse(**result, interaction_id=interaction.id)
```

---

## 12. Integración de Gemini API

### 12.1 Casos de Uso

| Caso de Uso | Prompt Template |
|-------------|-----------------|
| **Análisis de alerta** | "Analiza la siguiente alerta de seguridad minera y proporciona recomendaciones: [datos]" |
| **Resumen de reporte** | "Genera un resumen ejecutivo del siguiente reporte de riesgo: [datos]" |
| **Chatbot normativa** | "Responde como experto en seguridad minera subterránea: [pregunta]" |
| **Recomendaciones** | "Basado en estos eventos de riesgo, sugiere medidas preventivas: [datos]" |

### 12.2 Servicio de Gemini

```python
# app/services/gemini_service.py
import google.generativeai as genai
from app.core.config import settings

class GeminiService:
    def __init__(self):
        genai.configure(api_key=settings.GEMINI_API_KEY)
        self.model = genai.GenerativeModel('gemini-pro')
    
    async def analyze_alert(self, alert_data: dict) -> str:
        prompt = f"""
        Eres un experto en seguridad minera subterránea. Analiza la siguiente alerta:
        
        Trabajador: {alert_data['worker_name']}
        Máquina: {alert_data['machine_type']} ({alert_data['machine_id']})
        Nivel de riesgo: {alert_data['risk_level']}
        Distancia: {alert_data['distance']}m
        TTC: {alert_data['ttc']}s
        Zona restringida: {'Sí' if alert_data['in_restricted_zone'] else 'No'}
        
        Proporciona:
        1. Evaluación de la situación
        2. Acciones inmediatas recomendadas
        3. Medidas preventivas a largo plazo
        """
        
        response = await self.model.generate_content_async(prompt)
        return response.text
```

### 12.3 Circuit Breaker

```python
# Implementación con tenacity o librería similar
@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
async def gemini_call_with_fallback(prompt: str) -> str:
    try:
        return await gemini_service.generate(prompt)
    except Exception:
        return "Servicio de IA no disponible. Consulte al supervisor."
```

---

## 13. Diseño del Gemelo Digital 3D

### 13.1 Especificaciones Técnicas

| Aspecto | Especificación |
|---------|---------------|
| **Motor 3D** | Three.js v0.160+ |
| **Framework React** | React Three Fiber (@react-three/fiber) |
| **UI 3D** | @react-three/drei |
| **Estado 3D** | Zustand |
| **Animaciones** | @react-spring/three |
| **Formato de modelo** | GLTF/GLB (optimizado) |

### 13.2 Escena 3D

```
┌─────────────────────────────────────────────────────────────┐
│                    ESCENA 3D - FRENTE DE EXTRACCIÓN          │
│                                                              │
│   ┌──────────────┐                                          │
│   │   Túnel      │  ← Geometría procedural del túnel       │
│   │  (Malla)     │     (sección circular/rectangular)      │
│   └──────────────┘                                          │
│                                                              │
│        🧍 W-001 (Verde)    ─── Trabajador BAJO riesgo      │
│                                                              │
│        🧍 W-002 (Amarillo) ─── Trabajador MEDIO riesgo     │
│                                                              │
│        🧍 W-003 (Rojo) ⚠️   ─── Trabajador ALTO riesgo     │
│                                                              │
│        🚜 M-001 (Azul)      ─── Maquinaria en operación      │
│                                                              │
│   ╔═══════════════════════╗                                 │
│   ║  ZONA RESTRINGIDA     ║  ← Volumen semitransparente     │
│   ║  (Rojo transparente)  ║     con efecto de pulso           │
│   ╚═══════════════════════╝                                 │
│                                                              │
│   [Panel Info]  [Leyenda]  [Controles Cámara]  [Timeline]    │
└─────────────────────────────────────────────────────────────┘
```

### 13.3 Componentes 3D

| Componente | Descripción |
|-------------|-------------|
| `TunnelGeometry` | Malla del túnel subterráneo con texturas de roca |
| `WorkerAvatar` | Avatar simplificado del trabajador con indicador de color |
| `MachineModel` | Modelo GLB de maquinaria (LHD, Jumbo, Camión) |
| `RestrictedZone` | Volumen 3D semitransparente con animación de pulso |
| `RiskIndicator` | Halo/aura alrededor de entidades según nivel de riesgo |
| `TrajectoryLine` | Línea de trayectoria predictiva (dashed line) |
| `CollisionCone` | Cono de visión/colisión de la maquinaria |
| `InfoPanel3D` | Panel flotante con datos de la entidad seleccionada |

### 13.4 Estados Visuales

| Nivel de Riesgo | Color Avatar | Halo | Efecto Adicional |
|-----------------|------------|------|------------------|
| BAJO | Verde `#22c55e` | Sutil | Ninguno |
| MEDIO | Amarillo `#eab308` | Moderado | Parpadeo lento |
| ALTO | Rojo `#ef4444` | Intenso | Parpadeo rápido + sonido |

---

## 14. Estructura de Carpetas

```
m11-sistema-alerta-riesgo/
├── 📁 backend/
│   ├── 📁 app/
│   │   ├── 📁 api/
│   │   │   ├── 📁 endpoints/
│   │   │   │   ├── auth.py
│   │   │   │   ├── users.py
│   │   │   │   ├── workers.py
│   │   │   │   ├── machines.py
│   │   │   │   ├── predict.py
│   │   │   │   ├── alerts.py
│   │   │   │   ├── events.py
│   │   │   │   ├── reports.py
│   │   │   │   └── gemini.py
│   │   │   └── deps.py
│   │   ├── 📁 core/
│   │   │   ├── config.py
│   │   │   ├── security.py
│   │   │   └── logging.py
│   │   ├── 📁 db/
│   │   │   ├── base.py
│   │   │   ├── session.py
│   │   │   └── init_db.py
│   │   ├── 📁 models/
│   │   │   ├── user.py
│   │   │   ├── worker.py
│   │   │   ├── machine.py
│   │   │   ├── interaction.py
│   │   │   ├── alert.py
│   │   │   ├── event_log.py
│   │   │   ├── report.py
│   │   │   └── restricted_zone.py
│   │   ├── 📁 schemas/
│   │   │   ├── user.py
│   │   │   ├── prediction.py
│   │   │   ├── alert.py
│   │   │   └── report.py
│   │   ├── 📁 services/
│   │   │   ├── alert_engine.py
│   │   │   ├── report_generator.py
│   │   │   └── gemini_service.py
│   │   ├── 📁 ml/
│   │   │   ├── model_loader.py
│   │   │   ├── preprocessor.py
│   │   │   ├── feature_engineering.py
│   │   │   └── artifacts/
│   │   │       ├── model_v1.0.0.joblib
│   │   │       └── scaler_v1.0.0.joblib
│   │   ├── 📁 websocket/
│   │   │   └── alert_manager.py
│   │   └── main.py
│   ├── 📁 alembic/                    # Migraciones
│   ├── 📁 tests/
│   ├── 📁 scripts/
│   │   ├── generate_synthetic_data.py
│   │   ├── train_model.py
│   │   └── evaluate_model.py
│   ├── 📁 notebooks/
│   │   ├── 01_eda.ipynb
│   │   ├── 02_feature_engineering.ipynb
│   │   ├── 03_model_training.ipynb
│   │   └── 04_model_evaluation.ipynb
│   ├── Dockerfile
│   ├── requirements.txt
│   └── pyproject.toml
│
├── 📁 frontend/
│   ├── 📁 src/
│   │   ├── 📁 app/
│   │   │   ├── 📁 (auth)/
│   │   │   │   ├── login/
│   │   │   │   └── register/
│   │   │   ├── 📁 (dashboard)/
│   │   │   │   ├── page.tsx
│   │   │   │   └── layout.tsx
│   │   │   ├── 📁 gemelo-digital/
│   │   │   │   └── page.tsx
│   │   │   ├── 📁 monitoreo/
│   │   │   │   ├── trabajadores/
│   │   │   │   └── maquinaria/
│   │   │   ├── 📁 alertas/
│   │   │   │   └── page.tsx
│   │   │   ├── 📁 historial/
│   │   │   │   └── page.tsx
│   │   │   ├── 📁 reportes/
│   │   │   │   └── page.tsx
│   │   │   ├── 📁 admin/
│   │   │   │   ├── usuarios/
│   │   │   │   └── roles/
│   │   │   └── layout.tsx
│   │   ├── 📁 components/
│   │   │   ├── 📁 ui/                 # shadcn/ui components
│   │   │   ├── 📁 dashboard/
│   │   │   │   ├── RiskChart.tsx
│   │   │   │   ├── StatsCards.tsx
│   │   │   │   └── AlertFeed.tsx
│   │   │   ├── 📁 gemelo-3d/
│   │   │   │   ├── Scene3D.tsx
│   │   │   │   ├── TunnelGeometry.tsx
│   │   │   │   ├── WorkerAvatar.tsx
│   │   │   │   ├── MachineModel.tsx
│   │   │   │   ├── RestrictedZone.tsx
│   │   │   │   ├── RiskIndicator.tsx
│   │   │   │   ├── CameraControls.tsx
│   │   │   │   └── InfoPanel3D.tsx
│   │   │   ├── 📁 alertas/
│   │   │   │   └── AlertCard.tsx
│   │   │   ├── 📁 reportes/
│   │   │   │   └── ReportGenerator.tsx
│   │   │   └── 📁 layout/
│   │   │       ├── Sidebar.tsx
│   │   │       ├── Header.tsx
│   │   │       └── Breadcrumb.tsx
│   │   ├── 📁 hooks/
│   │   │   ├── useWebSocket.ts
│   │   │   useAuth.ts
│   │   │   ├── usePrediction.ts
│   │   │   └── useGemini.ts
│   │   ├── 📁 lib/
│   │   │   ├── api.ts
│   │   │   ├── utils.ts
│   │   │   └── constants.ts
│   │   ├── 📁 store/
│   │   │   ├── authStore.ts
│   │   │   ├── alertStore.ts
│   │   │   └── sceneStore.ts
│   │   ├── 📁 types/
│   │   │   ├── index.ts
│   │   │   ├── prediction.ts
│   │   │   └── alert.ts
│   │   └── 📁 public/
│   │       └── 📁 models/
│   │           ├── lhd.glb
│   │           ├── jumbo.glb
│   │           └── worker_avatar.glb
│   ├── 📁 components/ui/              # shadcn/ui
│   ├── next.config.js
│   ├── tailwind.config.ts
│   ├── tsconfig.json
│   └── package.json
│
├── 📁 database/
│   ├── 📁 migrations/
│   ├── 📁 seeds/
│   └── init.sql
│
├── 📁 docs/
│   ├── 📁 arquitectura/
│   ├── 📁 api/
│   │   └── openapi.yaml
│   ├── 📁 ml/
│   │   └── model_documentation.md
│   └── 📁 usuario/
│       └── manual_usuario.md
│
├── 📁 infrastructure/
│   ├── docker-compose.yml
│   ├── 📁 k8s/                        # Kubernetes manifests
│   └── 📁 terraform/                  # IaC (futuro)
│
├── 📁 data/
│   ├── 📁 raw/                        # Datos sintéticos crudos
│   ├── 📁 processed/                  # Datos procesados
│   └── 📁 synthetic_generation/       # Scripts de generación
│
├── .env.example
├── .gitignore
├── README.md
└── Makefile
```

---

## 15. Plan de Implementación por Etapas

### 📌 Etapa 0: Fundamentos (Semana 1-2)
**Objetivo**: Infraestructura base y configuración del proyecto

- [ ] Configurar repositorio Git y estructura de carpetas
- [ ] Docker + docker-compose (PostgreSQL, Redis, backend, frontend)
- [ ] Configurar PostgreSQL con esquema inicial
- [ ] Setup FastAPI con estructura base
- [ ] Setup Next.js + TypeScript + Tailwind + shadcn/ui
- [ ] Configurar Alembic para migraciones
- [ ] Implementar autenticación JWT básica
- [ ] **Entregable**: Proyecto base corriendo localmente

---

### 📌 Etapa 1: Datos y Machine Learning (Semana 3-5)
**Objetivo**: Dataset sintético y modelo entrenado

- [ ] Implementar generador de datos sintéticos (`scripts/generate_synthetic_data.py`)
- [ ] Generar dataset de 50,000 registros con distribución balanceada
- [ ] Documentar claramente que los datos son sintéticos
- [ ] Feature engineering y preprocesamiento
- [ ] Entrenar Random Forest, XGBoost y SVM
- [ ] Evaluar con accuracy, precision, recall, F1, matriz de confusión
- [ ] Optimizar recall de clase ALTO
- [ ] Seleccionar mejor modelo y serializar (joblib)
- [ ] **Entregable**: Modelo entrenado + notebook de evaluación + métricas

---

### 📌 Etapa 2: Backend Core (Semana 6-8)
**Objetivo**: API REST funcional con predicciones

- [ ] Modelos SQLAlchemy y migraciones
- [ ] CRUD de trabajadores y maquinaria
- [ ] Endpoint `/predict` con integración del modelo
- [ ] Endpoint `/predict/batch`
- [ ] Sistema de alertas con persistencia
- [ ] WebSocket para streaming de alertas
- [ ] Middleware de autenticación y autorización
- [ ] Tests unitarios (pytest)
- [ ] **Entregable**: API REST documentada y testeada

---

### 📌 Etapa 3: Frontend Dashboard (Semana 9-11)
**Objetivo**: Interfaz de usuario principal

- [ ] Layout con sidebar y navegación
- [ ] Pantalla de login
- [ ] Dashboard con KPIs y gráficos (Recharts)
- [ ] Lista de trabajadores y maquinaria
- [ ] Feed de alertas en tiempo real (WebSocket)
- [ ] Historial de eventos con filtros
- [ ] Panel de administración de usuarios y roles
- [ ] **Entregable**: Dashboard funcional conectado al backend

---

### 📌 Etapa 4: Gemelo Digital 3D (Semana 12-14)
**Objetivo**: Visualización 3D interactiva

- [ ] Setup React Three Fiber
- [ ] Crear geometría del túnel
- [ ] Implementar avatares de trabajadores
- [ ] Implementar modelos de maquinaria
- [ ] Visualizar zonas restrictas (volúmenes 3D)
- [ ] Indicadores de riesgo por color y halo
- [ ] Cámara orbital y controles
- [ ] Sincronización con datos en tiempo real (WebSocket)
- [ ] **Entregable**: Gemelo Digital 3D interactivo

---

### 📌 Etapa 5: Reportes y Gemini (Semana 15-16)
**Objetivo**: Generación de documentos e IA generativa

- [ ] Generación de reportes PDF (ReportLab / WeasyPrint)
- [ ] Generación de reportes Excel (openpyxl)
- [ ] Generación de reportes Word (python-docx)
- [ ] Templates de reportes configurables
- [ ] Integración Gemini API
- [ ] Chatbot de consulta de seguridad
- [ ] Análisis automático de alertas
- [ ] Circuit breaker para Gemini
- [ ] **Entregable**: Sistema de reportes + IA integrada

---

### 📌 Etapa 6: Integración y Validación (Semana 17-18)
**Objetivo**: Sistema end-to-end funcional

- [ ] Integración completa frontend-backend
- [ ] Pruebas de carga (locust)
- [ ] Pruebas de usabilidad
- [ ] Documentación técnica completa
- [ ] Documentación de usuario
- [ ] Demo funcional del prototipo
- [ ] **Entregable**: Prototipo M-11 funcional y documentado

---

### 📌 Etapa 7: Despliegue y Cierre (Semana 19-20)
**Objetivo**: Preparación para producción

- [ ] Optimización de performance
- [ ] Docker optimizado (multi-stage)
- [ ] CI/CD básico (GitHub Actions)
- [ ] Manual de despliegue
- [ ] Presentación del prototipo
- [ ] Roadmap para producción (datos reales, edge computing, etc.)
- [ ] **Entregable**: Prototipo desplegable + presentación

---

## 16. Consideraciones de Seguridad y Ética

### 16.1 Datos Sintéticos
- Todos los datos del prototipo son generados algorítmicamente
- No se utiliza información personal real de trabajadores
- Se documenta explícitamente el origen sintético de los datos

### 16.2 Privacidad (Futuro)
- En producción, el sistema debe cumplir con regulaciones de privacidad laboral
- El monitoreo de posición debe ser notificado y consentido
- Los datos de ubicación son sensibles y deben anonimizarse para análisis

### 16.3 Fiabilidad del ML
- El modelo es un **asistente de decisión**, no reemplaza el juicio humano
- Las alertas ALTO requieren confirmación humana
- El sistema debe tener fallback si el modelo falla

---

## 17. Tecnologías y Dependencias Clave

### Backend
```
fastapi==0.109.0
uvicorn[standard]==0.27.0
sqlalchemy==2.0.25
asyncpg==0.29.0
alembic==1.13.1
pydantic==2.5.3
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4
python-multipart==0.0.6
scikit-learn==1.4.0
xgboost==2.0.3
numpy==1.26.3
pandas==2.1.4
joblib==1.3.2
redis==5.0.1
websockets==12.0
google-generativeai==0.3.2
reportlab==4.0.9
openpyxl==3.1.2
python-docx==1.1.0
pytest==7.4.4
httpx==0.26.0
```

### Frontend
```
next==14.1.0
react==18.2.0
typescript==5.3.3
tailwindcss==3.4.1
@react-three/fiber==8.15.16
@react-three/drei==9.96.5
three==0.160.0
@types/three==0.160.0
zustand==4.5.0
axios==1.6.5
recharts==2.10.4
lucide-react==0.312.0
class-variance-authority==0.7.0
clsx==2.1.0
tailwind-merge==2.2.0
```

---

## 18. Próximos Pasos

Una vez aprobada esta propuesta técnica, el desarrollo comenzará con la **Etapa 0** (Fundamentos), seguida de la generación del dataset sintético y el entrenamiento del modelo ML. Cada etapa incluirá revisiones de código, documentación y demos parciales.

¿Deseas que proceda a implementar alguna etapa específica, comenzando por la **generación del dataset sintético y el entrenamiento del modelo ML**?