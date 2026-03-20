from fastapi import APIRouter
from app.sender.sender import router as sender_router
from app.viewer.viewer import router as viewer_router
from app.ws.websocket import router as ws_router

router = APIRouter()
router.include_router(sender_router)
router.include_router(viewer_router)
router.include_router(ws_router)