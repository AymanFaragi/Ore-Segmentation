import pandas as pd

from backend.logs import function_logger


@function_logger(start_message="Calculating remaining (non-contaminated) area percentage")
def calculate_remaining_area_percentage(df: pd.DataFrame, total_area_px: int) -> float:
    """The one statistic that matters: % of the frame NOT covered by oversized
    (foreign) particles. Operates purely in pixel-area ratios — no ppcm
    dependency, since the calibration factor cancels out of a same-units ratio.

    Relies on particle_metrics.flag_oversized having already set 'conformity'
    (False = oversized) so this stays the single source of truth for what
    counts as oversized, rather than recomputing the threshold independently.
    """
    if total_area_px <= 0 or df.empty:
        return 100.0

    oversized_mask = ~df["conformity"]
    covered_area_px = df.loc[oversized_mask, "area_px"].sum()
    covered_percentage = 100.0 * covered_area_px / total_area_px
    return round(100.0 - covered_percentage, 1)