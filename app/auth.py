"""
Seguridad y autenticación.

Dos responsabilidades:
1. Hashear y verificar contraseñas con bcrypt (nunca se guarda texto plano).
2. Crear y validar tokens JWT firmados, usados tanto en la API REST como
   en el handshake del WebSocket.
"""
import os
from datetime import datetime, timedelta, timezone
from typing import Optional

import bcrypt
import jwt

# En producción esta clave DEBE venir de una variable de entorno secreta.
SECRET_KEY = os.getenv("SECRET_KEY", "cambia-esta-clave-en-produccion-por-favor")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "720"))


# --- Contraseñas -----------------------------------------------------------
def hash_password(password: str) -> str:
    """Devuelve el hash bcrypt de una contraseña."""
    # bcrypt trabaja con un máximo de 72 bytes; recortamos por seguridad.
    pwd = password.encode("utf-8")[:72]
    return bcrypt.hashpw(pwd, bcrypt.gensalt()).decode("utf-8")


def verify_password(password: str, hashed: str) -> bool:
    """Compara una contraseña en texto plano con su hash almacenado."""
    try:
        pwd = password.encode("utf-8")[:72]
        return bcrypt.checkpw(pwd, hashed.encode("utf-8"))
    except (ValueError, TypeError):
        return False


# --- Tokens JWT ------------------------------------------------------------
def create_access_token(username: str) -> str:
    """Genera un JWT firmado que identifica al usuario y expira en X minutos."""
    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    payload = {"sub": username, "exp": expire}
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


def decode_access_token(token: str) -> Optional[str]:
    """Valida la firma y expiración del token. Devuelve el usuario o None."""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload.get("sub")
    except jwt.PyJWTError:
        return None
