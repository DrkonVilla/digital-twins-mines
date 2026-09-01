import pytest
from httpx import AsyncClient, ASGITransport
from main import app as fastapi_app
from app.core.security import create_access_token
from app.db.session import engine, Base
import app.models.user
import app.models.worker
import app.models.machine
import app.models.interaction
import app.models.alert

@pytest.fixture(autouse=True)
async def setup_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

@pytest.fixture
def token():
    return create_access_token(data={"sub": "admin@example.com"})

@pytest.fixture
def headers(token):
    return {"Authorization": f"Bearer {token}"}

@pytest.mark.asyncio
async def test_predict_endpoint(headers):
    # Using ASGITransport to avoid DeprecationWarnings in newer httpx versions
    transport = ASGITransport(app=fastapi_app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        interaction_data = {
            "worker_id": 1,
            "machine_id": 1,
            "worker_x": 0.0,
            "worker_y": 0.0,
            "worker_z": 0.0,
            "machine_x": 1.5,
            "machine_y": 0.0,
            "machine_z": 0.0,
            "direction_worker": 1,
            "direction_machine": 2,
            "distance_3d": 1.5,
            "ttc": 2.0,
            "worker_speed": 1.0,
            "machine_speed": 5.0,
            "relative_speed": 6.0,
            "in_restricted_zone": 1,
            "machine_status": 1
        }
        
        response = await ac.post("/api/v1/predict/", json=interaction_data, headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert "risk_level" in data
        assert "risk_score" in data
        # Con esos datos esperamos que el riesgo sea ALTO o al menos que devuelva correctamente la info
        print(f"Prediction Output: {data}")

@pytest.mark.asyncio
async def test_read_workers(headers):
    transport = ASGITransport(app=fastapi_app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        response = await ac.get("/api/v1/workers/", headers=headers)
        assert response.status_code == 200
        assert isinstance(response.json(), list)

@pytest.mark.asyncio
async def test_auth_no_token():
    transport = ASGITransport(app=fastapi_app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        response = await ac.get("/api/v1/workers/")
        assert response.status_code == 401
