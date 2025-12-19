# spray_logger.py
import csv
import os
import time


SPRAY_LOG_PATH = "/home/pi/logs/spray_log.csv"


def ensure_log_file():
    os.makedirs(os.path.dirname(SPRAY_LOG_PATH), exist_ok=True)

    if not os.path.exists(SPRAY_LOG_PATH):
        with open(SPRAY_LOG_PATH, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow([
                "id",
                "lat",
                "lon",
                "alt",
                "spray_duration",
                "timestamp",
                "status"
            ])


def log_spray(target, spray_duration, status="sprayed"):
    ensure_log_file()

    with open(SPRAY_LOG_PATH, "a", newline="") as f:
        writer = csv.writer(f)
        writer.writerow([
            target.get("id"),
            target.get("lat"),
            target.get("lon"),
            target.get("alt"),
            spray_duration,
            int(time.time()),
            status
        ])

