from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class MachineBase(BaseModel):
    machine_code: str
    type: str
    model: Optional[str] = None
    status: Optional[str] = "Detenida"

class MachineCreate(MachineBase):
    pass

class Machine(MachineBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True
