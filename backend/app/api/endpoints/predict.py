from typing import Any, List
from fastapi import APIRouter, Depends
from pydantic import BaseModel

from app.api.deps import get_current_user
from app.ml.model_loader import ml_engine
from app.schemas.interaction import InteractionCreate
from app.services.alert_engine import process_prediction

router = APIRouter()

class PredictionResult(BaseModel):
    risk_level: str
    risk_score: float

@router.post("/", response_model=PredictionResult)
async def predict_interaction(
    *,
    interaction_in: InteractionCreate,
    current_user = Depends(get_current_user),
) -> Any:
    # 1. Run prediction
    features = interaction_in.model_dump()
    # ML model expects features directly corresponding to the training data columns
    # We might need to map them slightly, but for now they match
    result = ml_engine.predict(features)
    
    # 2. Process alerts and store interaction
    await process_prediction(interaction_in, result)
    
    return result

@router.post("/batch", response_model=List[PredictionResult])
async def predict_interactions_batch(
    *,
    interactions_in: List[InteractionCreate],
    current_user = Depends(get_current_user),
) -> Any:
    # 1. Run batch prediction
    features_list = [i.model_dump() for i in interactions_in]
    results = ml_engine.predict_batch(features_list)
    
    # 2. Process alerts and store interactions
    for interaction, result in zip(interactions_in, results):
        await process_prediction(interaction, result)
        
    return results

import asyncio
from fastapi import BackgroundTasks

async def run_simulation_background():
    scenarios = [
        # Escenario 1: Normal
        {
            "worker_id": 1, "machine_id": 1,
            "worker_x": 0.0, "worker_y": 0.0, "worker_z": 0.0,
            "machine_x": 35.0, "machine_y": 0.0, "machine_z": 0.0,
            "direction_worker": 0, "direction_machine": 4,
            "distance_3d": 35.0, "ttc": 45.0,
            "worker_speed": 0.8, "machine_speed": 2.0, "relative_speed": 2.8,
            "in_restricted_zone": 0, "machine_status": 1,
            "worker_bpm": 76.0, "fatigue_index": 0.15,
            "vibration_rms": 0.8, "acceleration_z": 9.81,
            "gas_co_ppm": 8.0, "dust_density_mg_m3": 0.8, "ambient_light_lux": 80.0
        },
        # Escenario 2: Advertencia (Fatiga + Proximidad Moderada)
        {
            "worker_id": 1, "machine_id": 1,
            "worker_x": 0.0, "worker_y": 0.0, "worker_z": 0.0,
            "machine_x": 12.0, "machine_y": 0.0, "machine_z": 0.0,
            "direction_worker": 1, "direction_machine": 5,
            "distance_3d": 12.0, "ttc": 12.0,
            "worker_speed": 1.2, "machine_speed": 4.0, "relative_speed": 5.2,
            "in_restricted_zone": 1, "machine_status": 1,
            "worker_bpm": 115.0, "fatigue_index": 0.48,
            "vibration_rms": 1.8, "acceleration_z": 9.81,
            "gas_co_ppm": 22.0, "dust_density_mg_m3": 2.1, "ambient_light_lux": 45.0
        },
        # Escenario 3: Riesgo Crítico (Colisión + Fatiga Alta + Gas CO)
        {
            "worker_id": 1, "machine_id": 1,
            "worker_x": 0.0, "worker_y": 0.0, "worker_z": 0.0,
            "machine_x": 3.0, "machine_y": 0.0, "machine_z": 0.0,
            "direction_worker": 2, "direction_machine": 6,
            "distance_3d": 3.0, "ttc": 0.8,
            "worker_speed": 1.5, "machine_speed": 5.0, "relative_speed": 6.5,
            "in_restricted_zone": 1, "machine_status": 1,
            "worker_bpm": 145.0, "fatigue_index": 0.88,
            "vibration_rms": 3.2, "acceleration_z": 9.81,
            "gas_co_ppm": 65.0, "dust_density_mg_m3": 5.5, "ambient_light_lux": 15.0
        }
    ]

    for item in scenarios:
        interaction_in = InteractionCreate(**item)
        features = interaction_in.model_dump()
        result = ml_engine.predict(features)
        await process_prediction(interaction_in, result)
        await asyncio.sleep(2.5)

@router.post("/simulate")
async def trigger_simulation(
    background_tasks: BackgroundTasks,
) -> Any:
    background_tasks.add_task(run_simulation_background)
    return {"message": "Simulación de telemetría iniciada exitosamente"}
