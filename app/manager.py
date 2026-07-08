"""
Gestor de conexiones WebSocket.

El ConnectionManager es el corazón del chat en tiempo real: mantiene el
registro de todos los clientes conectados y se encarga de reenviar
(broadcast) los mensajes a todos ellos. Un mismo usuario puede tener varias
pestañas abiertas, por eso agrupamos las conexiones por nombre de usuario.
"""
from typing import Dict, List, Set

from fastapi import WebSocket


class ConnectionManager:
    def __init__(self) -> None:
        # username -> conjunto de WebSockets activos de ese usuario
        self.active: Dict[str, Set[WebSocket]] = {}

    async def connect(self, websocket: WebSocket, username: str) -> None:
        await websocket.accept()
        self.active.setdefault(username, set()).add(websocket)

    def disconnect(self, websocket: WebSocket, username: str) -> None:
        conns = self.active.get(username)
        if conns:
            conns.discard(websocket)
            if not conns:
                self.active.pop(username, None)

    def online_users(self) -> List[str]:
        """Lista ordenada de usuarios conectados en este momento."""
        return sorted(self.active.keys())

    async def send_personal(self, message: dict, websocket: WebSocket) -> None:
        await websocket.send_json(message)

    async def broadcast(self, message: dict) -> None:
        """Envía un mensaje a todas las conexiones activas."""
        dead: List[tuple] = []
        for username, conns in list(self.active.items()):
            for ws in list(conns):
                try:
                    await ws.send_json(message)
                except Exception:
                    dead.append((ws, username))
        # Limpiamos conexiones que fallaron al enviar.
        for ws, username in dead:
            self.disconnect(ws, username)


manager = ConnectionManager()
