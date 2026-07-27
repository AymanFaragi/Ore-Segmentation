import logging
import os
import time
from datetime import datetime
from pathlib import Path

import cv2
import numpy as np
import typer
from dotenv import load_dotenv

from backend import config
from backend.constants import CAM_RAW_IMAGES_PATH

# =============== Fetch configurations =================

load_dotenv()

# =============== Default MJPEG Axis URL ====================
CAM_MJPEG_URL = os.environ.get("CAM_MJPEG_URL")
if not CAM_MJPEG_URL:
    raise RuntimeError(
        "CAM_MJPEG_URL environment variable is not set. "
        "Set it in your .env file (never commit real camera credentials)."
    )

# =============== Setup ===============================

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
app = typer.Typer()

# ======================================================


class VideoCapture:
    def __init__(
        self,
        video_source: str = CAM_MJPEG_URL,
        output_dir: Path = CAM_RAW_IMAGES_PATH,
        mode: str = "single",
        interval: int = config["inference"]["interval_seconds"],
    ):
        self.video_source = video_source
        self.output_dir = output_dir
        self.mode = mode
        self.interval = interval
        self.cap = None
        self.fps = None
        self.warmup_frames = 5

        os.makedirs(output_dir, exist_ok=True)

    def start_capture(self):
        logger.info(f"Connecting to video source: {self.video_source}")
        if self.cap:
            self.cap.release()
            self.cap = None

        self.cap = cv2.VideoCapture(self.video_source)

        if not self.cap.isOpened():
            raise RuntimeError(f"Failed to open video source: {self.video_source}")

        logger.info(f"Warming up by discarding {self.warmup_frames} frames")
        for i in range(self.warmup_frames):
            read_success, _ = self.cap.read()
            if not read_success:
                logger.warning(f"Warmup frame {i} failed")
            time.sleep(0.1)

        ret, test_frame = self.cap.read()
        if not ret or test_frame is None:
            raise RuntimeError(
                f"Failed to read frame after warmup from: {self.video_source}"
            )

        self.fps = int(self.cap.get(cv2.CAP_PROP_FPS)) or 15
        width = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        logger.info(f"Connected (FPS: {self.fps}, Resolution: {width}x{height})")

    def stop_capture(self):
        if self.cap:
            self.cap.release()
            self.cap = None

    def capture_frame(self):
        for _ in range(3):
            self.cap.grab()
        ret, frame = self.cap.read()
        if not ret or frame is None:
            raise RuntimeError("Failed to capture frame")
        return cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    def save_frame(self, frame: np.ndarray):
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        file_path = os.path.join(self.output_dir, f"frame_{timestamp}.png")
        cv2.imwrite(file_path, cv2.cvtColor(frame, cv2.COLOR_RGB2BGR))
        logger.info(f"Saved frame to {file_path}")
        return file_path

    def capture_single(self):
        try:
            self.start_capture()
            frame = self.capture_frame()
            self.save_frame(frame)
            return frame
        finally:
            self.stop_capture()

    def capture_periodic(self):
        try:
            self.start_capture()
            last_save_time = 0
            while True:
                current_time = time.time()
                if current_time - last_save_time >= self.interval:
                    frame = self.capture_frame()
                    self.save_frame(frame)
                    last_save_time = current_time

                time.sleep(
                    min(max(0.1, (last_save_time + self.interval) - time.time()), 1.0)
                )
        except KeyboardInterrupt:
            logger.info("Periodic capture stopped by user.")
        finally:
            self.stop_capture()

    def run(self):
        if self.mode == "single":
            return self.capture_single()
        elif self.mode == "periodic":
            return self.capture_periodic()
        else:
            raise ValueError("Mode must be 'single' or 'periodic'")


@app.command()
def capture(
    video_source: str = typer.Option(
        CAM_MJPEG_URL,
        help="Axis MJPEG stream URL (4K, max quality)",
    ),
    output_dir: Path = typer.Option(
        CAM_RAW_IMAGES_PATH, help="Directory to save captured frames."
    ),
    mode: str = typer.Option("single", help="Capture mode: 'single' or 'periodic'"),
    interval: int = typer.Option(
        config["inference"]["interval_seconds"],
        help="Interval between captures (in periodic mode, seconds)",
    ),
):
    video_capture = VideoCapture(
        video_source=video_source, output_dir=output_dir, mode=mode, interval=interval
    )
    video_capture.run()


if __name__ == "__main__":
    app()
