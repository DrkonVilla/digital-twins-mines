from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class AlertBase(BaseModel):
    interaction_id: int
    alert_level: str
    message: str
    status: Optional[str] = "NEW"

class AlertCreate(AlertBase):
    pass

class Alert(AlertBase):
    id: int
    acknowledged_by: Optional[int] = None
    acknowledged_at: Optional[datetime] = None
    created_at: datetime

    class Config:
        from_attributes = True
