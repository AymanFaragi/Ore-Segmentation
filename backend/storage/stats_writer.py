import csv
from pathlib import Path
from datetime import datetime

from backend.constants import DAILY_STATS_CSV_PATH  # add this to constants.py


class StatsWriter:
    def __init__(self, csv_path: Path = DAILY_STATS_CSV_PATH):
        self.csv_path = csv_path
        self.csv_path.parent.mkdir(parents=True, exist_ok=True)

    def append_run(self, data: dict):
        is_new_file = not self.csv_path.exists()
        with open(self.csv_path, "a", newline="") as f:
            writer = csv.writer(f)
            if is_new_file:
                writer.writerow(
                    ["timestamp", "stuck_percentage"]
                )
            writer.writerow([
                datetime.now().isoformat(),
                data["stuck_percentage"],
            ])