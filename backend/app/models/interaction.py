from sqlalchemy import Column, Integer, Float, ForeignKey, DateTime, String, Boolean
from sqlalchemy.sql import func
from app.db.session import Base

class Interaction(Base):
    __tablename__ = "interactions"

    id = Column(Integer, primary_key=True, index=True)
    worker_id = Column(Integer, ForeignKey("workers.id"))
    machine_id = Column(Integer, ForeignKey("machines.id"))
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
    
    distance_3d = Column(Float)
    ttc = Column(Float)
    worker_speed = Column(Float)
    machine_speed = Column(Float)
    relative_speed = Column(Float)
    in_restricted_zone = Column(Integer)
    machine_status = Column(Integer)
    
    risk_level = Column(String, default="BAJO") # BAJO, MEDIO, ALTO
    risk_score = Column(Float)
    alert_triggered = Column(Boolean, default=False)
    model_version = Column(String)
