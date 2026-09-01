import asyncio
import sys
import os

# Add backend directory to PYTHONPATH
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from passlib.context import CryptContext

from app.db.session import async_session, engine, Base
from app.models.user import User
from app.models.worker import Worker
from app.models.machine import Machine

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

async def init_and_seed():
    print("[1/2] Inicializando tablas de la base de datos...")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    print("[OK] Tablas creadas exitosamente.")

    print("[2/2] Poblando datos iniciales (Seed Data)...")
    async with async_session() as session:
        # Check if admin exists
        result = await session.execute(select(User).filter(User.email == "admin@example.com"))
        user = result.scalars().first()
        
        if not user:
            hashed_password = get_password_hash("admin123")
            admin_user = User(
                email="admin@example.com",
                password_hash=hashed_password,
                role="ADMIN",
                is_active=True
            )
            session.add(admin_user)
            print("[USER] Usuario Admin creado: admin@example.com | Password: admin123")
        else:
            print("[USER] Usuario Admin ya existente.")

        # Check workers
        w_res = await session.execute(select(Worker))
        if not w_res.scalars().first():
            workers_data = [
                Worker(id=1, worker_code="W001", full_name="Juan Perez", role_job="Operador LHD", area="Frente Norte 01", is_active=True),
                Worker(id=2, worker_code="W002", full_name="Carlos Gomez", role_job="Supervisión", area="Frente Norte 01", is_active=True),
                Worker(id=3, worker_code="W003", full_name="Maria Torres", role_job="Técnico IoT", area="Galería Principal", is_active=True),
            ]
            session.add_all(workers_data)
            print("[WORKERS] Trabajadores iniciales creados.")

        # Check machines
        m_res = await session.execute(select(Machine))
        if not m_res.scalars().first():
            machines_data = [
                Machine(id=1, machine_code="M001", type="Cargador Subterráneo", model="Scoop LHD-01", status="OPERATING"),
                Machine(id=2, machine_code="M002", type="Transporte Pesado", model="Camión Minero BK-04", status="OPERATING"),
                Machine(id=3, machine_code="M003", type="Perforación", model="Jumbo J-02", status="STOPPED"),
            ]
            session.add_all(machines_data)
            print("[MACHINES] Maquinaria inicial creada.")

        await session.commit()
        print("[EXITO] Base de datos SQLite inicializada y lista.")

if __name__ == "__main__":
    asyncio.run(init_and_seed())
