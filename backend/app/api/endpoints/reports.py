import os
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel
from app.services.report_generator import report_generator
from app.core.security import get_current_user
from app.models.user import User

router = APIRouter()

@router.post("")
async def create_report(current_user: User = Depends(get_current_user)):
    try:
        filepath = await report_generator.generate_pdf_report()
        filename = os.path.basename(filepath)
        return {"message": "Reporte generado", "filename": filename}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generando reporte: {str(e)}")

@router.get("/{filename}/download")
async def download_report(filename: str, current_user: User = Depends(get_current_user)):
    filepath = os.path.join(report_generator.output_dir, filename)
    if not os.path.exists(filepath):
        raise HTTPException(status_code=404, detail="Reporte no encontrado")
    
    return FileResponse(path=filepath, filename=filename, media_type='application/pdf')
