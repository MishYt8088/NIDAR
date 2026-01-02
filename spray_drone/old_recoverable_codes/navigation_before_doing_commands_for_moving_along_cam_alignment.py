# navigation.py
from dronekit import connect, VehicleMode, LocationGlobalRelative
import time
import math

# --------------------------------------------------
# CONNECT TO VEHICLE
# --------------------------------------------------
def connect_vehicle(connection_string, baudrate=57600):
    print("🔌 Connecting to vehicle...")
    vehicle = connect(connection_string, baud=baudrate, wait_ready=True)
    print("✅ Vehicle connected")
    return vehicle


# --------------------------------------------------
# SMART TAKEOFF (Handles Ground & Mid-Air)
# --------------------------------------------------
def smart_takeoff(vehicle, target_altitude):
    """
    Arms and takes off. Sets SAFE SPEED immediately.
    """
    # 1. Arm if not armed
    if not vehicle.armed:
        while not vehicle.is_armable:
            print("⏳ Waiting for vehicle to become armable...")
            time.sleep(1)

        vehicle.mode = VehicleMode("GUIDED")
        while vehicle.mode.name != "GUIDED":
            print("⏳ Waiting for GUIDED mode...")
            time.sleep(0.5)

        vehicle.armed = True
        while not vehicle.armed:
            print("⏳ Arming...")
            time.sleep(0.5)

    # --- CRITICAL FIX: Set speed BEFORE moving ---
    print("🐌 Setting safe groundspeed to 1.0 m/s...")
    vehicle.groundspeed = 1.0
    # ---------------------------------------------

    # 2. Decide: Takeoff or Goto
    current_alt = vehicle.location.global_relative_frame.alt

    if current_alt < 1.0:
        print(f"🚀 Taking off to {target_altitude}m...")
        vehicle.simple_takeoff(target_altitude)
    else:
        print(f"🚀 Already airborne ({current_alt:.1f}m). Adjusting to {target_altitude}m...")
        current_loc = vehicle.location.global_relative_frame
        target_loc = LocationGlobalRelative(current_loc.lat, current_loc.lon, target_altitude)
        vehicle.simple_goto(target_loc)

    # 3. Wait for Altitude
    while True:
        current_alt = vehicle.location.global_relative_frame.alt
        if current_alt >= target_altitude * 0.95:
            print(f"✅ Reached Safe Altitude: {current_alt:.1f}m")
            break
        time.sleep(1)


# --------------------------------------------------
# BLOCKING NAVIGATION (Slow & Safe)
# --------------------------------------------------
def navigate_to_target_blocking(vehicle, lat, lon, alt):
    """
    Flies to lat/lon at fixed 'alt'. Blocks until arrival.
    Enforces 1.0 m/s speed for heavy payload safety.
    """
    print(f"🧭 NAVIGATING to target at {alt}m altitude...")

    # 1. ENFORCE SPEED AGAIN
    vehicle.groundspeed = 1.0

    # 2. SEND COMMAND
    target_loc = LocationGlobalRelative(float(lat), float(lon), float(alt))
    vehicle.simple_goto(target_loc)

    last_log_time = time.time()

    while True:
        current_loc = vehicle.location.global_relative_frame
        dist = distance_to_target_meters(current_loc, target_loc)

        # Log every 3 seconds
        if time.time() - last_log_time > 3.0:
            print(f"   ... Distance to target: {dist:.1f}m")
            last_log_time = time.time()

            # Resend command to correct drift & enforce speed
            vehicle.groundspeed = 1.0
            vehicle.simple_goto(target_loc)

        # Safety Exit
        if vehicle.mode.name not in ['GUIDED', 'AUTO']:
            print("⚠️ Manual Control Detected! Stopping Navigation.")
            return False

        # Arrival Check (within 1.0m)
#        if dist < 1.0:
#            print(f"✅ Arrived at Target: {lat}, {lon}")
#            return True
#
#        time.sleep(0.2)

        # 1. Check Distance (Are we close?)
        if dist < 1.0:  # Stricter: 0.5m instead of 1.0m

            # 2. Check Speed (Have we actually stopped?)
            current_speed = vehicle.groundspeed
            if current_speed < 0.2:  # Wait until almost motionless (0.2 m/s)
                print(f"✅ Arrived at Target: {lat}, {lon} (Speed: {current_speed:.2f} m/s)")
                return True
            else:
                # We are close, but moving too fast. Wait a tiny bit more.
                # (Optional: print debug to see it braking)
                # print(f"   ... Braking ... Speed: {current_speed:.2f} m/s")
                pass

        time.sleep(0.2)


# --------------------------------------------------
# CHANGE ALTITUDE (Vertical Only)
# --------------------------------------------------
def change_altitude(vehicle, new_alt):
    """
    Changes altitude IN PLACE (without moving lat/lon).
    """
    current_alt = vehicle.location.global_relative_frame.alt
    direction = "Ascending" if new_alt > current_alt else "Descending"
    print(f"↕️  {direction} to {new_alt}m...")

    current_loc = vehicle.location.global_relative_frame
    target_loc = LocationGlobalRelative(current_loc.lat, current_loc.lon, float(new_alt))

    vehicle.simple_goto(target_loc)

    while True:
        current_alt = vehicle.location.global_relative_frame.alt
        diff = abs(current_alt - new_alt)

        if diff < 0.3: # Within 30cm
            print(f"✅ Reached Altitude: {new_alt}m")
            break
        time.sleep(0.5)


# --------------------------------------------------
# HELPER: DISTANCE CALCULATION
# --------------------------------------------------
def distance_to_target_meters(loc1, loc2):
    lat1 = loc1.lat
    lon1 = loc1.lon

    if isinstance(loc2, dict):
        lat2 = loc2["lat"]
        lon2 = loc2["lon"]
    else:
        lat2 = loc2.lat
        lon2 = loc2.lon

    dlat = lat2 - lat1
    dlon = lon2 - lon1
    return math.sqrt((dlat * 1.113195e5) ** 2 + (dlon * 1.113195e5) ** 2)
