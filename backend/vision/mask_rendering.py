import base64
import io

import cv2
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

from backend.logs import function_logger


@function_logger(start_message="Plotting detected masks")
def plot_masks(masks: list, fill_color: np.ndarray, border_color: np.ndarray, alpha_value: float) -> np.ndarray:
    """Renders a full annotated overlay (all given masks) for the saved snapshot image."""
    if not masks:
        return np.array([])

    height, width = masks[0]["segmentation"].shape
    img = np.zeros((height, width, 4), dtype=np.float32)

    for mask in masks:
        m = mask["segmentation"]
        color_mask = np.concatenate([fill_color / 255.0, [alpha_value]])
        img[m] = color_mask

        contours, _ = cv2.findContours(m.astype(np.uint8), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        temp_img = np.zeros((height, width, 3), dtype=np.uint8)
        border_color_tuple = (int(border_color[0]), int(border_color[1]), int(border_color[2]))
        cv2.drawContours(temp_img, contours, -1, color=border_color_tuple, thickness=1)

        border_mask = np.any(temp_img > 0, axis=2)
        img[border_mask, 0:3] = border_color / 255.0
        img[border_mask, 3] = 1.0

    return img


def process_single_mask(mask: dict, fill_color: np.ndarray, border_color: np.ndarray, alpha_value: float) -> dict:
    """Renders one mask's thumbnail (for gallery/overlay use) and extracts the
    raw data particle_metrics needs: bbox side lengths (px) and area (px).
    """
    m = mask["segmentation"]
    height, width = m.shape
    img = np.zeros((height, width, 4), dtype=np.float32)

    color_mask = np.concatenate([fill_color / 255.0, [alpha_value]])
    img[m] = color_mask

    contours, _ = cv2.findContours(m.astype(np.uint8), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    temp_img = np.zeros((height, width, 3), dtype=np.uint8)
    border_color_tuple = (int(border_color[0]), int(border_color[1]), int(border_color[2]))
    cv2.drawContours(temp_img, contours, -1, color=border_color_tuple, thickness=3)

    border_mask = np.any(temp_img > 0, axis=2)
    img[border_mask, 0:3] = border_color / 255.0
    img[border_mask, 3] = 1.0

    return {
        "img": encode_image_to_base64(img),
        "bbox": mask["bbox"][2:],       # [width_px, height_px]
        "area_px": int(mask["area"]),
    }


def prepare_transparent_masks(masks: list, fill_color: np.ndarray, border_color: np.ndarray, alpha_value: float) -> list:
    if not masks:
        return []
    return [process_single_mask(mask, fill_color, border_color, alpha_value) for mask in masks]

def encode_image_to_base64(img: np.ndarray) -> str:
    buf = io.BytesIO()
    plt.imsave(buf, img, format="png")
    buf.seek(0)
    encoded_string = base64.b64encode(buf.getvalue()).decode("utf-8")
    return f"data:image/png;base64,{encoded_string}"


def filter_non_conforming_masks(masks: list, conformity) -> list:
    """Filter raw SAM masks (not the rendered dicts) to keep only oversized ones,
    for building the annotated saved-image overlay."""
    return [mask for mask, is_conform in zip(masks, conformity) if not is_conform]

