class GPSUtils:
    def __init__(self, vehicle):
        self.vehicle = vehicle

    def gps_fix_ok(self):
        return self.vehicle.gps_0.fix_type >= 3

    def ekf_ok(self):
        return self.vehicle.ekf_ok

    def position_ok(self):
        return self.gps_fix_ok() and self.ekf_ok()

    def get_position(self):
        loc = self.vehicle.location.global_frame
        return loc.lat, loc.lon, loc.alt
