import asyncio
from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.router import router
from app.ws.websocket import manager


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Start background maintenance tasks
    heartbeat_task = asyncio.create_task(manager.heartbeat())
    inactivity_task = asyncio.create_task(manager.inactivity_watcher())
    yield
    # Graceful shutdown
    heartbeat_task.cancel()
    inactivity_task.cancel()


app = FastAPI(lifespan=lifespan)
app.include_router(router)