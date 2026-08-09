import numpy as np
import pandas as pd

from backend.logs import function_logger


@function_logger(start_message="Constructing particle DataFrame from masks data")
def build_particle_df(rendered_masks: list) -> pd.DataFrame:
    """rendered_masks: list of dicts with 'img', 'bbox' ([width_px, height_px]),
    and 'area_px' — as produced by vision.mask_rendering.prepare_transparent_masks.
    """
    records = []
    for mask in rendered_masks:
        width_px, height_px = mask["bbox"]
        records.append({
            "img": mask["img"],
            "min_dim": min(width_px, height_px),
            "max_dim": max(width_px, height_px),
            "width_px": width_px,
            "height_px": height_px,
            "area_px": mask["area_px"],
        })
    return pd.DataFrame(records)


@function_logger(start_message="Converting all values from pixel to cm")
def convert_pixels_to_cm(df: pd.DataFrame, ppcm: float) -> pd.DataFrame:
    """Converts min_dim/max_dim (bbox side lengths) from px to cm.
    area_px is deliberately left untouched — it stays in raw pixels because
    the contamination stat is a same-units ratio and never needs cm² area.
    """
    df["max_dim"] = np.round(df["max_dim"].to_numpy() / ppcm, 2)
    df["min_dim"] = np.round(df["min_dim"].to_numpy() / ppcm, 2)
    return df


@function_logger(start_message="Flagging oversized (foreign) particles")
def flag_oversized(df: pd.DataFrame, sieve_dimension: list) -> pd.DataFrame:
    """Adds a 'conformity' column: False means the particle exceeds the sieve
    opening in both dimensions (i.e. it's foreign material that shouldn't be
    in the stream at all). True means normal-sized (passthrough or expected
    reject) — kept for gallery/overlay highlighting downstream, not for the
    aggregate contamination stat itself (see particles.contamination).
    """
    sieve_min, sieve_max = sieve_dimension
    min_dim_np = df["min_dim"].to_numpy()
    max_dim_np = df["max_dim"].to_numpy()
    df["conformity"] = ~((min_dim_np > sieve_min) & (max_dim_np > sieve_max))
    return df