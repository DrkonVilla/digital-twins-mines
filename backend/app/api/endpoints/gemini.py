from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from app.services.gemini_service import gemini_service
from app.core.security import get_current_user
from app.models.user import User

router = APIRouter()

class AnalyzeRequest(BaseModel):
    alert_level: str
    message: str
    created_at: str
    worker_id: int
    machine_id: int

class ChatRequest(BaseModel):
    message: str

@router.post("/analyze")
async def analyze_event(request: AnalyzeRequest, current_user: User = Depends(get_current_user)):
    try:
        response = await gemini_service.analyze_alert(request.dict())
        return {"analysis": response}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error analizando con IA: {str(e)}")

@router.post("/chat")
async def chat_with_bot(request: ChatRequest, current_user: User = Depends(get_current_user)):
    try:
        response = await gemini_service.chat(request.message)
        return {"reply": response}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error conectando con chatbot: {str(e)}")
