# survey_logger.py
import csv
import os
from datetime import datetime


class SurveyLogger:
    def __init__(self, csv_path="/home/pi/logs/survey_targets.csv"):
        self.csv_path = csv_path
        self.next_id = 1

        os.makedirs(os.path.dirname(self.csv_path), exist_ok=True)

        if not os.path.exists(self.csv_path):
            with open(self.csv_path, "w", newline="") as f:
                writer = csv.writer(f)
                writer.writerow([
                    "id",
                    "lat",
                    "lon",
                    "alt",
                    "confidence",
                    "timestamp"
                ])

    def log_target(self, lat, lon, alt, confidence):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        with open(self.csv_path, "a", newline="") as f:
            writer = csv.writer(f)
            writer.writerow([
                self.next_id,
                f"{lat:.7f}",
                f"{lon:.7f}",
                f"{alt:.2f}",
                f"{confidence:.2f}",
                timestamp
            ])

        print(f"📁 Survey CSV logged ID={self.next_id}")
        self.next_id += 1
