from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class InteractionBase(BaseModel):
    worker_id: int
    machine_id: int
    worker_x: float
    worker_y: float
    worker_z: float
    machine_x: float
    machine_y: float
    machine_z: float
    direction_worker: int
    direction_machine: int
    distance_3d: float
    ttc: float
    worker_speed: float
    machine_speed: float
    relative_speed: float
    in_restricted_zone: int
    machine_status: int

class InteractionCreate(InteractionBase):
    pass

class Interaction(InteractionBase):
    id: int
    timestamp: datetime
    risk_level: str
    risk_score: float
    alert_triggered: bool
    model_version: str

    class Config:
        from_attributes = True
