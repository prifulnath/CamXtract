import os
from fastapi import APIRouter
from fastapi.responses import FileResponse

router = APIRouter()
current_dir = os.path.dirname(os.path.abspath(__file__))

@router.get("/sender.html")
async def get_sender_page():
    html_path = os.path.join(current_dir, "sender.html")
    return FileResponse(html_path)

@router.get("/static/sender.js")
async def get_sender_js():
    js_path = os.path.join(current_dir, "sender.js")
    return FileResponse(js_path, media_type="application/javascript")