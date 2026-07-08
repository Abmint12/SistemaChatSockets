"""
Aplicación principal.

Une todas las piezas:
- API REST para registro e inicio de sesión (devuelve un JWT).
- Endpoint WebSocket /ws para el chat en tiempo real, protegido por token.
- Sirve el frontend estático (login y sala de chat).
"""
import time
from datetime import datetime, timezone
from pathlib import Path

from fastapi import (Depends, FastAPI, HTTPException, WebSocket,
                     WebSocketDisconnect, status)
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session

from . import auth, models, schemas
from .database import Base, SessionLocal, engine, get_db
from .manager import manager

# Crea las tablas si no existen.
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Chat en Tiempo Real", version="1.0.0")

# CORS: permitimos el propio origen. En un despliegue real se restringe
# a los dominios necesarios.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

BASE_DIR = Path(__file__).resolve().parent.parent
STATIC_DIR = BASE_DIR / "static"
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

# Anti-spam sencillo: máximo de mensajes por ventana de tiempo por conexión.
RATE_LIMIT_MSGS = 8
RATE_LIMIT_WINDOW = 5.0  # segundos
MAX_MESSAGE_LEN = 1000
HISTORY_LIMIT = 30


# --- Rutas del frontend ----------------------------------------------------
@app.get("/")
def index():
    return FileResponse(STATIC_DIR / "index.html")


@app.get("/chat")
def chat_page():
    return FileResponse(STATIC_DIR / "chat.html")


@app.get("/health")
def health():
    """Endpoint de salud usado por la plataforma de despliegue."""
    return {"status": "ok"}


# --- API REST: autenticación ----------------------------------------------
@app.post("/api/register", response_model=schemas.Token, status_code=201)
def register(data: schemas.UserCreate, db: Session = Depends(get_db)):
    if db.query(models.User).filter(models.User.username == data.username).first():
        raise HTTPException(status_code=400, detail="El usuario ya existe.")
    if db.query(models.User).filter(models.User.email == data.email).first():
        raise HTTPException(status_code=400, detail="El correo ya está registrado.")

    user = models.User(
        username=data.username,
        email=data.email,
        hashed_password=auth.hash_password(data.password),
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    token = auth.create_access_token(user.username)
    return schemas.Token(access_token=token, username=user.username)


@app.post("/api/login", response_model=schemas.Token)
def login(data: schemas.UserLogin, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.username == data.username).first()
    if not user or not auth.verify_password(data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuario o contraseña incorrectos.",
        )
    token = auth.create_access_token(user.username)
    return schemas.Token(access_token=token, username=user.username)


# --- Utilidades del WebSocket ---------------------------------------------
def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _recent_history(db: Session):
    rows = (
        db.query(models.Message)
        .order_by(models.Message.id.desc())
        .limit(HISTORY_LIMIT)
        .all()
    )
    rows.reverse()
    return [
        {
            "type": "message",
            "username": r.username,
            "content": r.content,
            "timestamp": r.created_at.replace(tzinfo=timezone.utc).isoformat(),
        }
        for r in rows
    ]


# --- Endpoint WebSocket ----------------------------------------------------
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket, token: str = ""):
    # 1) Autenticación en el handshake: el token viaja como query param.
    username = auth.decode_access_token(token)
    if not username:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        return

    # 2) Registramos la conexión y avisamos a la sala.
    await manager.connect(websocket, username)
    db = SessionLocal()
    try:
        # Historial reciente solo para el que acaba de entrar.
        await manager.send_personal({"type": "history", "messages": _recent_history(db)}, websocket)
        # Lista de conectados actualizada para todos.
        await manager.broadcast({"type": "users", "users": manager.online_users()})
        await manager.broadcast({
            "type": "system",
            "content": f"{username} se unió al chat",
            "timestamp": _now_iso(),
        })

        timestamps: list[float] = []
        while True:
            data = await websocket.receive_json()
            msg_type = data.get("type", "message")

            if msg_type == "typing":
                await manager.broadcast({"type": "typing", "username": username})
                continue

            if msg_type == "message":
                content = (data.get("content") or "").strip()
                if not content:
                    continue
                if len(content) > MAX_MESSAGE_LEN:
                    content = content[:MAX_MESSAGE_LEN]

                # Control anti-spam por ventana deslizante.
                now = time.monotonic()
                timestamps = [t for t in timestamps if now - t < RATE_LIMIT_WINDOW]
                if len(timestamps) >= RATE_LIMIT_MSGS:
                    await manager.send_personal(
                        {"type": "system", "content": "Estás enviando mensajes muy rápido.",
                         "timestamp": _now_iso()},
                        websocket,
                    )
                    continue
                timestamps.append(now)

                # Guardamos en el historial y reenviamos a todos.
                db.add(models.Message(username=username, content=content))
                db.commit()
                await manager.broadcast({
                    "type": "message",
                    "username": username,
                    "content": content,
                    "timestamp": _now_iso(),
                })
    except WebSocketDisconnect:
        pass
    finally:
        manager.disconnect(websocket, username)
        db.close()
        await manager.broadcast({"type": "users", "users": manager.online_users()})
        await manager.broadcast({
            "type": "system",
            "content": f"{username} salió del chat",
            "timestamp": _now_iso(),
        })
