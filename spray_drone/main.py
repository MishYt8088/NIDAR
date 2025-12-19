# main.py
import time
import sys

from dronekit import connect

from config import USE_VISION_ALIGN
from queue_manager import QueueManager
from mission_manager import MissionManager

# Vision module is optional
if USE_VISION_ALIGN:
    from vision_align import VisionAlign


# --------------------------------------------------
# VEHICLE CONNECTION
# --------------------------------------------------
def connect_vehicle():
    """
    Connects to Pixhawk via serial or UDP.
    Adjust connection string as needed.
    """
    print("🔌 Connecting to vehicle...")
    vehicle = connect('/dev/ttyAMA0', baud=57600, wait_ready=True)
    print("✅ Vehicle connected")
    return vehicle


# --------------------------------------------------
# MAIN ENTRY POINT
# --------------------------------------------------
def main():
    vehicle = None

    try:
        # ---------- CONNECT ----------
        vehicle = connect_vehicle()

        # ---------- QUEUE ----------
        queue_manager = QueueManager()

        # ---------- VISION (OPTIONAL) ----------
        vision = None
        if USE_VISION_ALIGN:
            vision = VisionAlign()

        # ---------- MISSION MANAGER ----------
        mission_manager = MissionManager(
            vehicle=vehicle,
            queue_manager=queue_manager,
            vision_align=vision
        )

        print("🚀 Spray Drone Mission Started")

        # ---------- MAIN LOOP ----------
        while True:
            mission_manager.step()
            time.sleep(0.1)

    except KeyboardInterrupt:
        print("\n🛑 Mission interrupted by user")

    except Exception as e:
        print(f"\n❌ Fatal error: {e}")

    finally:
        print("🧹 Cleaning up before exit...")

        try:
            if vehicle:
                vehicle.close()
        except Exception:
            pass

        print("✅ Shutdown complete")
        sys.exit(0)


# --------------------------------------------------
# PROGRAM START
# --------------------------------------------------
if __name__ == "__main__":
    main()

