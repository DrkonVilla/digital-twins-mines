from datetime import datetime
from sqlalchemy import Column, Integer, String, Boolean, DateTime
from app.db.session import Base

class Machine(Base):
    __tablename__ = "machines"

    id = Column(Integer, primary_key=True, index=True)
    machine_code = Column(String, unique=True, index=True, nullable=False)
    type = Column(String, nullable=False)
    model = Column(String)
    status = Column(String, default="Detenida")
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
