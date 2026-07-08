"""
Modelos ORM de la aplicación.

- User: usuarios registrados. La contraseña NUNCA se guarda en texto plano,
  solo su hash (ver auth.py).
- Message: historial de mensajes del chat, para poder mostrar los últimos
  mensajes cuando un usuario se conecta.
"""
from datetime import datetime, timezone

from sqlalchemy import Column, DateTime, Integer, String, Text

from .database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(30), unique=True, index=True, nullable=False)
    email = Column(String(120), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))


class Message(Base):
    __tablename__ = "messages"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(30), index=True, nullable=False)
    content = Column(Text, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
