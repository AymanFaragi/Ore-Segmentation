from pathlib import Path
from unittest.mock import MagicMock, patch

import numpy as np
import pandas as pd
import pytest

from backend.sam.inference import SamInference


def test_build_particle_df():
    # SAM object
    sam_inference = SamInference()

    # Sample input data (mocks)
    masks = np.array(
        [
            {"area": 150, "bbox": [0, 0, 10, 15]},
            {"area": 200, "bbox": [5, 5, 8, 12]},
        ]
    )

    # Expected output DataFrame
    expected_df = pd.DataFrame(
        [
            {"particle_area": 150, "min_dim": 10, "max_dim": 15},
            {"particle_area": 200, "min_dim": 8, "max_dim": 12},
        ]
    )

    # Call the function
    result_df = sam_inference.build_particle_df(masks)

    # Check if the DataFrame content matches
    pd.testing.assert_frame_equal(result_df, expected_df)


# ------------------------------------------------------------------------


def test_convert_pixels_to_cm():
    # SAM object
    sam_inference = SamInference()

    # Sample input DataFrame
    df_particule = pd.DataFrame(
        [
            {"particle_area": 150, "min_dim": 10, "max_dim": 15},
            {"particle_area": 200, "min_dim": 8, "max_dim": 12},
        ]
    )

    # Pixel to millimeter conversion ratio
    px_mm_ratio = 19
    sam_inference.px_mm_ratio = px_mm_ratio

    # Expected output DataFrame after conversion
    expected_df = pd.DataFrame(
        [
            {
                "particle_area": 150 / (px_mm_ratio**2),
                "min_dim": 10 / px_mm_ratio,
                "max_dim": 15 / px_mm_ratio,
            },
            {
                "particle_area": 200 / (px_mm_ratio**2),
                "min_dim": 8 / px_mm_ratio,
                "max_dim": 12 / px_mm_ratio,
            },
        ]
    )

    # Call the function
    result_df = sam_inference.convert_pixels_to_cm(df_particule)

    # Check if the DataFrame content matches
    pd.testing.assert_frame_equal(result_df, expected_df)


# ------------------------------------------------------------------------


def test_calculate_particle_conformity():
    # SAM object
    sam_inference = SamInference()

    # Sample input DataFrame
    conv_df_particule = pd.DataFrame(
        [
            {"particle_area": 37.5, "min_dim": 5, "max_dim": 7.5},
            {"particle_area": 50, "min_dim": 4, "max_dim": 6},
            {"particle_area": 60, "min_dim": 9, "max_dim": 10},
            {"particle_area": 60, "min_dim": 5, "max_dim": 9},
        ]
    )

    # Sieve dimensions
    sam_inference.sieve_dimension = [6, 8]

    # Expected output DataFrame after conformity calculation
    expected_df = pd.DataFrame(
        [
            {"particle_area": 37.5, "min_dim": 5, "max_dim": 7.5, "conformity": True},
            {"particle_area": 50, "min_dim": 4, "max_dim": 6, "conformity": True},
            {"particle_area": 60, "min_dim": 9, "max_dim": 10, "conformity": False},
            {"particle_area": 60, "min_dim": 5, "max_dim": 9, "conformity": False},
        ]
    )

    # Call the function
    result_df = sam_inference.calculate_particle_conformity(conv_df_particule)

    # Check if the DataFrame content matches
    pd.testing.assert_frame_equal(result_df, expected_df)


# ------------------------------------------------------------------------


def test_calculate_conformity_percentage():
    # SAM object
    sam_inference = SamInference()

    # Sample input DataFrame
    final_df_particule = pd.DataFrame(
        [
            {
                "particle_area": 37.5,
                "min_dim": 7.5,
                "max_dim": 5.0,
                "conformity": True,
            },
            {
                "particle_area": 50.0,
                "min_dim": 6.0,
                "max_dim": 4.0,
                "conformity": True,
            },
            {
                "particle_area": 60.0,
                "min_dim": 10.0,
                "max_dim": 9.0,
                "conformity": False,
            },
        ]
    )

    # Expected output percentage of conformity
    expected_conformity_perc = (
        0.67  # 2 out of 3 particles conform, so 2/3 = 0.666... rounded to 0.67
    )

    # Call the function
    result_conformity_perc = sam_inference.calculate_conformity_percentage(
        final_df_particule
    )

    # Check if the conformity percentage matches
    assert result_conformity_perc == expected_conformity_perc


# ------------------------------------------------------------------------
