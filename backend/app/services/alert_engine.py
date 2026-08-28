from typing import Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.db.session import async_session
from app.models.interaction import Interaction
from app.models.alert import Alert
from app.schemas.interaction import InteractionCreate
# from app.websocket.alert_manager import alert_manager # We will import inside function to avoid circular imports

async def process_prediction(interaction_in: InteractionCreate, prediction: Dict[str, Any]):
    """
    Guarda la interacción en la BD y evalúa si se debe generar una alerta.
    """
    from app.websocket.alert_manager import alert_manager
    
    async with async_session() as session:
        # 1. Store the interaction
        risk_level = prediction["risk_level"]
        risk_score = prediction["risk_score"]
        
        interaction = Interaction(
            **interaction_in.model_dump(),
            risk_level=risk_level,
            risk_score=risk_score,
            alert_triggered=(risk_level in ["ALTO", "MEDIO"]),
            model_version="xgb_v1"
        )
        session.add(interaction)
        await session.commit()
        await session.refresh(interaction)
        
        # 2. Check if we need to create an alert
        if interaction.alert_triggered:
            alert = Alert(
                interaction_id=interaction.id,
                alert_level=risk_level,
                message=f"Riesgo {risk_level} detectado: {risk_score}% de probabilidad."
            )
            session.add(alert)
            await session.commit()
            await session.refresh(alert)
            
            # 3. Broadcast over WebSockets
            await alert_manager.broadcast_alert({
                "alert_id": alert.id,
                "level": alert.alert_level,
                "message": alert.message,
                "worker_id": interaction.worker_id,
                "machine_id": interaction.machine_id,
                "distance": interaction.distance_3d,
                "timestamp": str(alert.created_at)
            })
