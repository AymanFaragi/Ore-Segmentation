import asyncio
import base64
import io
import logging

import cv2
from PIL import Image

from backend import config
from backend.api.ws_manager import STREAM_STATUS_ACTIVE, STREAM_STATUS_DOWN, manager
from backend.sam.inference import SamInference
from backend.storage.stats_writer import StatsWriter
from backend.video_capture.video_capture import VideoCapture

static_img = cv2.imread("assets/test111.png")


# Helper functions
async def add_base64_image(result, frame):
    if "image" not in result:
        img = Image.fromarray(frame)
        buffered = io.BytesIO()
        img.save(buffered, format="JPEG")
        img_str = base64.b64encode(buffered.getvalue()).decode()
        result["image"] = f"data:image/jpeg;base64,{img_str}"
    return result


# Initialize global components
stats_writer = StatsWriter()
sam_inference = SamInference()
video_capture = VideoCapture()


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

        stats_writer.append_run(result)

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
