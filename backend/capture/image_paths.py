import logging
import re
from pathlib import Path

logger = logging.getLogger(__name__)


def get_last_captured_image_path(ins_folder: Path) -> Path:
    images = list(ins_folder.glob("*.png"))
    if not images:
        logger.error(f"No images found in the directory: {ins_folder}")
        raise FileNotFoundError(f"No images found in the directory: {ins_folder}")
    return max(images, key=lambda p: p.stat().st_mtime)


def extract_datetime_from_filename(filename: str) -> str:
    """Extract date and time from filename with format frame_YYYYMMDD_HHMMSS.png"""
    match = re.search(r"frame_(\d{4})(\d{2})(\d{2})_(\d{2})(\d{2})(\d{2})\.png", filename)
    if match:
        year, month, day, hour, minute, second = match.groups()
        return f"{day}/{month}/{year} - {hour}:{minute}:{second}"
    return ""