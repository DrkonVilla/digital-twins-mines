from datetime import datetime
from sqlalchemy import Column, Integer, Float, ForeignKey, DateTime, String, Boolean
from app.db.session import Base

class Interaction(Base):
    __tablename__ = "interactions"

    id = Column(Integer, primary_key=True, index=True)
    worker_id = Column(Integer, ForeignKey("workers.id"))
    machine_id = Column(Integer, ForeignKey("machines.id"))
    timestamp = Column(DateTime(timezone=True), default=datetime.utcnow)
    worker_x = Column(Float)
    worker_y = Column(Float)
    worker_z = Column(Float)
    machine_x = Column(Float)
    machine_y = Column(Float)
    machine_z = Column(Float)
    direction_worker = Column(Integer)
    direction_machine = Column(Integer)
    distance_3d = Column(Float)
    ttc = Column(Float)
    worker_speed = Column(Float)
    machine_speed = Column(Float)
    relative_speed = Column(Float)
    in_restricted_zone = Column(Integer)
    machine_status = Column(Integer)
    
    # Biometric, IMU, and Environmental Telemetry
    worker_bpm = Column(Float, nullable=True)
    fatigue_index = Column(Float, nullable=True)
    vibration_rms = Column(Float, nullable=True)
    acceleration_z = Column(Float, nullable=True)
    gas_co_ppm = Column(Float, nullable=True)
    dust_density_mg_m3 = Column(Float, nullable=True)
    ambient_light_lux = Column(Float, nullable=True)

    risk_level = Column(String, default="BAJO") # BAJO, MEDIO, ALTO
    risk_score = Column(Float)
    alert_triggered = Column(Boolean, default=False)
    model_version = Column(String)
