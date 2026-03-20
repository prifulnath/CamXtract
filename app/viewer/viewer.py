import os
from fastapi import APIRouter
from fastapi.responses import FileResponse

router = APIRouter()
current_dir = os.path.dirname(os.path.abspath(__file__))

@router.get("/viewer.html")
async def get_viewer_page():
    html_path = os.path.join(current_dir, "viewer.html")
    return FileResponse(html_path)

@router.get("/static/viewer.js")
async def get_viewer_js():
    js_path = os.path.join(current_dir, "viewer.js")
    return FileResponse(js_path, media_type="application/javascript")