from fastapi import WebSocket
from typing import Dict, Set

class ConnectionManager:
    def __init__(self):
        # Все подключения по ролям и ID
        self.admin_connections: Set[WebSocket] = set()
        self.curator_connections: Dict[int, Set[WebSocket]] = {}  # curator_user_id -> set of websockets
        self.teacher_connections: Set[WebSocket] = set()  # учителя видят текущий урок, но проще — все активные

    async def connect(self, websocket: WebSocket, user_id: int, role: str, group_id: int = None):
        await websocket.accept()
        if role == "admin":
            self.admin_connections.add(websocket)
        elif role == "curator":
            if user_id not in self.curator_connections:
                self.curator_connections[user_id] = set()
            self.curator_connections[user_id].add(websocket)
        elif role == "teacher":
            self.teacher_connections.add(websocket)

    def disconnect(self, websocket: WebSocket, user_id: int, role: str):
        if role == "admin":
            self.admin_connections.discard(websocket)
        elif role == "curator":
            if user_id in self.curator_connections:
                self.curator_connections[user_id].discard(websocket)
                if not self.curator_connections[user_id]:
                    del self.curator_connections[user_id]
        elif role == "teacher":
            self.teacher_connections.discard(websocket)

    async def broadcast_to_admins(self, message: dict):
        for conn in self.admin_connections.copy():
            try:
                await conn.send_json(message)
            except:
                self.admin_connections.discard(conn)

    async def broadcast_to_curator(self, curator_id: int, message: dict):
        if curator_id in self.curator_connections:
            for conn in self.curator_connections[curator_id].copy():
                try:
                    await conn.send_json(message)
                except:
                    self.curator_connections[curator_id].discard(conn)

    async def broadcast_to_teachers(self, message: dict):
        for conn in self.teacher_connections.copy():
            try:
                await conn.send_json(message)
            except:
                self.teacher_connections.discard(conn)

manager = ConnectionManager()