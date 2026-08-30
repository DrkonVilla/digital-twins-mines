# 🏔️ Sistema M-11 — Digital Twin de Seguridad Minera

> Sistema de alerta temprana inteligente para la predicción de riesgos de proximidad entre trabajadores y maquinaria pesada en operaciones mineras subterráneas. Incluye un Gemelo Digital 3D interactivo, predicciones con Machine Learning (XGBoost), alertas en tiempo real vía WebSocket e integración con Gemini AI.

---

## 📐 Arquitectura

```
mines-prediction/
├── backend/          # FastAPI + SQLAlchemy (asyncpg) + XGBoost
│   ├── app/
│   │   ├── api/          # Endpoints REST + WebSocket
│   │   ├── core/         # Configuración, seguridad, JWT
│   │   ├── db/           # Sesión async, init DB
│   │   ├── ml/           # Motor de predicción XGBoost
│   │   ├── models/       # Modelos SQLAlchemy (ORM)
│   │   ├── schemas/      # Pydantic schemas
│   │   ├── services/     # Lógica de negocio (alertas, reportes, Gemini)
│   │   └── websocket/    # Alert Manager WebSocket
│   ├── alembic/          # Migraciones de base de datos
│   └── scripts/          # Seed data
└── frontend/         # Next.js 16 + React + Three.js
    └── src/
        ├── app/          # App Router (páginas del dashboard)
        ├── components/   # Componentes UI y 3D
        ├── hooks/        # Custom hooks (useWebSocket)
        ├── lib/          # Cliente Axios (api.ts)
        └── store/        # Zustand (auth, alerts)
```

---

## ✅ Prerrequisitos

| Herramienta | Versión mínima | Notas |
|-------------|---------------|-------|
| Python | 3.10+ | Para el backend |
| Node.js | 18+ | Para el frontend |
| PostgreSQL | 14+ | Escuchar en puerto **5433** |
| Git | — | Para clonar el repositorio |

---

## 🚀 Pasos de instalación y ejecución

### 1. Clonar el repositorio

```bash
git clone https://github.com/marck-h-cmd/digital-twins-mines.git
cd digital-twins-mines
```

---

### 2. Configurar la base de datos PostgreSQL

Asegúrate de que PostgreSQL esté corriendo en el **puerto 5433** (o ajusta el `.env` si usas otro puerto).

```sql
-- Ejecutar como superusuario de PostgreSQL
CREATE USER m11_user WITH PASSWORD 'm11_password';
CREATE DATABASE m11_db OWNER m11_user;
GRANT ALL PRIVILEGES ON DATABASE m11_db TO m11_user;
```

---

### 3. Configurar el Backend

```bash
cd backend
```

#### 3.1 Crear y activar el entorno virtual

```bash
# Windows
python -m venv venv
.\venv\Scripts\Activate.ps1

# macOS / Linux
python3 -m venv venv
source venv/bin/activate
```

#### 3.2 Instalar dependencias

```bash
pip install -r requirements.txt
```

#### 3.3 Crear el archivo `.env`

Crea el archivo `backend/.env` con el siguiente contenido:

```env
# Base de datos
POSTGRES_SERVER=127.0.0.1
POSTGRES_USER=m11_user
POSTGRES_PASSWORD=m11_password
POSTGRES_DB=m11_db
POSTGRES_PORT=5433

# JWT - cambia esto en producción
SECRET_KEY=super-secret-key-change-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Gemini AI (opcional pero recomendado para el chatbot)
GEMINI_API_KEY=tu_clave_aqui

# Redis (opcional para caché)
REDIS_URL=redis://localhost:6379/0
```

#### 3.4 Ejecutar las migraciones

```bash
alembic upgrade head
```

#### 3.5 Poblar la base de datos con datos iniciales

```bash
python scripts/seed_db.py
```

Esto crea el usuario administrador por defecto:
- **Email:** `admin@example.com`
- **Contraseña:** `admin123`

#### 3.6 Iniciar el servidor backend

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

El backend estará disponible en:
- API: `http://localhost:8000`
- Documentación interactiva (Swagger): `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

---

### 4. Configurar el Frontend

Abre una **nueva terminal** y ejecuta:

```bash
cd frontend
```

#### 4.1 Instalar dependencias

```bash
npm install
```

#### 4.2 Crear el archivo `.env.local`

Crea el archivo `frontend/.env.local`:

```env
NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1
NEXT_PUBLIC_WS_URL=ws://localhost:8000/api/v1/alerts/ws
```

#### 4.3 Iniciar el servidor de desarrollo

```bash
npm run dev
```

El frontend estará disponible en: `http://localhost:3000`

---

## 🔑 Credenciales de acceso

| Campo | Valor |
|-------|-------|
| Email | `admin@example.com` |
| Contraseña | `admin123` |

---

## 📱 Vistas disponibles

| Ruta | Descripción |
|------|-------------|
| `/` | Página de login |
| `/dashboard` | KPIs en vivo, gráfico de tendencia, feed de alertas |
| `/gemelo-digital` | Gemelo Digital 3D interactivo del túnel minero |
| `/monitoreo/trabajadores` | Listado de trabajadores y estados |
| `/monitoreo/maquinaria` | Listado de maquinaria y estados |
| `/alertas` | Historial completo de alertas |
| `/historial` | Historial de interacciones y predicciones |
| `/reportes` | Generador de reportes PDF/Excel/Word + Chatbot IA |

---

## 🧪 Ejecutar pruebas del backend

```bash
cd backend
.\venv\Scripts\Activate.ps1  # (Windows)
pytest tests/ -v
```

---

## 🔌 Endpoints principales de la API

### Autenticación
| Método | Ruta | Descripción |
|--------|------|-------------|
| `POST` | `/api/v1/auth/login` | Login — devuelve JWT |
| `GET` | `/api/v1/users/me` | Perfil del usuario actual |

### Predicción ML
| Método | Ruta | Descripción |
|--------|------|-------------|
| `POST` | `/api/v1/predict/` | Predice riesgo de una interacción |
| `POST` | `/api/v1/predict/batch` | Predicción por lotes |

### Alertas
| Método | Ruta | Descripción |
|--------|------|-------------|
| `GET` | `/api/v1/alerts/` | Lista historial de alertas |
| `WS` | `/api/v1/alerts/ws` | WebSocket de alertas en tiempo real |

### Reportes
| Método | Ruta | Descripción |
|--------|------|-------------|
| `POST` | `/api/v1/reports?format=pdf` | Genera reporte PDF |
| `POST` | `/api/v1/reports?format=excel` | Genera reporte Excel |
| `POST` | `/api/v1/reports?format=word` | Genera reporte Word |
| `GET` | `/api/v1/reports/{filename}/download` | Descarga un reporte |

### Gemini AI
| Método | Ruta | Descripción |
|--------|------|-------------|
| `POST` | `/api/v1/gemini/chat` | Chatbot de seguridad minera |
| `POST` | `/api/v1/gemini/analyze` | Análisis automático de alertas |

---

## 🛠️ Stack tecnológico

### Backend
- **FastAPI** — Framework web async
- **SQLAlchemy (asyncpg)** — ORM async para PostgreSQL
- **Alembic** — Migraciones de base de datos
- **XGBoost + scikit-learn** — Motor de predicción ML
- **PassLib + PyJWT** — Autenticación con BCrypt y JWT
- **ReportLab + openpyxl + python-docx** — Generación de reportes
- **Google Generative AI (Gemini)** — IA generativa
- **WebSockets** — Alertas en tiempo real

### Frontend
- **Next.js 16** (App Router) — Framework React
- **Three.js + React Three Fiber** — Gemelo Digital 3D
- **Recharts** — Gráficos de tendencias
- **Zustand** — Estado global (autenticación, alertas)
- **Axios** — Cliente HTTP con interceptores JWT
- **Lucide React** — Iconografía
- **shadcn/ui** — Componentes de interfaz

---

## 📋 Variables de entorno requeridas

### Backend (`backend/.env`)

| Variable | Descripción | Valor por defecto |
|----------|-------------|-------------------|
| `POSTGRES_SERVER` | Host de PostgreSQL | `127.0.0.1` |
| `POSTGRES_PORT` | Puerto de PostgreSQL | `5433` |
| `POSTGRES_USER` | Usuario de BD | `m11_user` |
| `POSTGRES_PASSWORD` | Contraseña de BD | `m11_password` |
| `POSTGRES_DB` | Nombre de la BD | `m11_db` |
| `SECRET_KEY` | Clave secreta JWT | `super-secret-key-...` |
| `GEMINI_API_KEY` | API Key de Google Gemini | _(vacío, opcional)_ |

### Frontend (`frontend/.env.local`)

| Variable | Descripción | Valor por defecto |
|----------|-------------|-------------------|
| `NEXT_PUBLIC_API_URL` | URL base del backend | `http://localhost:8000/api/v1` |
| `NEXT_PUBLIC_WS_URL` | URL WebSocket | `ws://localhost:8000/api/v1/alerts/ws` |

---

## 👤 Autor

**Marck H.** — [@marck-h-cmd](https://github.com/marck-h-cmd)  
Universidad Nacional de Trujillo — Software II

---

> ⚠️ **Nota**: Este proyecto es un prototipo académico. Para uso en producción se deben cambiar todas las claves secretas, configurar HTTPS y aplicar políticas de seguridad apropiadas.
