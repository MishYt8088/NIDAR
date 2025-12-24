from dronekit import connect
from mission_step1_polygon import upload_rectangle_mission, start_step1_mission
import time

vehicle = connect("udp:127.0.0.1:14550", wait_ready=True)

upload_rectangle_mission(vehicle, altitude=4.0)
start_step1_mission(vehicle, speed=1.0)

print("🟢 STEP-1 SITL test running")

while True:
    print(f"Mode: {vehicle.mode.name}, Alt: {vehicle.location.global_relative_frame.alt:.1f}")
    time.sleep(2)
