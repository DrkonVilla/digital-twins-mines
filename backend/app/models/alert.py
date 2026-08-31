from datetime import datetime
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from app.db.session import Base

class Alert(Base):
    __tablename__ = "alerts"

    id = Column(Integer, primary_key=True, index=True)
    interaction_id = Column(Integer, ForeignKey("interactions.id"))
    alert_level = Column(String) # MEDIO, ALTO
    message = Column(String)
    status = Column(String, default="NEW") # NEW, ACKNOWLEDGED, RESOLVED
    acknowledged_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    acknowledged_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
