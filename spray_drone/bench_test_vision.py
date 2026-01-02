# bench_test_vision.py
# USE THIS ON THE BENCH ONLY (PROPS OFF)

import dronekit_py311_fix
import time
from dronekit import connect, VehicleMode
from vision_align import VisionAlign
from navigation import send_body_velocity

# --- CONFIG ---
CONNECTION_STRING = '/dev/ttyACM0' # Adjust if needed
BAUD = 57600

def bench_test():
    print("🔌 Connecting to vehicle (BENCH MODE)...")
    try:
        vehicle = connect(CONNECTION_STRING, baud=BAUD, wait_ready=True)
        print("✅ Vehicle connected")
    except:
        print("❌ Could not connect! Check USB cable.")
        return

    # Initialize Vision
    print("📷 Initializing Vision System...")
    vision = VisionAlign()
    vision.start()

    print("⚠️ STARTING TEST LOOP. PRESS CTRL+C TO STOP.")
    print("🌊 Wave a yellow object in front of the camera!")
    print("-" * 50)

    try:
        while True:
            # 1. Get Error from Camera
            aligned, err_x, err_y = vision.process_frame()
            
            # 2. Simulate the Logic from MissionManager
            if aligned:
                print("✅ [ALIGNED] - Drone would STOP and SPRAY now.")
                # We don't actually stop, so you can keep testing
            
            elif err_x is not None and err_y is not None:
                # Calculate Correction (Same math as MissionManager)
                K_p = 0.002
                MAX_SPEED = 0.3 

                vel_x = -err_y * K_p
                vel_y = err_x * K_p
                
                # Clamp speed
                vel_x = max(min(vel_x, MAX_SPEED), -MAX_SPEED)
                vel_y = max(min(vel_y, MAX_SPEED), -MAX_SPEED)
                
                # Print what the drone WOULD do
                direction_x = "FORWARD" if vel_x > 0 else "BACKWARD"
                direction_y = "RIGHT" if vel_y > 0 else "LEFT"
                
                print(f"🎯 Target Found! ErrX:{err_x} ErrY:{err_y}")
                print(f"   ➥ COMMAND: {direction_x} ({vel_x:.2f} m/s) | {direction_y} ({vel_y:.2f} m/s)")
                
                # OPTIONAL: Actually send the command to see motors twitch?
                # vehicle.mode = VehicleMode("GUIDED")
                # send_body_velocity(vehicle, vel_x, vel_y, 0)
                
            else:
                print("❌ No Target Seen (Searching...)")

            time.sleep(0.1)

    except KeyboardInterrupt:
        print("\n🛑 Test Stopped.")
        vision.stop()
        vehicle.close()

if __name__ == "__main__":
    bench_test()
