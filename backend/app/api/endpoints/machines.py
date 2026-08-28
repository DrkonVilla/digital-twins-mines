from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.api.deps import get_db, get_current_user
from app.models.machine import Machine
from app.schemas.machine import Machine as MachineSchema, MachineCreate

router = APIRouter()

@router.get("/", response_model=List[MachineSchema])
async def read_machines(
    db: AsyncSession = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    current_user = Depends(get_current_user),
) -> Any:
    result = await db.execute(select(Machine).offset(skip).limit(limit))
    machines = result.scalars().all()
    return machines

@router.post("/", response_model=MachineSchema)
async def create_machine(
    *,
    db: AsyncSession = Depends(get_db),
    machine_in: MachineCreate,
    current_user = Depends(get_current_user),
) -> Any:
    result = await db.execute(select(Machine).filter(Machine.machine_code == machine_in.machine_code))
    if result.scalars().first():
        raise HTTPException(status_code=400, detail="Machine code already exists.")
    
    machine = Machine(**machine_in.model_dump())
    db.add(machine)
    await db.commit()
    await db.refresh(machine)
    return machine

@router.get("/{machine_id}", response_model=MachineSchema)
async def read_machine(
    *,
    db: AsyncSession = Depends(get_db),
    machine_id: int,
    current_user = Depends(get_current_user),
) -> Any:
    result = await db.execute(select(Machine).filter(Machine.id == machine_id))
    machine = result.scalars().first()
    if not machine:
        raise HTTPException(status_code=404, detail="Machine not found")
    return machine
