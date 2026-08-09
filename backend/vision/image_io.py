import logging
import threading

import matplotlib.pyplot as plt
import numpy as np

from backend.logs import function_logger
from backend.capture.image_paths import extract_datetime_from_filename
from backend.vision.mask_rendering import filter_non_conforming_masks, plot_masks

logger = logging.getLogger(__name__)


@function_logger(end_message="Image saved successfully")
def save_image(image: np.ndarray, output_path, metadata: dict = None) -> None:
    if image.size == 0:
        return

    fig, ax = plt.subplots(figsize=(10, 8))
    ax.imshow(image)
    ax.axis("off")

    if metadata:
        title_text = "".join(f"{key}: {value}\n" for key, value in metadata.items())
        fig.suptitle(title_text, fontsize=12, y=0.98)
        fig.subplots_adjust(top=0.85)

    fig.savefig(output_path, bbox_inches="tight", pad_inches=0.1)
    plt.close(fig)
    logger.info(f"Image saved to {output_path} with metadata")


def _process_and_save_masks(masks, df, data, last_raw_image_path, out_folder, fill_color, border_color, alpha_value):
    try:
        non_conform_masks = filter_non_conforming_masks(masks, df["conformity"])
        img = plot_masks(non_conform_masks, fill_color, border_color, alpha_value)

        formatted_datetime = extract_datetime_from_filename(last_raw_image_path.name)
        metadata = {
            "Date de capture": formatted_datetime,
            "Pourcentage restant": f"{data['stuck_percentage']}%",
        }

        save_image(img, out_folder / last_raw_image_path.name, metadata)
    except Exception as e:
        logger.error(f"Error in async image processing: {e}")


def save_annotated_image_async(masks, df, data, last_raw_image_path, out_folder, fill_color, border_color, alpha_value):
    """Background thread — no CUDA calls happen here, so a thread is safe and
    never drags the GPU-resident model across a process boundary (see the
    Windows spawn/CUDA-OOM note from earlier)."""
    thread = threading.Thread(
        target=_process_and_save_masks,
        args=(masks, df, data, last_raw_image_path, out_folder, fill_color, border_color, alpha_value),
        daemon=True,
    )
    thread.start()