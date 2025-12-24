from dronekit import Command, VehicleMode
from pymavlink import mavutil
import time
import math


def get_location_offset_meters(origin, dNorth, dEast, alt):
    """
    Returns new (lat, lon, alt) offset from origin by meters
    """
    earth_radius = 6378137.0

    dLat = dNorth / earth_radius
    dLon = dEast / (earth_radius * math.cos(math.pi * origin.lat / 180))

    new_lat = origin.lat + (dLat * 180 / math.pi)
    new_lon = origin.lon + (dLon * 180 / math.pi)

    return new_lat, new_lon, alt


def upload_rectangle_mission(vehicle, altitude=4.0):
    """
    Uploads a rectangle mission relative to current location
    """
    cmds = vehicle.commands
    cmds.clear()
    time.sleep(1)

    home = vehicle.location.global_relative_frame

    # Rectangle size (meters)
    length = 20   # North
    width = 10    # East

    print("🧭 Uploading STEP-1 rectangle mission")

    # TAKEOFF
    cmds.add(
        Command(
            0, 0, 0,
            mavutil.mavlink.MAV_FRAME_GLOBAL_RELATIVE_ALT,
            mavutil.mavlink.MAV_CMD_NAV_TAKEOFF,
            0, 0, 0, 0, 0, 0,
            home.lat, home.lon, altitude
        )
    )

    # Rectangle waypoints
    points = [
        get_location_offset_meters(home, 0, 0, altitude),
        get_location_offset_meters(home, length, 0, altitude),
        get_location_offset_meters(home, length, width, altitude),
        get_location_offset_meters(home, 0, width, altitude),
    ]

    for lat, lon, alt in points:
        cmds.add(
            Command(
                0, 0, 0,
                mavutil.mavlink.MAV_FRAME_GLOBAL_RELATIVE_ALT,
                mavutil.mavlink.MAV_CMD_NAV_WAYPOINT,
                0, 0, 0, 0, 0, 0,
                lat, lon, alt
            )
        )

    cmds.upload()
    time.sleep(2)

    print("✅ Rectangle mission uploaded")


def start_step1_mission(vehicle, speed=1.0):
    """
    Sets speed and starts AUTO mission
    """
    vehicle.groundspeed = speed
    time.sleep(1)

    print(f"🐢 Ground speed set to {speed} m/s")
    print("🚀 Switching to AUTO mode")

    vehicle.mode = VehicleMode("AUTO")  #vehicle.commands.next = 0
					#vehicle.mode = VehicleMode("AUTO")

    while vehicle.mode.name != "AUTO":
        time.sleep(0.5)

    print("✅ STEP-1 mission started")
