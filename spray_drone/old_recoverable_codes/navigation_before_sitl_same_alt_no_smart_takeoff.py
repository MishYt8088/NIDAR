# navigation.py
from dronekit import connect, VehicleMode, LocationGlobalRelative
import time
import math


# --------------------------------------------------
# CONNECT TO VEHICLE
# --------------------------------------------------
def connect_vehicle(connection_string, baudrate=57600):
    """
    Connects to Pixhawk and returns vehicle object
    """
    print("🔌 Connecting to vehicle...")
    vehicle = connect(connection_string, baud=baudrate, wait_ready=True)
    print("✅ Vehicle connected")
    return vehicle


# --------------------------------------------------
# ARM AND TAKEOFF
# --------------------------------------------------
def arm_and_takeoff(vehicle, target_altitude):
    """
    Arms the drone and takes off to target altitude
    """

    # Wait until vehicle is armable
    while not vehicle.is_armable:
        print("⏳ Waiting for vehicle to become armable...")
        time.sleep(1)

    # Set GUIDED mode
    vehicle.mode = VehicleMode("GUIDED")
    while vehicle.mode.name != "GUIDED":
        print("⏳ Waiting for GUIDED mode...")
        time.sleep(0.5)

    # Arm the vehicle
    vehicle.armed = True
    while not vehicle.armed:
        print("⏳ Arming...")
        time.sleep(0.5)

    print("🚀 Taking off...")
    vehicle.simple_takeoff(target_altitude)

    # Wait until altitude is reached
    while True:
        current_alt = vehicle.location.global_relative_frame.alt
        print(f"📡 Altitude: {current_alt:.2f} m")

        if current_alt >= target_altitude * 0.95:
            print("✅ Target altitude reached")
            break

        time.sleep(0.5)


# --------------------------------------------------
# GOTO GPS LOCATION
# --------------------------------------------------
def goto_location(vehicle, lat, lon, alt, speed=1.0):
    """
    Sends the drone to a GPS location
    """
    vehicle.groundspeed = speed
    target_location = LocationGlobalRelative(lat, lon, alt)
    vehicle.simple_goto(target_location)


# --------------------------------------------------
# DISTANCE CALCULATION (meters)
# --------------------------------------------------
def distance_to_target(current_location, target):
    """
    Calculates horizontal distance between two GPS points
    """

    dlat = target["lat"] - current_location.lat
    dlon = target["lon"] - current_location.lon

    return math.sqrt((dlat * 1.113195e5) ** 2 +
                     (dlon * 1.113195e5) ** 2)
