# safety_checks.py
import time
from config import (
    MIN_BATTERY_VOLTAGE,
    MAX_ROLL_DEG,
    MAX_PITCH_DEG,
    MAX_ALTITUDE_M,
    USE_VISION_ALIGN,
    VISION_TIMEOUT_SEC
)


class SafetyChecks:
    def __init__(self, vehicle):
        self.vehicle = vehicle
        self.last_vision_time = time.time()

    # --------------------------------------------------
    # BATTERY CHECK
    # --------------------------------------------------
    #def battery_ok(self):
        #voltage = self.vehicle.battery.voltage
        #if voltage is None:
         #   return False
        #return voltage >= MIN_BATTERY_VOLTAGE

    # --------------------------------------------------
    # ATTITUDE CHECK
    # --------------------------------------------------
    def attitude_ok(self):
        roll = abs(self.vehicle.attitude.roll * 57.3)   # rad → deg
        pitch = abs(self.vehicle.attitude.pitch * 57.3)
        return roll <= MAX_ROLL_DEG and pitch <= MAX_PITCH_DEG

#    # --------------------------------------------------
#    # GPS CHECK
#    # --------------------------------------------------
#    def gps_ok(self):
#        gps = self.vehicle.gps_0
#        return gps.fix_type >= 3
        
    # --------------------------------------------------
    # GPS CHECK (UPDATED)
    # --------------------------------------------------
    def gps_ok(self):
        # Access the GPS info
        gps = self.vehicle.gps_0
        
        # 1. Check for 3D Fix (3) or DGPS/RTK (4, 5, 6)
        fix_ok = gps.fix_type >= 3
        
        # 2. Check HDOP (Horizontal Dilution of Precision)
        # Lower is better. < 1.0 is good. > 1.4 is risky.
        hdop_ok = gps.eph < 140  # DroneKit returns eph in centimeters usually (140 = 1.4m)
        
        # 3. Check satellite count (optional, but good)
        sats_ok = gps.satellites_visible >= 7
        
        if not fix_ok:
            print(f"❌ GPS Fail: Fix type {gps.fix_type}")
        if not hdop_ok:
            print(f"❌ GPS Fail: HDOP {gps.eph/100.0}m (Too high)")
            
        return fix_ok and hdop_ok and sats_ok

    # --------------------------------------------------
    # ALTITUDE CHECK
    # --------------------------------------------------
    def altitude_ok(self):
        alt = self.vehicle.location.global_relative_frame.alt
        return alt <= MAX_ALTITUDE_M

    # --------------------------------------------------
    # VISION HEARTBEAT (optional)
    # --------------------------------------------------
    def update_vision_heartbeat(self):
        self.last_vision_time = time.time()

    def vision_ok(self):
        if not USE_VISION_ALIGN:
            return True
        return (time.time() - self.last_vision_time) <= VISION_TIMEOUT_SEC

    # --------------------------------------------------
    # GLOBAL SAFETY STATUS
    # --------------------------------------------------
    def all_ok(self):
        return (
            #self.battery_ok() and
            self.attitude_ok() and
            self.gps_ok() and
            self.altitude_ok() and
            self.vision_ok()
        )
