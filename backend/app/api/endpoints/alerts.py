from typing import Any, List
from fastapi import APIRouter, Depends, WebSocket, WebSocketDisconnect
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.api.deps import get_db, get_current_user
from app.models.alert import Alert
from app.schemas.alert import Alert as AlertSchema
from app.websocket.alert_manager import alert_manager

router = APIRouter()

@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await alert_manager.connect(websocket)
    try:
        while True:
            # We just keep the connection open. Clients only listen.
            data = await websocket.receive_text()
    except WebSocketDisconnect:
        alert_manager.disconnect(websocket)

@router.get("/", response_model=List[AlertSchema])
async def read_alerts(
    db: AsyncSession = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    current_user = Depends(get_current_user),
) -> Any:
    result = await db.execute(select(Alert).order_by(Alert.created_at.desc()).offset(skip).limit(limit))
    alerts = result.scalars().all()
    return alerts
