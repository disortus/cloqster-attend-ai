from fastapi import APIRouter, WebSocket, Depends
from auth.utils import get_current_user
from ws.redis_pubsub import subscribe
import json

ws_router = APIRouter()


@ws_router.websocket("/ws")
async def ws_attends(ws: WebSocket, user=Depends(get_current_user)):
    await ws.accept()

    role = user["role"]

    if role == "teacher":
        channel = f"teacher_{user['id']}"
    elif role == "curator":
        channel = f"curator_{user['id']}"
    elif role == "admin":
        channel = "admin"
    else:
        await ws.close()
        return

    pubsub = await subscribe(channel)

    try:
        async for message in pubsub.listen():
            if message["type"] == "message":
                await ws.send_text(message["data"])
    except Exception:
        await ws.close()
