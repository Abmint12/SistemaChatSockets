"""
Configuración de la base de datos.

Usa SQLite por defecto (ideal para desarrollo y demos). Si se define la
variable de entorno DATABASE_URL (por ejemplo, la que provee Render con
PostgreSQL), la usa automáticamente. Esto permite desplegar sin cambiar código.
"""
import os

from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

# Render entrega la URL de Postgres como "postgres://...". SQLAlchemy 2.x
# exige el prefijo "postgresql://", por eso lo normalizamos.
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./chat.db")
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

# check_same_thread solo aplica a SQLite (necesario para FastAPI + WebSockets).
connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}

engine = create_engine(DATABASE_URL, connect_args=connect_args, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    """Dependencia de FastAPI: entrega una sesión y la cierra al terminar."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
