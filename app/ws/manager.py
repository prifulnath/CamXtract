import json
from typing import Optional
from fastapi import WebSocket

class ConnectionManager:
    def __init__(self):
        self.active_sender: Optional[WebSocket] = None
        self.waiting_senders: list[WebSocket] = []
        self.viewers: list[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()

    async def disconnect(self, websocket: WebSocket):
        if websocket == self.active_sender:
            self.active_sender = None
            # Promote next waiting sender if any
            if self.waiting_senders:
                next_sender = self.waiting_senders.pop(0)
                self.active_sender = next_sender
                try:
                    await next_sender.send_text(json.dumps({"type": "start_sending"}))
                except:
                    pass
        elif websocket in self.waiting_senders:
            self.waiting_senders.remove(websocket)
        elif websocket in self.viewers:
            self.viewers.remove(websocket)

    async def handle_message(self, websocket: WebSocket, text_data: str):
        try:
            data = json.loads(text_data)
        except json.JSONDecodeError:
            return
            
        if data.get("type") == "register_sender":
            if self.active_sender is not None and self.active_sender != websocket:
                self.waiting_senders.append(websocket)
                await websocket.send_text(json.dumps({"type": "wait", "message": "Camera is currently in use by another device. You will be connected automatically when they leave."}))
                return
            self.active_sender = websocket
            await websocket.send_text(json.dumps({"type": "start_sending"}))
            return
            
        if data.get("type") == "register_viewer":
            if websocket not in self.viewers:
                self.viewers.append(websocket)
            return

        # Routine Signaling Routing
        if websocket == self.active_sender:
            for viewer in self.viewers:
                await viewer.send_text(text_data)
        elif websocket in self.viewers:
            if self.active_sender:
                await self.active_sender.send_text(text_data)
