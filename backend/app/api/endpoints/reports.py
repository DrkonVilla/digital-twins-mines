import os
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query, Request
from fastapi.responses import FileResponse
from jose import jwt, JWTError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.services.report_generator import report_generator
from app.core.security import get_current_user
from app.core.config import settings
from app.api.deps import get_db
from app.models.user import User

router = APIRouter()

async def get_user_for_download(
    request: Request,
    token: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db)
) -> Optional[User]:
    auth_header = request.headers.get("Authorization")
    auth_token = None
    if auth_header and auth_header.startswith("Bearer "):
        auth_token = auth_header.split(" ")[1]
    elif token:
        auth_token = token

    if not auth_token:
        return None
    
    try:
        payload = jwt.decode(auth_token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            return None
        result = await db.execute(select(User).filter(User.email == username))
        user = result.scalars().first()
        return user
    except JWTError:
        return None

@router.post("")
async def create_report(
    format: str = Query("pdf", description="Report format: pdf, excel, or word"),
    current_user: User = Depends(get_current_user)
):
    try:
        filepath = await report_generator.generate(fmt=format)
        filename = os.path.basename(filepath)
        return {"message": "Reporte generado", "filename": filename, "format": format}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generando reporte: {str(e)}")

@router.get("/{filename}/download")
async def download_report(
    filename: str,
    current_user: Optional[User] = Depends(get_user_for_download)
):
    filepath = os.path.join(report_generator.output_dir, filename)
    if not os.path.exists(filepath):
        raise HTTPException(status_code=404, detail="Reporte no encontrado")
    
    media_type = "application/pdf"
    if filename.endswith(".xlsx"):
        media_type = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    elif filename.endswith(".docx"):
        media_type = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"

    return FileResponse(path=filepath, filename=filename, media_type=media_type)

