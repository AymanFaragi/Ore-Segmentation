import argparse
import logging
from pathlib import Path

import requests

from backend.constants import SAM_CHECKPOINT_VIT_L_PATH

logger = logging.getLogger(__name__)


def load_checkpoint(checkpoint_path: Path = SAM_CHECKPOINT_VIT_L_PATH) -> Path:
    if checkpoint_path.exists():
        return checkpoint_path
    logger.warning(
        f"🔍 Local copy of {checkpoint_path.name} not found. Attempting to download... 🚀"
    )
    url = f"https://dl.fbaipublicfiles.com/segment_anything/{checkpoint_path.name}"
    response = requests.get(url)

    if response.status_code == 200:
        checkpoint_path.parent.mkdir(parents=True, exist_ok=True)
        with open(checkpoint_path, "wb") as f:
            f.write(response.content)
        logger.info(f"🎉 Download of {checkpoint_path.name} completed successfully! 🎊")
        logger.info(f"Checkpoint saved to: {checkpoint_path}")
        return checkpoint_path
    else:
        logger.error(f"❌ Failed to download checkpoint from {url}")
        raise FileNotFoundError(f"Checkpoint not found locally or at {url}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Load SAM model checkpoint")
    parser.add_argument(
        "--path",
        type=str,
        default=SAM_CHECKPOINT_VIT_L_PATH,
        help=f"Path to the checkpoint file. Default is {SAM_CHECKPOINT_VIT_L_PATH}",
    )

    # Parse arguments
    args = parser.parse_args()

    # Load checkpoint
    load_checkpoint(Path(args.path))
