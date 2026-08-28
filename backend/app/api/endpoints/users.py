from fastapi import APIRouter, Depends
from app.core.security import get_current_user
from app.models.user import User

router = APIRouter()

@router.get("/me")
async def get_current_user_profile(current_user: User = Depends(get_current_user)):
    return {
        "id": current_user.id,
        "email": current_user.email,
        "role": current_user.role,
        "is_active": current_user.is_active,
    }
