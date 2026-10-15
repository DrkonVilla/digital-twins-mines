import logging
from sqlalchemy import select
import bcrypt

from app.db.base import Base
from app.db.session import engine, async_session
from app.models.user import User
from app.models.worker import Worker
from app.models.machine import Machine

logger = logging.getLogger("m11.init_db")

def get_password_hash(password: str) -> str:
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")

async def init_database():
    """Crea automáticamente las tablas y puebla los datos iniciales si no existen."""
    try:
        logger.info("Verificando / inicializando tablas de base de datos...")
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

        async with async_session() as session:
            # 1. Verificar / Crear Usuario Administrador
            admin_result = await session.execute(select(User).filter(User.email == "admin@example.com"))
            if not admin_result.scalars().first():
                admin_user = User(
                    email="admin@example.com",
                    password_hash=get_password_hash("admin123"),
                    role="ADMIN",
                    is_active=True
                )
                session.add(admin_user)
                logger.info("Admin inicial creado: admin@example.com / admin123")

            # 2. Verificar / Crear Trabajadores
            w_res = await session.execute(select(Worker))
            if not w_res.scalars().first():
                workers_data = [
                    Worker(worker_code="W001", full_name="Juan Perez", role_job="Operador LHD", area="Frente Norte 01", is_active=True),
                    Worker(worker_code="W002", full_name="Carlos Gomez", role_job="Supervisión", area="Frente Norte 01", is_active=True),
                    Worker(worker_code="W003", full_name="Maria Torres", role_job="Técnico IoT", area="Galería Principal", is_active=True),
                ]
                session.add_all(workers_data)
                print("[INIT_DB] Trabajadores iniciales registrados.")

            # 3. Verificar / Crear Maquinaria
            m_res = await session.execute(select(Machine))
            if not m_res.scalars().first():
                machines_data = [
                    Machine(machine_code="M001", type="Cargador Subterráneo", model="Scoop LHD-01", status="OPERATING"),
                    Machine(machine_code="M002", type="Transporte Pesado", model="Camión Minero BK-04", status="OPERATING"),
                    Machine(machine_code="M003", type="Perforación", model="Jumbo J-02", status="STOPPED"),
                ]
                session.add_all(machines_data)
                print("[INIT_DB] Maquinaria inicial registrada.")

            await session.commit()
            print("[INIT_DB] Base de datos lista y sincronizada.")
    except Exception as e:
        print(f"[INIT_DB ERROR] Aviso durante inicializacion de base de datos: {e}")
        logger.warning(f"Aviso durante inicialización de base de datos: {e}")
