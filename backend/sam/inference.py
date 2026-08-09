import logging
from pathlib import Path

import numpy as np
import torch

from backend import config
from backend.capture.image_paths import get_last_captured_image_path
from backend.logs import function_logger
from backend.particles import contamination, particle_metrics
from backend.sam.load_checkpoint import load_checkpoint
from backend.sam.model import build_sam_mask_generator
from backend.vision.image_io import save_annotated_image_async
from backend.vision.mask_rendering import prepare_transparent_masks

logger = logging.getLogger(__name__)


class SamInference:
    def __init__(
        self,
        model_type: str = config["sam_model"]["type"],
        checkpoint_path: Path = Path(config["paths"][f"sam_checkpoint_{config['sam_model']['type']}"]),
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
        self.sieve_width_cm = sieve_width_cm if sieve_width_cm is not None else config["sieve_dimensions"]["width_cm"]
        self.sieve_height_cm = sieve_height_cm if sieve_height_cm is not None else config["sieve_dimensions"]["height_cm"]
        self.sieve_dimension = self._calculate_sieve_dimension()
        self.generator = build_sam_mask_generator(self.checkpoint_path, self.model_type, self.device)

        # OCP color scheme for mask visualization
        self.fill_color = np.array([255, 100, 100])
        self.border_color = np.array([228, 0, 0])
        self.alpha_value = 0.8

        logger.info(repr(self))

    def __repr__(self):
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
        """Normalized sieve dimensions (smaller first)."""
        return (
            [self.sieve_width_cm, self.sieve_height_cm]
            if self.sieve_width_cm < self.sieve_height_cm
            else [self.sieve_height_cm, self.sieve_width_cm]
        )

    def update_params(self, **params):
        self.min_mask_region_area = params.get("min_mask_region_area", self.min_mask_region_area)
        self.ppcm = params.get("ppcm", self.ppcm)
        self.sieve_width_cm = params.get("sieve_width_cm", self.sieve_width_cm)
        self.sieve_height_cm = params.get("sieve_height_cm", self.sieve_height_cm)
        self.sieve_dimension = self._calculate_sieve_dimension()
        logging.info(f"Updated sam inference instance parameters:\n\t - {params}")

    def get_current_params(self):
        return {
            "min_mask_region_area": self.min_mask_region_area,
            "ppcm": self.ppcm,
            "sieve_width_cm": self.sieve_width_cm,
            "sieve_height_cm": self.sieve_height_cm,
        }

    @function_logger(start_message="Applying SAM mask generator")
    def apply_sam_mask_generator(self, image: np.ndarray) -> list:
        return self.generator.generate(image)

    def run(self, image_np):
        last_raw_image_path = get_last_captured_image_path(self.ins_folder)
        masks = self.apply_sam_mask_generator(image_np)

        # Frame's total pixel area — plain numpy array metadata, independent
        # of SAM; computed straight off the captured frame.
        total_area_px = image_np.shape[0] * image_np.shape[1]

        rendered = prepare_transparent_masks(masks, self.fill_color, self.border_color, self.alpha_value)
        df = particle_metrics.build_particle_df(rendered)
        df = particle_metrics.convert_pixels_to_cm(df, self.ppcm)
        df = particle_metrics.flag_oversized(df, self.sieve_dimension)

        remaining_percentage = contamination.calculate_remaining_area_percentage(df, total_area_px)
        data = {
            "masks_data": df.to_dict(orient="records"),
            "stuck_percentage": remaining_percentage,
        }

        save_annotated_image_async(
            masks, df, data, last_raw_image_path, self.out_folder,
            self.fill_color, self.border_color, self.alpha_value,
        )

        return data


if __name__ == "__main__":
    sam_inference = SamInference(
        model_type=config["sam_model"]["type"],
        checkpoint_path=Path(config["paths"]["sam_checkpoint_vit_l"]),
    )