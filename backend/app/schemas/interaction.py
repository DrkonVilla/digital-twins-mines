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
    # Biometric, IMU, and Environmental Telemetry (Tema 3)
    worker_bpm: Optional[float] = 85.0
    fatigue_index: Optional[float] = 0.2
    vibration_rms: Optional[float] = 1.5
    acceleration_z: Optional[float] = 9.81
    gas_co_ppm: Optional[float] = 10.0
    dust_density_mg_m3: Optional[float] = 1.5
    ambient_light_lux: Optional[float] = 45.0

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
