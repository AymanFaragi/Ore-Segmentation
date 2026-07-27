import base64
import io
import logging
import multiprocessing
import re
import torch, gc
import warnings
import threading
from pathlib import Path

import cv2
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import torch
from segment_anything import SamAutomaticMaskGenerator, sam_model_registry

from backend import config
from backend.logs import function_logger
from backend.sam.load_checkpoint import load_checkpoint

logger = logging.getLogger(__name__)

# Suppress debug logs for specific libraries
logging.getLogger("matplotlib").setLevel(logging.WARNING)
logging.getLogger("PIL").setLevel(logging.WARNING)


class SamInference:
    def __init__(
        self,
        model_type: str = config["sam_model"]["type"],
        checkpoint_path: Path = Path(config["paths"][f"sam_checkpoint_{config["sam_model"]["type"]}"]),
        ins_folder: Path = Path(config["paths"]["raw_image_path"]),
        outs_folder: Path = Path(config["paths"]["sam_output_path"]),    
        sieve_width_cm: float = None,
        sieve_height_cm: float = None,
    ):
        self.model_type = model_type
        self.ins_folder = ins_folder
        self.out_folder = outs_folder
        self.checkpoint_path = load_checkpoint(checkpoint_path)
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.ppcm = config["camera_settings"]["pixels_per_cm"]
        self.min_mask_region_area = config["sam_model"]["min_mask_region_area"]
        self.sieve_width_cm = (
            sieve_width_cm
            if sieve_width_cm is not None
            else config["sieve_dimensions"]["width_cm"]
        )
        self.sieve_height_cm = (
            sieve_height_cm
            if sieve_height_cm is not None
            else config["sieve_dimensions"]["height_cm"]
        )
        self.sieve_dimension = self._calculate_sieve_dimension()
        self.generator = self.get_sam_mask_generator()

        # OCP color scheme for mask visualization
        self.fill_color = np.array([255, 100, 100])
        self.border_color = np.array([228, 0, 0])
        self.alpha_value = 0.8

        print(self)

    def __repr__(self):
        logger.info("The running instance of Sam Inference has the following config:\n")
        return (
            f"SamInference(\n"
            f"    model_type={self.model_type!r},\n"
            f"    checkpoint_path={self.checkpoint_path!r},\n"
            f"    device={self.device!r}\n"
            f"    ins_folder={self.ins_folder!r},\n"
            f"    out_folder={self.out_folder!r},\n"
            f"    min_mask_region_area={self.min_mask_region_area!r},\n"
            f"    ppcm={self.ppcm!r},\n"
            f"    sieve_width_cm={self.sieve_width_cm!r},\n"
            f"    sieve_height_cm={self.sieve_height_cm!r},\n"
            f")"
        )

    def _calculate_sieve_dimension(self) -> list:
        """Calculate normalized sieve dimensions (smaller first)."""
        return (
            [self.sieve_width_cm, self.sieve_height_cm]
            if self.sieve_width_cm < self.sieve_height_cm
            else [self.sieve_height_cm, self.sieve_width_cm]
        )
    def update_params(self, **params):
        self.min_mask_region_area = params.get(
            "min_mask_region_area", self.min_mask_region_area
        )
        self.ppcm = params.get("ppcm", self.ppcm)
        self.sieve_width_cm = params.get("sieve_width_cm", self.sieve_width_cm)
        self.sieve_height_cm = params.get("sieve_height_cm", self.sieve_height_cm)
        logging.info(f"Updated sam inference instance parameters:\n\t - {params}")

    def get_current_params(self):
        return {
            "min_mask_region_area": self.min_mask_region_area,
            "ppcm": self.ppcm,
            "sieve_width_cm": self.sieve_width_cm,
            "sieve_height_cm": self.sieve_height_cm,
        }

    def get_sam_mask_generator(self) -> SamAutomaticMaskGenerator:
        with warnings.catch_warnings():
            warnings.filterwarnings(
                "ignore",
                category=FutureWarning,
                message="You are using `torch.load` with `weights_only=False`",
            )
            sam = sam_model_registry[self.model_type](checkpoint=self.checkpoint_path)
            sam.to(device=self.device)
            
        sam_conf = config["sam_model"]
        return SamAutomaticMaskGenerator(
            model=sam,
            points_per_side=sam_conf["points_per_side"],
            pred_iou_thresh=sam_conf["prediction_iou_threshold"],
            stability_score_thresh=sam_conf["stability_score_threshold"],
            crop_n_layers=sam_conf["cropping_layers"],
            crop_n_points_downscale_factor=sam_conf["crop_points_downscale_factor"],
            min_mask_region_area=sam_conf["min_mask_region_area"],
            box_nms_thresh=sam_conf["box_nms_threshold"],        # Stricter overlap filtering
            crop_nms_thresh=sam_conf["crop_nms_threshold"],      # Stricter crop filtering  
            crop_overlap_ratio=sam_conf["crop_overlap_ratio"],   # Less crop overlap
            
        )


    @function_logger(start_message="Applying SAM mask generator")
    def apply_sam_mask_generator(self, image: np.ndarray) -> list:
        return self.generator.generate(image)

    @function_logger(start_message="Selecting last captured image path")
    def get_last_captured_image_path(self) -> Path:
        images = list(self.ins_folder.glob("*.png"))
        if not images:
            logger.error(f"No images found in the directory: {self.ins_folder}")
            raise FileNotFoundError(
                f"No images found in the directory: {self.ins_folder}"
            )
        return max(images, key=lambda p: p.stat().st_mtime)

    @function_logger(start_message="Reading image")
    def read_image(self, path: Path) -> np.ndarray:
        return cv2.cvtColor(cv2.imread(str(path)), cv2.COLOR_BGR2RGB)

    @staticmethod
    def extract_datetime_from_filename(filename: str) -> str:
        """Extract date and time from filename with format frame_YYYYMMDD_HHMMSS.png"""
        match = re.search(
            r"frame_(\d{4})(\d{2})(\d{2})_(\d{2})(\d{2})(\d{2})\.png", filename
        )
        if match:
            year, month, day, hour, minute, second = match.groups()
            return f"{day}/{month}/{year} - {hour}:{minute}:{second}"
        return ""

    @function_logger(start_message="Plotting detected masks")
    def plot_masks(self, masks: list) -> np.ndarray:
        if not masks:
            return np.array([])

        height, width = masks[0]["segmentation"].shape
        img = np.zeros((height, width, 4), dtype=np.float32)

        for mask in masks:
            m = mask["segmentation"]

            # Use green fill color with alpha
            color_mask = np.concatenate([self.fill_color / 255.0, [self.alpha_value]])
            img[m] = color_mask

            # Find contours for red border
            contours, _ = cv2.findContours(
                m.astype(np.uint8), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
            )

            # Create a temporary image for drawing contours
            temp_img = np.zeros((height, width, 3), dtype=np.uint8)

            # Important: Use tuple for color, not numpy array
            border_color_tuple = (
                int(self.border_color[0]),
                int(self.border_color[1]),
                int(self.border_color[2]),
            )
            cv2.drawContours(
                temp_img, contours, -1, color=border_color_tuple, thickness=1
            )

            # Get the border mask (where the border is drawn)
            border_mask = np.any(temp_img > 0, axis=2)

            # Apply red color to the borders with full opacity
            img[border_mask, 0:3] = self.border_color / 255.0
            img[border_mask, 3] = 1.0  # Full opacity for borders

        return img

    def process_single_mask(self, mask):
        m = mask["segmentation"]
        height, width = m.shape
        img = np.zeros((height, width, 4), dtype=np.float32)

        # Use green fill color with alpha
        color_mask = np.concatenate([self.fill_color / 255.0, [self.alpha_value]])
        img[m] = color_mask

        # Find contours for red border
        contours, _ = cv2.findContours(
            m.astype(np.uint8), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
        )

        # Create a temporary image for drawing contours
        temp_img = np.zeros((height, width, 3), dtype=np.uint8)

        # Important: Use tuple for color, not numpy array
        border_color_tuple = (
            int(self.border_color[0]),
            int(self.border_color[1]),
            int(self.border_color[2]),
        )
        cv2.drawContours(temp_img, contours, -1, color=border_color_tuple, thickness=3)

        # Get the border mask (where the border is drawn)
        border_mask = np.any(temp_img > 0, axis=2)

        # Apply red color to the borders with full opacity
        img[border_mask, 0:3] = self.border_color / 255.0
        img[border_mask, 3] = 1.0  # Full opacity for borders

        return {
            "img": self.encode_image_to_base64(img),
            "bbox": mask["bbox"][2:],
        }

    def prepare_transparent_masks(self, masks: list) -> list:
        if not masks:
            return []

        return [self.process_single_mask(mask) for mask in masks]

#    @function_logger(start_message="Constructing particle DataFrame from masks data")
#    def build_particle_df(self, masks: list) -> pd.DataFrame:
#        return pd.DataFrame(
#            [
#                {
#                    "img": mask["img"],
#                    "min_dim": min(mask["bbox"]),
#                    "max_dim": max(mask["bbox"]),
#                }
#                for mask in masks
#            ]
#        )


    @function_logger(start_message="Constructing particle DataFrame from masks data")
    def build_particle_df(self, masks: list) -> pd.DataFrame:
        records = []
        for mask in masks:
            # mask["bbox"] was already set to [width_px, height_px] by process_single_mask()
            width_px, height_px = mask["bbox"]

            # min_dim/max_dim in pixels (will later be converted to cm by convert_pixels_to_cm)
            min_dim = min(width_px, height_px)
            max_dim = max(width_px, height_px)

            records.append({
                "img": mask["img"],
                "min_dim": min_dim,
                "max_dim": max_dim,
                "width_px": width_px,
                "height_px": height_px,
            })

        return pd.DataFrame(records)




    @function_logger(start_message="Converting all values from pixel to cm")
    def convert_pixels_to_cm(self, df: pd.DataFrame) -> pd.DataFrame:
        df["max_dim"] = np.round(df["max_dim"].to_numpy() / self.ppcm, 2)
        df["min_dim"] = np.round(df["min_dim"].to_numpy() / self.ppcm, 2)
        return df

    @function_logger(start_message="Calculating the conformity of each particle")
    def calculate_particle_conformity(self, df: pd.DataFrame) -> pd.DataFrame:
        min_dim_np = df["min_dim"].to_numpy()
        max_dim_np = df["max_dim"].to_numpy()
        df["conformity"] = ~((min_dim_np < self.sieve_dimension[0]) & (max_dim_np < self.sieve_dimension[1]))
        return df

    @function_logger(start_message="Calculating the percentage of non-conformity")
    def calculate_non_conformity_percentage(self, df: pd.DataFrame) -> float:
        return round(100 - (df["conformity"].mean() * 100), 1)

    @function_logger(end_message="Image saved successfully")
    def save_image(
        self, image: np.ndarray, input_image_path: Path, metadata: dict = None
    ) -> None:
        if image.size > 0:
            output_path = self.out_folder / input_image_path.name

            # Create a figure and axis
            fig, ax = plt.subplots(figsize=(10, 8))

            # Display the mask image
            ax.imshow(image)
            ax.axis("off")

            # Add metadata as title if provided
            if metadata:
                title_text = ""
                for key, value in metadata.items():
                    title_text += f"{key}: {value}\n"
                fig.suptitle(title_text, fontsize=12, y=0.98)
                fig.subplots_adjust(top=0.85)  # Adjust top margin to accommodate title

            # Save the figure
            fig.savefig(output_path, bbox_inches="tight", pad_inches=0.1)
            plt.close(fig)
            logger.info(f"Image saved to {output_path} with metadata")

    @staticmethod
    def encode_image_to_base64(img):
        buf = io.BytesIO()
        plt.imsave(buf, img, format="png")
        buf.seek(0)
        encoded_string = base64.b64encode(buf.getvalue()).decode("utf-8")
        return f"data:image/png;base64,{encoded_string}"

    def filter_non_conforming_masks(self, masks, conformity):
        """Filter masks to keep only non-conforming ones."""
        return [mask for mask, is_conform in zip(masks, conformity) if not is_conform]

    @function_logger(start_message="Formatting particle DataFrame to JSON response")
    def format_masks_data(self, df):
        # Get counts before filtering
        total_masks = len(df)
        non_conform_count = (~df["conformity"]).sum()
        non_conformity_percentage = self.calculate_non_conformity_percentage(df)

        response_data = {
            "masks_data": df.to_dict(orient="records"),
            "non_conformity_percentage": non_conformity_percentage,
            "masks_count": int(total_masks),
            "non_conform_count": int(non_conform_count),
        }
        return response_data

    def _process_and_save_masks_async(self, masks, df, data, last_raw_image_path):
        """Background thread — no CUDA calls happen in here, so a thread is safe
        and never drags the GPU-resident model across a process boundary."""
        thread = threading.Thread(
            target=self._process_and_save_masks,
            args=(masks, df, data, last_raw_image_path),
            daemon=True,
        ) 
        thread.start()

    def _process_and_save_masks(self, masks, df, data, last_raw_image_path):
        """Helper method to process masks and save image."""
        try:
            # Filter only non-conforming masks and plot
            non_conform_masks = self.filter_non_conforming_masks(
                masks, df["conformity"]
            )
            img = self.plot_masks(non_conform_masks)

            # Get metadata for the image
            non_conformity_percentage = data["non_conformity_percentage"]
            total_masks = data["masks_count"]
            non_conform_count = data["non_conform_count"]

            # Extract date and time from filename
            formatted_datetime = self.extract_datetime_from_filename(
                last_raw_image_path.name
            )

            # Create metadata for image title
            metadata = {
                "Date de capture": formatted_datetime,
                "Pourcentage de non-conformité": f"{non_conformity_percentage}%",
                "Nombre de particules non-conformes": non_conform_count,
                "Nombre total de particules": total_masks,
            }

            # Save image with metadata
            self.save_image(img, last_raw_image_path, metadata)
        except Exception as e:
            logger.error(f"Error in async image processing: {e}")

    def run(self, image_np):
        last_raw_image_path = self.get_last_captured_image_path()
        masks = self.apply_sam_mask_generator(image_np)

        # Convert to DataFrame and process
        masks_processed = self.prepare_transparent_masks(masks)
        df = self.build_particle_df(masks=masks_processed)
        df = self.convert_pixels_to_cm(df)
        df = self.calculate_particle_conformity(df)
        data = self.format_masks_data(df)

        # Start async task for image processing
        self._process_and_save_masks_async(masks, df, data, last_raw_image_path)

        return data


# ------------------------------------------------------------------------

if __name__ == "__main__":
    sam_inference = SamInference(
        model_type=config["sam_model"]["type"],
        checkpoint_path=Path(config["paths"]["sam_checkpoint_vit_l"]),
    )
    sam_inference.run()
