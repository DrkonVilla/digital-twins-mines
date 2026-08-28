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
