import math

class DroneState:
    def __init__(self, vehicle, max_tilt_deg=5):
        self.vehicle = vehicle
        self.max_tilt_rad = math.radians(max_tilt_deg)

    def is_level(self):
        roll = self.vehicle.attitude.roll
        pitch = self.vehicle.attitude.pitch

        if roll is None or pitch is None:
            return False

        return (
            abs(roll) <= self.max_tilt_rad and
            abs(pitch) <= self.max_tilt_rad
        )

    def get_attitude_deg(self):
        roll = math.degrees(self.vehicle.attitude.roll)
        pitch = math.degrees(self.vehicle.attitude.pitch)
        return roll, pitch
