from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.api.deps import get_db, get_current_user
from app.models.worker import Worker
from app.schemas.worker import Worker as WorkerSchema, WorkerCreate

router = APIRouter()

@router.get("/", response_model=List[WorkerSchema])
async def read_workers(
    db: AsyncSession = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    current_user = Depends(get_current_user),
) -> Any:
    result = await db.execute(select(Worker).offset(skip).limit(limit))
    workers = result.scalars().all()
    return workers

@router.post("/", response_model=WorkerSchema)
async def create_worker(
    *,
    db: AsyncSession = Depends(get_db),
    worker_in: WorkerCreate,
    current_user = Depends(get_current_user),
) -> Any:
    # Check if worker code exists
    result = await db.execute(select(Worker).filter(Worker.worker_code == worker_in.worker_code))
    if result.scalars().first():
        raise HTTPException(status_code=400, detail="Worker code already exists.")
    
    worker = Worker(**worker_in.model_dump())
    db.add(worker)
    await db.commit()
    await db.refresh(worker)
    return worker

@router.get("/{worker_id}", response_model=WorkerSchema)
async def read_worker(
    *,
    db: AsyncSession = Depends(get_db),
    worker_id: int,
    current_user = Depends(get_current_user),
) -> Any:
    result = await db.execute(select(Worker).filter(Worker.id == worker_id))
    worker = result.scalars().first()
    if not worker:
        raise HTTPException(status_code=404, detail="Worker not found")
    return worker
