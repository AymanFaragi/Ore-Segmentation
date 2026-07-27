# import logging
# from pathlib import Path

# import cv2
# from confluent_kafka import Producer

# from backend.logs import function_logger

# logger = logging.getLogger(__name__)


# def delivery_report(err, msg):

#     if err is not None:
#         print(f"Message delivery failed: {msg} -> {err}")
#     else:
#         print(f"Message delivered to {msg.topic()} [{msg.partition()}]")


# @function_logger(
#     start_message="Periodically capturing and publishing images to kafka topic",
#     log_args=True,
#     args_list=["frame_interval"],
# )
# def capture_images_periodically(
#     cap: cv2.VideoCapture,
#     output_folder: Path,
#     frame_interval: int,
# ) -> None:
#     """
#     Periodically capture and publish images from a video stream to a Kafka topic.
#     """

#     TOPIC = "captured-images-topic"
#     frame_count, captured_count = 0, 0
#     producer = Producer({"bootstrap.servers": "localhost:9092"})

#     try:
#         while True:
#             ret, frame = cap.read()
#             if ret:
#                 if frame_count % frame_interval == 0:
#                     producer.produce(
#                         TOPIC,
#                         value=frame.tobytes(),
#                         callback=delivery_report,
#                     )
#                     captured_count += 1
#                 frame_count += 1
#             else:
#                 logger.error("Stream may have ended")
#                 break
#     except KeyboardInterrupt:
#         cap.release()
#         logger.warning("Capture stopped by user.")
#     finally:
#         producer.flush()
#         cap.release()
#         logger.info(f"Total images captured and published: {captured_count}")


# # def capture_images_periodically(
# #     cap: cv2.VideoCapture,
# #     frame_interval: int,
# #     kafka_topic: str,
# #     kafka_servers: str = "localhost:9092",
# # ) -> None:
# #     frame_count, captured_count = 0, 0
# #     producer_config = {
# #         "bootstrap.servers": kafka_servers,
# #         "message.max.bytes": 15728640,  # 15MB
# #         "compression.type": "gzip",
# #     }
# #     producer = Producer(producer_config)
# #     try:
# #         while True:
# #             ret, frame = cap.read()
# #             if ret:
# #                 if frame_count % frame_interval == 0:
# #                     compressed_frame = compress_frame(frame)
# #                     producer.produce(
# #                         kafka_topic,
# #                         value=json.dumps(compressed_frame),
# #                         key="frame",
# #                         callback=delivery_report,
# #                     )
# #                     captured_count += 1
# #                     logger.info(f"Frame {captured_count} sent.")
# #                 frame_count += 1
# #             else:
# #                 logger.error("Stream may have ended")
# #                 break
# #     except KeyboardInterrupt:
# #         cap.release()
# #         producer.flush()
# #         logger.warning("Capture stopped by user.")
# #     finally:
# #         producer.flush()
# #         cap.release()
# #         logger.info(f"Total images captured and published: {captured_count}")


# # def delivery_report(err, msg):
# #     if err is not None:
# #         print(f"Message delivery failed: {msg} -> {err}")
# #     else:
# #         print(f"Message delivered to {msg.topic()} [{msg.partition()}]")


# # def compress_frame(frame: np.ndarray, quality: int = 100) -> bytes:
# #     encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), quality]
# #     _, buffer = cv2.imencode(".png", frame, encode_param)
# #     return base64.b64encode(buffer).decode("utf-8")
