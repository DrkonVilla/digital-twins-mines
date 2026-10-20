# 🏔️ Sistema M-11 — Gemelo Digital de Seguridad Minera Subterránea

> **M-11 Digital Twin** es una plataforma integral de alerta temprana inteligente para la prevención de colisiones y riesgos operacionales entre personal y maquinaria pesada (Scooptram, Dumpers, Jumbos) en minería subterránea. Combina un **Gemelo Digital 3D interactivo**, modelos de **Machine Learning (XGBoost / Voting Classifier)** entrenados sobre datasets híbridos industriales, un **Dashboard Analítico en Streamlit**, alertas en tiempo real vía **WebSocket** y un **Motor Resiliente de Protocolos de Emergencia** integrado con **Google Gemini AI**, **Langflow** y la normativa **D.S. 024-2016-EM / OSHA**.

---

## 📐 Arquitectura General del Sistema

```
digital-twins-mines/
├── backend/               # API REST FastAPI + WebSockets + Inferencia ML
│   ├── app/
│   │   ├── api/           # Endpoints REST (auth, workers, machines, predict, alerts, reports, gemini)
│   │   ├── core/          # Configuración, seguridad, JWT, CORS
│   │   ├── db/            # Sesión async SQLAlchemy (PostgreSQL / SQLite)
│   │   ├── ml/            # Motor ML Champion Loader y artefactos (.joblib)
│   │   ├── models/        # Modelos ORM (User, Worker, Machine, Interaction, Alert)
│   │   ├── schemas/       # Esquemas de validación Pydantic
│   │   ├── services/      # Lógica de negocio (alert_engine, gemini_service, reportes)
│   │   └── websocket/     # Gestor de conexiones WebSocket en vivo
│   ├── alembic/           # Migraciones de base de datos
│   ├── scripts/           # Scripts de entrenamiento ML y seed de datos
│   └── tests/             # Suite de pruebas unitarias y de integración (pytest)
│
├── frontend/              # Aplicación Web Next.js 16 + React 19 + Three.js
│   └── src/
│       ├── app/           # App Router (dashboard, gemelo 3D, alertas, monitoreo, api routes)
│       │   └── api/       # Route Handlers Next.js (/api/langflow con fallback autónomo)
│       ├── components/    # Componentes modulares UI (shadcn), 3D Canvas y Modales
│       ├── hooks/         # Hooks personalizados (useWebSocket)
│       ├── lib/           # Cliente HTTP Axios configurado y utilidades (api.ts, utils.ts)
│       └── store/         # Gestión de estado global con Zustand (authStore, alertStore)
│
├── ml_dashboard/          # Dashboard Analítico de Machine Learning (Streamlit)
│   ├── app.py             # Aplicación principal y visión ejecutiva
│   └── pages/             # Explorador de Dataset, Métricas, Estudio de Ablación e Inferencia
│
├── langflow/              # Flujos y Componentes de Langflow
│   ├── components/        # Componente personalizado MiningRiskPredictorComponent
│   └── mining_risk_prediction_flow.json  # Pipeline visual de evaluación de riesgos
│
└── data/raw/              # Dataset Oficial Híbrido (10,000 registros multimodales)
    └── public_mining_equipment_dataset.csv
```

---

## 📊 Dataset Oficial Híbrido y Pipeline de Machine Learning

El proyecto utiliza un dataset híbrido calibrado ([`data/raw/public_mining_equipment_dataset.csv`](data/raw/public_mining_equipment_dataset.csv)) que reemplaza datos sintéticos aleatorios con **10,000 ciclos operacionales reales**:

- **Base de Maquinaria Industrial (UCI AI4I 2020):** Datos de fatiga térmica, velocidad de rotación (RPM), par de torsión (Torque Nm) y desgaste de herramientas de equipos reales.
- **Cinemática Subterránea (UWB):** Posicionamiento tridimensional relativo ($X, Y, Z$), distancia 3D euclidiana y Tiempo Estimado al Impacto (**TTC** - *Time to Collision*).
- **Biometría de Operarios:** Frecuencia cardíaca (BPM) e índice dinámico de fatiga psicofísica.
- **Sensores Atmosféricos de Socavón:** Monóxido de Carbono (**CO ppm**) y densidad de polvo respirable ($\text{mg/m}^3$).

### Modelos y Validación Cruzada
- **Algoritmos Entrenados:** XGBoost, Random Forest, LightGBM y Ensamble por Votación Suave (*Voting Classifier*).
- **Estudio de Ablación:** Análisis riguroso del impacto de cada subconjunto de sensores (cinemáticos, fisiológicos, atmosféricos) sobre la métrica $F_1\text{-Score}$.
- **Reentrenar los modelos:**
  ```bash
  python backend/scripts/train_model.py
  ```

---

## 🚨 Motor Resiliente de Protocolos de Emergencia (M-11)

El sistema incorpora un mecanismo de resiliencia en cascada de 3 capas en [`frontend/src/app/api/langflow/route.ts`](frontend/src/app/api/langflow/route.ts):

1. **Capa 1 — Flujo Visual de Langflow:** Consulta al servidor Langflow local (`http://localhost:7860`) con timeout preventivo de 2.5s.
2. **Capa 2 — Inferencia Directa con Google Gemini:** Si Langflow no está activo pero se cuenta con `GEMINI_API_KEY`, consulta directamente a `gemini-2.5-flash` vía API REST.
3. **Capa 3 — Motor Normativo Determinista M-11:** Si no hay conexión externa ni API Key, genera de inmediato un **Protocolo de Emergencia Oficial** validado según el **D.S. 024-2016-EM (Perú)** y estándares **OSHA / MSHA**, detallando:
   - 🚨 Evaluación inmediata y matriz de telemetría de sensores en tiempo real.
   - 🚧 Acciones de frenado, paro de emergencia (E-Stop) y bloqueo hidráulico del equipo.
   - 🏃‍♂️ Protocolo de evacuación a nichos de seguridad y uso de autorescatadores ante gases (CO > 25 ppm).
   - 📋 Artículos legales (Art. 102, 248 y 250) y canal radial de emergencia (Canal 1).

---

## ✅ Prerrequisitos

| Herramienta | Versión mínima | Propósito |
| :--- | :--- | :--- |
| **Python** | 3.10+ (Recomendado 3.11 o 3.12) | Backend FastAPI y Dashboard Streamlit |
| **Node.js** | 18+ (Probado en v22) | Frontend Next.js 16 |
| **PostgreSQL / SQLite** | PostgreSQL 14+ o SQLite local | Base de datos relacional |
| **Git** | 2.30+ | Control de versiones |

---

## 🚀 Guía de Instalación y Ejecución

### 1. Clonar el Repositorio

```bash
git clone https://github.com/marck-h-cmd/digital-twins-mines.git
cd digital-twins-mines
```

---

### 2. Configurar y Levantar el Backend (FastAPI)

```bash
cd backend

# Crear y activar entorno virtual
python -m venv venv
source venv/bin/activate       # En Linux / macOS
# .\venv\Scripts\Activate.ps1  # En Windows PowerShell

# Instalar dependencias
pip install -r requirements.txt
```

#### Archivo de Configuración (`backend/.env`):
```env
# Base de datos (SQLite por defecto o PostgreSQL)
M11_DATABASE_URL=sqlite+aiosqlite:///m11_db.db
# Para PostgreSQL:
# POSTGRES_SERVER=127.0.0.1
# POSTGRES_PORT=5433
# POSTGRES_USER=m11_user
# POSTGRES_PASSWORD=m11_password
# POSTGRES_DB=m11_db

# Seguridad JWT
SECRET_KEY=super-secret-key-change-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60

# Google Gemini (opcional para IA Generativa)
GEMINI_API_KEY=tu_api_key_aqui
```

#### Iniciar el Backend:
```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```
- **API Base:** [http://localhost:8000](http://localhost:8000)
- **Documentación Swagger:** [http://localhost:8000/docs](http://localhost:8000/docs)
- **ReDoc:** [http://localhost:8000/redoc](http://localhost:8000/redoc)

---

### 3. Configurar y Levantar el Frontend (Next.js)

En una nueva terminal:
```bash
cd frontend
npm install
```

#### Archivo de Configuración (`frontend/.env.local`):
```env
NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1
NEXT_PUBLIC_WS_URL=ws://localhost:8000/api/v1/alerts/ws
```

#### Iniciar el Servidor de Desarrollo:
```bash
npm run dev
```
- **Frontend:** [http://localhost:3000](http://localhost:3000)

---

### 4. Levantar el Dashboard de Machine Learning (Streamlit)

En una nueva terminal (con el entorno virtual de Python activo):
```bash
cd ml_dashboard
streamlit run app.py --server.port 8501
```
- **ML Analytics:** [http://localhost:8501](http://localhost:8501)

---

## 🔑 Credenciales por Defecto

| Usuario | Contraseña | Rol |
| :--- | :--- | :--- |
| `admin@example.com` | `admin123` | Administrador / Supervisor de Seguridad |

---

## 📱 Módulos y Vistas de la Plataforma

| Módulo | Ruta | Descripción |
| :--- | :--- | :--- |
| **Inicio de Sesión** | `/` o `/login` | Autenticación basada en JWT con guardado seguro de sesión |
| **Centro de Control** | `/dashboard` | KPIs operativos, estado de flota, gráfico de tendencia y alertas en vivo |
| **Gemelo Digital 3D** | `/gemelo-digital` | Renderizado interactivo Three.js de socavón minero con maquinaria y personal |
| **Feed de Alertas** | `/alertas` | Notificaciones en tiempo real vía WebSocket con generación de protocolos de emergencia |
| **Monitoreo de Maquinaria** | `/monitoreo/maquinaria` | Telemetría de Scooptrams, dumpers y jumbos con estados de motor y velocidad |
| **Monitoreo de Personal** | `/monitoreo/trabajadores` | Signos vitales, localización UWB y niveles de fatiga de cuadrillas |
| **Historial Predictivo** | `/historial` | Registro de interacciones hombre-máquina e inferencias del modelo campeón |
| **Reportes e IA** | `/reportes` | Descarga de informes de seguridad (PDF / Excel / Word) y asistente conversacional |
| **ML Studio** | `:8501` | Portal analítico de métricas, curvas ROC, matriz de confusión y simulación en vivo |

---

## 🧪 Pruebas Unitarias y de Integración

Para ejecutar la suite de validación del backend:
```bash
cd backend
PYTHONPATH=. pytest tests/ -v
```

Para verificar la compilación de producción del frontend:
```bash
cd frontend
npm run build
```

---

## 🛠️ Stack Tecnológico

- **Backend:** FastAPI, Python 3.11+, SQLAlchemy Async, Uvicorn, Pydantic v2, PyJWT.
- **Machine Learning:** XGBoost, Scikit-learn, LightGBM, Joblib, Pandas, NumPy.
- **Frontend:** Next.js 16 (App Router), React 19, TypeScript, Tailwind CSS v4, Three.js, React Three Fiber, Lucide Icons, Zustand, Axios.
- **Analítica:** Streamlit, Matplotlib, Seaborn, Plotly.
- **IA Generativa & Flujos:** Google Gemini 2.5 Flash, LangChain, Langflow.
- **Protocolos Normativos:** D.S. 024-2016-EM (Reglamento de Seguridad y Salud Ocupacional en Minería - Perú), OSHA 29 CFR 1926.651, MSHA 30 CFR 57.

---

## 👤 Autor

**Marck H.** — [@marck-h-cmd](https://github.com/marck-h-cmd)  
Universidad Nacional de Trujillo — Ingeniería de Sistemas
