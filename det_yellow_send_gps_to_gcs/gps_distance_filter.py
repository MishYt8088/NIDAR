import math


class GPSDistanceFilter:
    def __init__(self, min_distance_m=1.0):
        self.min_distance = min_distance_m
        self.logged_points = []  # [(lat, lon)]

    def haversine_distance(self, lat1, lon1, lat2, lon2):
        R = 6371000.0  # Earth radius in meters

        phi1 = math.radians(lat1)
        phi2 = math.radians(lat2)
        dphi = math.radians(lat2 - lat1)
        dlambda = math.radians(lon2 - lon1)

        a = (
            math.sin(dphi / 2) ** 2
            + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2) ** 2
        )
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

        return R * c

    def is_new_target(self, lat, lon):
        for old_lat, old_lon in self.logged_points:
            dist = self.haversine_distance(lat, lon, old_lat, old_lon)
            if dist < self.min_distance:
                return False
        return True

    def register_target(self, lat, lon):
        self.logged_points.append((lat, lon))
