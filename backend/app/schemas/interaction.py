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
    # Biometric Wearables (FICHA 11: Frecuencia cardíaca, HRV, Movimientos oculares/fatiga)
    worker_bpm: Optional[float] = 85.0
    hrv_ms: Optional[float] = 45.0  # Variabilidad de la Frecuencia Cardíaca (HRV)
    eye_blink_rate: Optional[float] = 18.0  # Frecuencia de parpadeo / min
    fixation_duration_ms: Optional[float] = 320.0  # Duración de fijación ocular
    fatigue_index: Optional[float] = 0.2

    # IoT Equipment Sensors (FICHA 11: Trayectoria, velocidad, vibraciones, pendiente, paredes)
    vibration_rms: Optional[float] = 1.5
    acceleration_z: Optional[float] = 9.81
    machine_slope_angle: Optional[float] = 4.5  # Ángulo de inclinación / pendiente (grados)
    wall_distance: Optional[float] = 1.8  # Distancia a paredes del túnel (m)

    # Environmental Sensors & NTP Synchronization 1ms (FICHA 11: Iluminación, polvo, CO, NO2)
    gas_co_ppm: Optional[float] = 10.0
    gas_no2_ppm: Optional[float] = 1.2
    dust_density_mg_m3: Optional[float] = 1.5
    ambient_light_lux: Optional[float] = 45.0
    ntp_sync_precision_ms: Optional[float] = 1.0  # Precision NTP 1 ms

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
