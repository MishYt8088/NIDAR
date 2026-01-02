# manual_gps_logger.py
import dronekit_py311_fix

import time
import csv
import os
from dronekit import connect


# ================================
# CONFIGURATION
# ================================

CONNECTION_STRING = "/dev/ttyACM0"   # change if needed
BAUD_RATE = 57600

CSV_OUTPUT_PATH = "/home/pi/survey_outputs/yellow_targets.csv"


# ================================
# CONNECT TO VEHICLE
# ================================
def connect_vehicle():
    print("🔌 Connecting to Pixhawk...")
    vehicle = connect(CONNECTION_STRING, baud=BAUD_RATE, wait_ready=True)
    print("✅ Connected")
    return vehicle


# ================================
# ENSURE CSV EXISTS
# ================================
def ensure_csv_file():
    os.makedirs(os.path.dirname(CSV_OUTPUT_PATH), exist_ok=True)

    if not os.path.exists(CSV_OUTPUT_PATH):
        with open(CSV_OUTPUT_PATH, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow([
                "id",
                "lat",
                "lon",
                "alt",
                "confidence",
                "timestamp"
            ])


# ================================
# GET NEXT ID
# ================================
def get_next_id():
    try:
        with open(CSV_OUTPUT_PATH, newline="") as f:
            reader = list(csv.reader(f))
            if len(reader) <= 1:
                return 1
            return int(reader[-1][0]) + 1
    except Exception:
        return 1


# ================================
# MAIN LOGGER
# ================================
def main():
    ensure_csv_file()
    vehicle = None

    try:
        vehicle = connect_vehicle()
        next_id = get_next_id()

        print("\n📍 MANUAL GPS LOGGER READY")
        print("Press ENTER to log current GPS position")
        print("Press Ctrl+C to exit\n")

        while True:
            loc = vehicle.location.global_relative_frame

            if loc.lat is None or loc.lon is None:
                print("⏳ Waiting for GPS fix...")
                time.sleep(1)
                continue

            print(
                f"Current GPS → "
                f"Lat: {loc.lat:.7f}, "
                f"Lon: {loc.lon:.7f}, "
                f"Alt: {loc.alt:.2f} m"
            )

            input("➡️  Press ENTER to save this point...")

            timestamp = int(time.time())

            with open(CSV_OUTPUT_PATH, "a", newline="") as f:
                writer = csv.writer(f)
                writer.writerow([
                    next_id,
                    loc.lat,
                    loc.lon,
                    loc.alt,
                    1.0,          # confidence (manual)
                    timestamp
                ])

            print(f"✅ Saved point ID {next_id}\n")
            next_id += 1

    except KeyboardInterrupt:
        print("\n🛑 Logger stopped by user")

    finally:
        if vehicle:
            vehicle.close()
        print("🧹 Connection closed safely")


# ================================
# ENTRY POINT
# ================================
if __name__ == "__main__":
    main()
