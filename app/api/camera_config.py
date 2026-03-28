from fastapi import APIRouter
from pydantic import BaseModel
import json
import pathlib

CONFIG_PATH = pathlib.Path("camxtract_config.json")
router = APIRouter(prefix="/api")


class CameraConfig(BaseModel):
    resolution: str = "1920x1080"
    preferred_fps: int = 30
    codec_preference: str = "VP9"
    use_ideal: bool = True
    fallback_resolutions: list[str] = ["1280x720", "854x480"]
    zoom: float = 1.0
    exposure_compensation: float = 0.0
    torch: bool = False
    facing_mode: str = "environment"
    max_bitrate_mbps: int = 8


def _load_config() -> dict:
    try:
        return json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
    except Exception:
        return {}


def _save_config(cfg: dict):
    CONFIG_PATH.write_text(json.dumps(cfg, indent=4), encoding="utf-8")


@router.get("/camera-config", response_model=CameraConfig)
def get_camera_config():
    """Return the current camera configuration."""
    cfg = _load_config()
    cam = cfg.get("CAMERA", {})
    return CameraConfig(**cam) if cam else CameraConfig()


@router.put("/camera-config")
def set_camera_config(body: CameraConfig):
    """Persist camera configuration to camxtract_config.json."""
    cfg = _load_config()
    cfg["CAMERA"] = body.model_dump()
    _save_config(cfg)
    return {"status": "saved"}


@router.post("/camera-config/reset")
def reset_camera_config():
    """Reset camera config to factory defaults."""
    defaults = CameraConfig()
    cfg = _load_config()
    cfg["CAMERA"] = defaults.model_dump()
    _save_config(cfg)
    return {"status": "reset", "config": defaults}
