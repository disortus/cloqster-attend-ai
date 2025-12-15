from contextlib import asynccontextmanager
from routers import auth_route, curator_route, admin_route
from databases.postgres import database
from fastapi import FastAPI, WebSocket
from fastapi.middleware.cors import CORSMiddleware
import subprocess
import asyncio
import ws.manager as manager_module

manager = manager_module.manager

origins = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "https://localhost:3000",
    "https://127.0.0.1:3000",
]

@asynccontextmanager
async def lifespan(app: FastAPI):
    await database.connect()

    from scheduler.loop import scheduler_loop
    asyncio.create_task(scheduler_loop())
    yield
    await database.disconnect()

@app.websocket("/ws/attendance/{user_id}/{role}")
async def websocket_endpoint(websocket: WebSocket, user_id: int, role: str):
    group_id = None  # если нужно — можно передать
    await manager.connect(websocket, user_id, role, group_id)
    try:
        while True:
            await websocket.receive_text()  # keep-alive
    except:
        manager.disconnect(websocket, user_id, role)

app = FastAPI(lifespan=lifespan)
app.include_router(auth_route.auth_router)
app.include_router(curator_route.cur_router)
app.include_router(admin_route.admin_router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

if __name__ == "__main__":
    subprocess.run([
        "uvicorn",
        "main:app",
        "--host", "localhost",
        "--port", "8000",
        "--reload"
    ])