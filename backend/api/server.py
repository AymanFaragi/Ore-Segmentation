import asyncio
import logging
from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware

from backend import config
from backend.api.inference_loop import run_inference_loop
from backend.api.routes_dimensions import router as dimensions_router
from backend.api.ws_manager import manager

# Setup logging
logging.getLogger("multipart").setLevel(logging.INFO)
logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
logging.basicConfig(level=logging.INFO)


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
app = setup_app()
app.include_router(dimensions_router)


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


# Main entry point
if __name__ == "__main__":
    uvicorn.run(
        "backend.api.server:app",
        host=config["app"]["host"],
        port=config["app"]["port"],
        log_level="info",
        reload=True,
    )
