# packet_handler.py
import time
from config import MIN_CONFIDENCE, MAX_PACKET_AGE_SEC


class PacketHandler:
    def __init__(self):
        pass

    # --------------------------------------------------
    # MAIN VALIDATION ENTRY
    # --------------------------------------------------
    def validate(self, raw_packet):
        """
        Validates and normalizes an incoming packet.
        Returns a clean packet dict if valid, else None.
        """

        # ---------- Required fields ----------
        required_keys = [
            "id", "lat", "lon", "alt", "confidence", "timestamp"
        ]

        for key in required_keys:
            if key not in raw_packet:
                return None

        # ---------- Type conversion ----------
        try:
            pkt_id = int(raw_packet["id"])
            lat = float(raw_packet["lat"])
            lon = float(raw_packet["lon"])
            alt = float(raw_packet["alt"])
            confidence = float(raw_packet["confidence"])
            timestamp = float(raw_packet["timestamp"])
        except (ValueError, TypeError):
            return None

        # ---------- GPS sanity ----------
        if not (-90.0 <= lat <= 90.0):
            return None
        if not (-180.0 <= lon <= 180.0):
            return None

        # ---------- Confidence check ----------
        if confidence < MIN_CONFIDENCE:
            return None

        # ---------- Timestamp freshness ----------
        if (time.time() - timestamp) > MAX_PACKET_AGE_SEC:
            return None

        # ---------- Normalized packet ----------
        clean_packet = {
            "id": pkt_id,
            "lat": lat,
            "lon": lon,
            "alt": alt,
            "confidence": confidence,
            "timestamp": timestamp,
            "status": "pending"
        }

        return clean_packet

