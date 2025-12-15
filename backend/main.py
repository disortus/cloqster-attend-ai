from contextlib import asynccontextmanager
from routers import auth_route, curator_route, admin_route
from databases.postgres import database
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import subprocess
import asyncio


origins = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "https://localhost:3000",
    "https://127.0.0.1:3000",
]

@asynccontextmanager
async def lifespan(app: FastAPI):
    await database.connect()

    from aicamera.face_db import load_faces
    from aicamera.camera_worker import camera_worker
    from scheduler.loop import scheduler_loop

    await load_faces()

    asyncio.create_task(camera_worker())
    asyncio.create_task(scheduler_loop())
    yield
    await database.disconnect()

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