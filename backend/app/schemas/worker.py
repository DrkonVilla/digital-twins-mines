from pydantic import BaseModel
from typing import Optional

class WorkerBase(BaseModel):
    worker_code: str
    full_name: str
    role_job: Optional[str] = None
    area: Optional[str] = None
    is_active: Optional[bool] = True

class WorkerCreate(WorkerBase):
    pass

class Worker(WorkerBase):
    id: int

    class Config:
        from_attributes = True
