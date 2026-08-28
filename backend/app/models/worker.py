from sqlalchemy import Column, Integer, String, Boolean, Float
from app.db.session import Base

class Worker(Base):
    __tablename__ = "workers"

    id = Column(Integer, primary_key=True, index=True)
    worker_code = Column(String, unique=True, index=True, nullable=False)
    full_name = Column(String, nullable=False)
    role_job = Column(String)
    area = Column(String)
    is_active = Column(Boolean, default=True)
