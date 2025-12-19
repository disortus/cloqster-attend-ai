from fastapi import APIRouter, WebSocket, Depends
from broadcaster import Broadcast
from auth.utils import get_current_user

broadcast = Broadcast("redis://localhost:6379")
ws_router = APIRouter()

@ws_router.on_event("startup")
async def startup():
    await broadcast.connect()

@ws_router.websocket("/ws")
async def websocket_endpoint(ws: WebSocket, user=Depends(get_current_user)):
    await ws.accept()

    role = user["role"]

    # подписка на канал по роли
    if role == "admin":
        channel = "admin"

    elif role == "curator":
        channel = f"curator_{user['group_id']}"

    elif role == "teacher":
        channel = f"teacher_{user['lesson_id']}"

    else:
        await ws.close()
        return

    async with broadcast.subscribe(channel) as subscriber:
        async for event in subscriber:
            await ws.send_text(event.message)