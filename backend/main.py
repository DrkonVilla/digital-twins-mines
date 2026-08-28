from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.api.endpoints import auth, workers, machines, predict, alerts, users, gemini, reports

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    openapi_url=f"{settings.API_V1_STR}/openapi.json"
)

# Set all CORS enabled origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Update for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def root():
    return {"message": "M-11 API Server v1.0.0 is running"}

app.include_router(auth.router, prefix=f"{settings.API_V1_STR}/auth", tags=["auth"])
app.include_router(users.router, prefix=f"{settings.API_V1_STR}/users", tags=["users"])
app.include_router(workers.router, prefix=f"{settings.API_V1_STR}/workers", tags=["workers"])
app.include_router(machines.router, prefix=f"{settings.API_V1_STR}/machines", tags=["machines"])
app.include_router(predict.router, prefix=f"{settings.API_V1_STR}/predict", tags=["predict"])
app.include_router(alerts.router, prefix=f"{settings.API_V1_STR}/alerts", tags=["alerts"])
app.include_router(gemini.router, prefix=f"{settings.API_V1_STR}/gemini", tags=["gemini"])
app.include_router(reports.router, prefix=f"{settings.API_V1_STR}/reports", tags=["reports"])
