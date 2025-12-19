# queue_manager.py
from collections import deque
import math
from config import (
    MIN_BATCH_POINTS,
    MIN_DISTANCE_BETWEEN_TARGETS_M
)


class QueueManager:
    def __init__(self):
        self.queue = deque()
        self.seen_ids = set()
        self.current_target = None

    # --------------------------------------------------
    # ADD NEW PACKET
    # --------------------------------------------------
    def add_packet(self, packet):
        """
        Adds a validated packet to the queue if not duplicate.
        """

        pkt_id = packet["id"]

        # ---- ID duplicate check ----
        if pkt_id in self.seen_ids:
            return False

        # ---- Distance duplicate check ----
        for existing in self.queue:
            if self._distance_m(existing, packet) < MIN_DISTANCE_BETWEEN_TARGETS_M:
                return False

        # Passed all checks
        self.queue.append(packet)
        self.seen_ids.add(pkt_id)
        return True

    # --------------------------------------------------
    # CHECK IF READY TO START MISSION
    # --------------------------------------------------
    def ready_for_mission(self):
        return len(self.queue) >= MIN_BATCH_POINTS

    # --------------------------------------------------
    # GET NEXT TARGET
    # --------------------------------------------------
    def pop_next_target(self):
        if self.current_target is not None:
            return None

        if not self.queue:
            return None

        self.current_target = self.queue.popleft()
        return self.current_target

    # --------------------------------------------------
    # MARK CURRENT TARGET AS DONE
    # --------------------------------------------------
    def mark_current_done(self, status="sprayed"):
        if self.current_target is None:
            return

        self.current_target["status"] = status
        self.current_target = None

    # --------------------------------------------------
    # QUEUE STATUS HELPERS
    # --------------------------------------------------
    def has_pending(self):
        return bool(self.queue)

    def queue_size(self):
        return len(self.queue)

    # --------------------------------------------------
    # DISTANCE CALCULATION (meters)
    # --------------------------------------------------
    def _distance_m(self, p1, p2):
        """
        Fast distance approximation for short ranges
        """
        dlat = p1["lat"] - p2["lat"]
        dlon = p1["lon"] - p2["lon"]

        return math.sqrt(
            (dlat * 1.113195e5) ** 2 +
            (dlon * 1.113195e5) ** 2
        )

