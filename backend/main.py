from contextlib import asynccontextmanager
from routers.auth_route import auth_router
from databases.postgres import database
from fastapi import FastAPI
import subprocess


@asynccontextmanager
async def lifespan(app: FastAPI):
    await database.connect()
    yield
    await database.disconnect()

app = FastAPI(lifespan=lifespan)
app.include_router(auth_router)

if __name__ == "__main__":
    subprocess.run([
        "uvicorn",
        "main:app",
        "--host", "localhost",
        "--port", "3000",
        "--reload"
    ])