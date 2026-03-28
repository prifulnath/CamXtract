import json
import asyncio
import time
import uuid
import pathlib
from typing import Optional
from fastapi import WebSocket


CONFIG_PATH = pathlib.Path("camxtract_config.json")


def _load_config() -> dict:
    try:
        return json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
    except Exception:
        return {}


def _inactivity_timeout_seconds() -> int:
    try:
        raw = _load_config().get("INACTIVITY TIMEOUT", "5 Minutes")
        parts = raw.split()
        minutes = int(parts[0]) if parts[0].isdigit() else 5
        return minutes * 60
    except Exception:
        return 300


def _max_viewers() -> int:
    try:
        return int(_load_config().get("MAX VIEWERS", 12))
    except Exception:
        return 12


class ConnectionManager:
    def __init__(self):
        self.active_sender: Optional[WebSocket] = None
        self.waiting_senders: list[WebSocket] = []

        # Viewers: socket ↔ viewer_id  (bi-directional lookup)
        self.viewers: list[WebSocket] = []
        self.viewer_ids: dict[WebSocket, str] = {}    # ws → id
        self.viewer_sockets: dict[str, WebSocket] = {}  # id → ws

        self.gui_clients: list[WebSocket] = []
        self.last_activity: dict[WebSocket, float] = {}

    # ── Connection lifecycle ────────────────────────────────────────────────

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.last_activity[websocket] = time.monotonic()

    async def disconnect(self, websocket: WebSocket):
        self.last_activity.pop(websocket, None)

        if websocket == self.active_sender:
            self.active_sender = None
            if self.waiting_senders:
                next_sender = self.waiting_senders.pop(0)
                self.active_sender = next_sender
                try:
                    await next_sender.send_text(json.dumps({"type": "start_sending"}))
                except Exception:
                    pass
        elif websocket in self.waiting_senders:
            self.waiting_senders.remove(websocket)
        elif websocket in self.viewers:
            viewer_id = self.viewer_ids.pop(websocket, None)
            self.viewer_sockets.pop(viewer_id, None)
            self.viewers.remove(websocket)
            # Notify sender that this viewer left
            if viewer_id and self.active_sender:
                try:
                    await self.active_sender.send_text(
                        json.dumps({"type": "viewer_left", "viewer_id": viewer_id})
                    )
                except Exception:
                    pass
        elif websocket in self.gui_clients:
            self.gui_clients.remove(websocket)

    # ── Message handling ────────────────────────────────────────────────────

    async def handle_message(self, websocket: WebSocket, text_data: str):
        self.last_activity[websocket] = time.monotonic()

        try:
            data = json.loads(text_data)
        except json.JSONDecodeError:
            return

        msg_type = data.get("type")

        # ── Ping / Pong ────────────────────────────────────────────────────

        if msg_type == "ping":
            try:
                await websocket.send_text(json.dumps({"type": "pong"}))
            except Exception:
                pass
            return

        if msg_type == "pong":
            return

        # ── Registration ───────────────────────────────────────────────────

        if msg_type == "register_sender":
            if self.active_sender is not None and self.active_sender != websocket:
                self.waiting_senders.append(websocket)
                await websocket.send_text(json.dumps({
                    "type": "wait",
                    "message": "Camera is currently in use by another device. "
                               "You will be connected automatically when they leave."
                }))
                return
            self.active_sender = websocket
            await websocket.send_text(json.dumps({"type": "start_sending"}))
            return

        if msg_type == "register_viewer":
            # Enforce MAX VIEWERS limit
            if len(self.viewers) >= _max_viewers():
                await websocket.send_text(json.dumps({
                    "type": "rejected",
                    "message": f"Maximum viewers ({_max_viewers()}) reached. Try again later."
                }))
                return

            viewer_id = str(uuid.uuid4())
            self.viewers.append(websocket)
            self.viewer_ids[websocket] = viewer_id
            self.viewer_sockets[viewer_id] = websocket

            # Confirm ID to the viewer
            await websocket.send_text(json.dumps({
                "type": "viewer_registered",
                "viewer_id": viewer_id
            }))

            # Notify sender — it will create a dedicated RTCPeerConnection for this viewer
            if self.active_sender:
                try:
                    await self.active_sender.send_text(json.dumps({
                        "type": "viewer_joined",
                        "viewer_id": viewer_id
                    }))
                except Exception:
                    pass
            return

        if msg_type == "register_gui":
            if websocket not in self.gui_clients:
                self.gui_clients.append(websocket)
            return

        # ── Camera Remote Controls ─────────────────────────────────────────

        if msg_type == "camera_control":
            if websocket in self.viewers or websocket in self.gui_clients:
                if self.active_sender:
                    try:
                        await self.active_sender.send_text(text_data)
                    except Exception:
                        pass
            return

        # ── WebRTC Signalling — Sender → specific Viewer ───────────────────

        if websocket == self.active_sender:
            viewer_id = data.get("viewer_id")
            if viewer_id:
                # Addressed to a specific viewer
                target = self.viewer_sockets.get(viewer_id)
                if target:
                    try:
                        await target.send_text(text_data)
                    except Exception:
                        pass
            else:
                # Broadcast (legacy / fallback)
                for viewer in list(self.viewers):
                    try:
                        await viewer.send_text(text_data)
                    except Exception:
                        pass
            return

        # ── WebRTC Signalling — Viewer → Sender ───────────────────────────

        if websocket in self.viewers:
            if self.active_sender:
                # Stamp the viewer's ID so the sender can route to the right PC
                my_id = self.viewer_ids.get(websocket)
                if my_id and "viewer_id" not in data:
                    data["viewer_id"] = my_id
                try:
                    await self.active_sender.send_text(json.dumps(data))
                except Exception:
                    pass
            return

    # ── Background tasks ───────────────────────────────────────────────────

    async def heartbeat(self):
        while True:
            await asyncio.sleep(5)
            all_clients = [
                self.active_sender,
                *self.waiting_senders,
                *self.viewers,
                *self.gui_clients,
            ]
            for ws in all_clients:
                if ws is None:
                    continue
                try:
                    await ws.send_text(json.dumps({"type": "ping"}))
                except Exception:
                    await self.disconnect(ws)

    async def inactivity_watcher(self):
        while True:
            await asyncio.sleep(30)
            timeout = _inactivity_timeout_seconds()
            now = time.monotonic()
            stale = [ws for ws, t in list(self.last_activity.items())
                     if now - t > timeout]
            for ws in stale:
                try:
                    await ws.send_text(json.dumps({
                        "type": "timeout",
                        "message": "Connection closed due to inactivity."
                    }))
                    await ws.close()
                except Exception:
                    pass
                await self.disconnect(ws)
