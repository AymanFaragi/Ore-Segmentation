import asyncio
import base64
import io
import logging
from contextlib import asynccontextmanager
from typing import Any, Dict, List


import cv2
static_img = cv2.imread("assets/test111.png")


import uvicorn
from fastapi import FastAPI, Form, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from PIL import Image
from starlette.websockets import WebSocketState

from backend import config
from backend.constants import CONFIG_YAML_PATH
from backend.sam.inference import SamInference
from backend.video_capture.video_capture import VideoCapture

# Setup logging
logging.getLogger("multipart").setLevel(logging.INFO)
logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
logging.basicConfig(level=logging.INFO)

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


# Helper functions
async def add_base64_image(result, frame):
    if "image" not in result:
        img = Image.fromarray(frame)
        buffered = io.BytesIO()
        img.save(buffered, format="JPEG")
        img_str = base64.b64encode(buffered.getvalue()).decode()
        result["image"] = f"data:image/jpeg;base64,{img_str}"
    return result


# Application setup function
def setup_app():
    app = FastAPI(lifespan=lifespan)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=config["frontend"]["allow_origins"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    return app


# Core inference function
async def perform_inference(
    sieve_width_cm: float = None,
    sieve_height_cm: float = None,
    broadcast: bool = False,
):
    try:
        if sieve_width_cm is None:
            sieve_width_cm = config["sieve_dimensions"]["width_cm"]
        if sieve_height_cm is None:
            sieve_height_cm = config["sieve_dimensions"]["height_cm"]

        params = {"sieve_width_cm": sieve_width_cm, "sieve_height_cm": sieve_height_cm}

        def capture_and_infer():
            frame = static_img.copy()
            if params != sam_inference.get_current_params():
                sam_inference.update_params(**params)
            return frame, sam_inference.run(frame)

        # def capture_and_infer():
        #     frame = video_capture.capture_single()
        #     if params != sam_inference.get_current_params():
        #         sam_inference.update_params(**params)
        #     return frame, sam_inference.run(frame) 

     


        try:
            frame, result = await asyncio.to_thread(capture_and_infer)
        except Exception as e:
            logging.error(f"VideoCapture error: {str(e)}")
            manager.stream_status = STREAM_STATUS_DOWN
            await manager.broadcast({"status": STREAM_STATUS_DOWN, "message": str(e)})
            return None

        if frame is None:
            msg = "Video source returned empty frame"
            logging.error(msg)
            manager.stream_status = STREAM_STATUS_DOWN
            await manager.broadcast({"status": STREAM_STATUS_DOWN, "message": msg})
            return None

        result["status"] = STREAM_STATUS_ACTIVE
        result = await add_base64_image(result, frame)

        if broadcast:
            await manager.broadcast(result)

        return result

    except Exception as e:
        logging.error(f"Error during inference: {str(e)}")
        raise e


# Background task
async def run_inference_loop():
    interval_seconds = config["inference"]["interval_seconds"]
    logging.info(f"Starting automatic inference loop every {interval_seconds} seconds")
    try:
        while True:
            try:
                logging.info("Running periodic inference")
                await perform_inference(broadcast=True)
                client_count = len(manager.active_connections)
                if client_count > 0:
                    logging.info(
                        f"Broadcast inference result to {client_count} clients"
                    )
            except Exception as e:
                logging.error(f"Error in inference loop: {str(e)}")
            await asyncio.sleep(interval_seconds)
    except asyncio.CancelledError:
        logging.info("Inference loop task was cancelled")
        raise


# Application lifespan
@asynccontextmanager
async def lifespan(app: FastAPI):
    global inference_task
    inference_task = asyncio.create_task(run_inference_loop())
    logging.info("Started background inference task")
    yield
    if inference_task:
        inference_task.cancel()
        try:
            await inference_task
        except asyncio.CancelledError:
            logging.info("Background inference task cancelled")


# Initialize global components
inference_task = None
sam_inference = SamInference()
app = setup_app()
video_capture = VideoCapture()
manager = WsConnectionManager()


# API Endpoints
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket)
    except Exception as e:
        logging.error(f"WebSocket error: {str(e)}")
        manager.disconnect(websocket)


@app.get("/dimensions/")
async def get_dimensions():
    try:
        width_cm = config["sieve_dimensions"]["width_cm"]
        height_cm = config["sieve_dimensions"]["height_cm"]

        return JSONResponse(
            {
                "dimensions": {
                    "width_cm": width_cm,
                    "height_cm": height_cm,
                },
            },
            200,
        )
    except Exception as e:
        logging.error(f"Get dimensions error: {str(e)}")
        return JSONResponse({"status": "error", "message": str(e)}, 500)


@app.post("/update_dimensions/")
async def update_dimensions(
    sieve_width_cm: float = Form(...), sieve_height_cm: float = Form(...)
):
    try:
        if sieve_width_cm <= 0 or sieve_height_cm <= 0:
            return JSONResponse(
                {"status": "error", "message": "Dimensions must be positive"}, 400
            )

        # Update in-memory config
        config["sieve_dimensions"]["width_cm"] = sieve_width_cm
        config["sieve_dimensions"]["height_cm"] = sieve_height_cm

        try:
            # Read existing config file as text to preserve comments and format
            with open(CONFIG_YAML_PATH, "r") as f:
                config_lines = f.readlines()

            # Look for the lines containing the width and height values and update them
            width_pattern = "  width_cm:"
            height_pattern = "  height_cm:"

            for i, line in enumerate(config_lines):
                if width_pattern in line:
                    config_lines[i] = f"  width_cm: {sieve_width_cm}\n"
                elif height_pattern in line:
                    config_lines[i] = f"  height_cm: {sieve_height_cm}\n"

            # Write the modified content back to the file
            with open(CONFIG_YAML_PATH, "w") as f:
                f.writelines(config_lines)

            logging.info(
                f"Updated config.yaml with new dimensions: {sieve_width_cm}x{sieve_height_cm}cm"
            )
        except Exception as yaml_error:
            logging.error(f"Failed to update config.yaml: {str(yaml_error)}")
            # Continue execution - we've already updated the in-memory config

        logging.info(f"Updated dimensions: {sieve_width_cm}x{sieve_height_cm}cm")
        return JSONResponse(
            {
                "status": "success",
                "dimensions": {
                    "width_cm": sieve_width_cm,
                    "height_cm": sieve_height_cm,
                },
            },
            200,
        )
    except Exception as e:
        logging.error(f"Update dimensions error: {str(e)}")
        return JSONResponse({"status": "error", "message": str(e)}, 500)


# Main entry point
if __name__ == "__main__":
    uvicorn.run(
        "backend.api.server:app",
        host=config["app"]["host"],
        port=config["app"]["port"],
        log_level="info",
        reload=True,
    )
