import logging
from typing import Any, Dict, List

from fastapi import WebSocket
from starlette.websockets import WebSocketState

# Constants
STREAM_STATUS_STARTING = "starting"
STREAM_STATUS_ACTIVE = "active"
STREAM_STATUS_DOWN = "down"


# WebSocket Connection Manager
class WsConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []
        self.latest_result: Dict[str, Any] = None
        self.stream_status: str = STREAM_STATUS_STARTING

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        logging.info(
            f"WebSocket client connected. Total clients: {len(self.active_connections)}"
        )

        if self.stream_status == STREAM_STATUS_ACTIVE and self.latest_result:
            payload = self.latest_result
        elif self.stream_status == STREAM_STATUS_DOWN:
            payload = {
                "status": STREAM_STATUS_DOWN,
                "message": "Video source unavailable; please try later.",
            }
        else:
            payload = {
                "status": STREAM_STATUS_STARTING,
                "message": "Stream initializing — please wait a moment.",
            }

        await websocket.send_json(payload)

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
            logging.info(
                f"WebSocket client disconnected. Remaining clients: {len(self.active_connections)}"
            )

    async def broadcast(self, message: Dict[str, Any]):
        self.latest_result = message
        self.stream_status = message.get("status", STREAM_STATUS_STARTING)
        disconnected_clients = []
        for connection in self.active_connections:
            try:
                if connection.client_state == WebSocketState.CONNECTED:
                    await connection.send_json(message)
            except Exception as e:
                logging.error(f"Failed to send message to client: {str(e)}")
                disconnected_clients.append(connection)
        for client in disconnected_clients:
            self.disconnect(client)
        return len(self.active_connections)


# Shared singleton — the same connection manager instance is used by the
# inference loop (to broadcast results) and the /ws route (to register and
# drop clients). Kept as a module-level global here, same pattern as the
# other singletons (stats_writer, sam_inference) in inference_loop.py.
manager = WsConnectionManager()
