# """ This module runs a kafka consumer to process frames captured by cam_reader module"""

# import base64
# import json
# import logging
# from pathlib import Path

# # from segment_anything import SamAutomaticMaskGenerator, sam_model_registry
# import cv2
# import numpy as np
# from confluent_kafka import Consumer

# from backend.logs.log_config import setup_logging
# from backend.video_capture.run import save_frame

# setup_logging()
# logger = logging.getLogger(__name__)

# OUTPUT_DIR = Path("../asset/raw_images")


# def decompress_frame(frame_data: str) -> np.ndarray:
#     """Decompress the frame data."""
#     jpg_buffer = base64.b64decode(frame_data)
#     frame = cv2.imdecode(np.frombuffer(jpg_buffer, dtype=np.uint8), cv2.IMREAD_COLOR)
#     return frame


# def process_message(message):
#     try:
#         msg = json.loads(message.value())
#         frame = decompress_frame(msg)
#         if frame is not None:
#             save_frame(frame=frame, output_folder=OUTPUT_DIR)
#         else:
#             logger.error("Failed to decode frame")

#     except (json.JSONDecodeError, KeyError, TypeError) as e:
#         logger.error(f"Failed to process message: {e}")


# def consume_and_process_images():
#     TOPIC = "captured-images-topic"
#     consumer = Consumer(
#         {
#             "bootstrap.servers": "localhost:9092",
#             "max.partition.fetch.bytes": 15728640,  # 15MB
#             "group.id": "frame_group",
#             "auto.offset.reset": "earliest",
#         }
#     )
#     consumer.subscribe([TOPIC])

#     while True:
#         msg = consumer.poll(timeout=4.0)
#         if msg is None:
#             continue
#         if msg.error():
#             logger.error(f"Consumer error: {msg.error()}")
#             raise Exception(msg.error())

#         process_message(msg)


# if __name__ == "__main__":
#     consume_and_process_images()
