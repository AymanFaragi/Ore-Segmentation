import warnings

from segment_anything import SamAutomaticMaskGenerator, sam_model_registry

from backend import config


def build_sam_mask_generator(checkpoint_path, model_type: str, device: str) -> SamAutomaticMaskGenerator:
    """Loads the SAM checkpoint and constructs the mask generator.

    Pure model construction only — no business logic, no particle/contamination
    concerns. This is the one place that touches model weights and the GPU.
    """
    with warnings.catch_warnings():
        warnings.filterwarnings(
            "ignore",
            category=FutureWarning,
            message="You are using `torch.load` with `weights_only=False`",
        )
        sam = sam_model_registry[model_type](checkpoint=checkpoint_path)
        sam.to(device=device)

    sam_conf = config["sam_model"]
    return SamAutomaticMaskGenerator(
        model=sam,
        points_per_side=sam_conf["points_per_side"],
        pred_iou_thresh=sam_conf["prediction_iou_threshold"],
        stability_score_thresh=sam_conf["stability_score_threshold"],
        crop_n_layers=sam_conf["cropping_layers"],
        crop_n_points_downscale_factor=sam_conf["crop_points_downscale_factor"],
        min_mask_region_area=sam_conf["min_mask_region_area"],
        box_nms_thresh=sam_conf["box_nms_threshold"],
        crop_nms_thresh=sam_conf["crop_nms_threshold"],
        crop_overlap_ratio=sam_conf["crop_overlap_ratio"],
    )