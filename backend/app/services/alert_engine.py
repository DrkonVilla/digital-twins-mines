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
    Guarda la interacción en la BD, calcula HMM + Particle Filter y difunde alerta por WebSocket.
    """
    from app.websocket.alert_manager import alert_manager
    from app.ml.hmm_model import hmm_engine
    from app.ml.particle_filter import particle_filter_engine
    
    telemetry_data = interaction_in.model_dump()

    # 1. Inferencia HMM (Hidden Markov Model - Tema 3)
    hmm_res = hmm_engine.estimate_hidden_state(telemetry_data)

    # 2. Predicción Filtro de Partículas a +30s (Particle Filter - Tema 3)
    particle_res = particle_filter_engine.predict_future_risk(telemetry_data)
    
    async with async_session() as session:
        # 3. Store the interaction
        risk_level = prediction["risk_level"]
        risk_score = prediction["risk_score"]
        
        valid_cols = {c.name for c in Interaction.__table__.columns}
        filtered_telemetry = {k: v for k, v in telemetry_data.items() if k in valid_cols}

        interaction = Interaction(
            **filtered_telemetry,
            risk_level=risk_level,
            risk_score=risk_score,
            alert_triggered=(risk_level in ["ALTO", "MEDIO"] or particle_res["early_warning_level"] != "SEGURO_30S"),
            model_version="xgb_v1"
        )
        session.add(interaction)
        await session.commit()
        await session.refresh(interaction)
        
        # 4. Check if we need to create an alert or broadcast status
        if interaction.alert_triggered or True: # Broadcast live telemetry to 3D twin
            alert_msg = f"Riesgo {risk_level} (ML): {risk_score}%. HMM: {hmm_res['hidden_state_name']}. 30s: {particle_res['early_warning_level']}"
            
            if interaction.alert_triggered:
                alert = Alert(
                    interaction_id=interaction.id,
                    alert_level=risk_level,
                    message=alert_msg
                )
                session.add(alert)
                await session.commit()
                await session.refresh(alert)
                alert_id = alert.id
            else:
                alert_id = interaction.id

            # 5. Broadcast complete payload over WebSockets to 3D Digital Twin
            await alert_manager.broadcast_alert({
                "alert_id": alert_id,
                "level": risk_level,
                "risk_level": risk_level,
                "risk_score": risk_score,
                "message": alert_msg,
                "worker_id": interaction.worker_id,
                "machine_id": interaction.machine_id,
                "distance": interaction.distance_3d,
                "timestamp": str(interaction.timestamp),

                # Posiciones 3D para movimiento del Gemelo Digital
                "worker_x": getattr(interaction_in, 'worker_x', 0.0),
                "worker_y": getattr(interaction_in, 'worker_y', 0.0),
                "worker_z": getattr(interaction_in, 'worker_z', 0.0),
                "machine_x": getattr(interaction_in, 'machine_x', 12.0),
                "machine_y": getattr(interaction_in, 'machine_y', 0.0),
                "machine_z": getattr(interaction_in, 'machine_z', 0.0),

                # Tema 3 Módulos Avanzados
                "hmm_state": hmm_res["hidden_state_name"],
                "hmm_probabilities": hmm_res["state_probabilities"],
                "particle_filter_30s": particle_res,
                "worker_bpm": interaction_in.worker_bpm,
                "fatigue_index": interaction_in.fatigue_index,
                "gas_co_ppm": interaction_in.gas_co_ppm,
                "dust_density_mg_m3": interaction_in.dust_density_mg_m3,
                "vibration_rms": interaction_in.vibration_rms
            })


