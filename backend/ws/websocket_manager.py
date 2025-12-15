from fastapi import WebSocket
from typing import Dict, List

GROUP_CONNECTIONS: Dict[int, List[WebSocket]] = {}

async def connect(group_id: int, websocket: WebSocket):
    await websocket.accept()
    if group_id not in GROUP_CONNECTIONS:
        GROUP_CONNECTIONS[group_id] = []
    GROUP_CONNECTIONS[group_id].append(websocket)

async def disconnect(group_id: int, websocket: WebSocket):
    if group_id in GROUP_CONNECTIONS and websocket in GROUP_CONNECTIONS[group_id]:
        GROUP_CONNECTIONS[group_id].remove(websocket)

async def notify_group(group_id: int, data: dict):
    if group_id not in GROUP_CONNECTIONS:
        return
    for ws in GROUP_CONNECTIONS[group_id]:
        try:
            await ws.send_json(data)
        except:
            pass
