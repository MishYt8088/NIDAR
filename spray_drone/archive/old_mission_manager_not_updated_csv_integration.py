# mission_manager.py
import time
from dronekit import VehicleMode

from state_machine import StateMachine, DroneState
from navigation import arm_and_takeoff, goto_location, distance_to_target
from spray_controller import SprayController
from safety_checks import SafetyChecks
from config import (
    USE_VISION_ALIGN,
    SPRAY_DURATION_SEC,
    NAVIGATION_REACHED_DIST_M,
    GPS_GRACE_SEC,
    NO_TARGET_HOVER_SEC
)


class MissionManager:
    def __init__(self, vehicle, queue_manager, vision_align=None):
        self.vehicle = vehicle
        self.sm = StateMachine()
        self.queue = queue_manager
        self.vision = vision_align

        self.spray = SprayController()
        self.safety = SafetyChecks(vehicle)

        self.current_target = None
        self.takeoff_done = False

        self.gps_bad_since = None
        self.no_target_since = None

    # --------------------------------------------------
    # ONE STEP OF MISSION (NON-BLOCKING)
    # --------------------------------------------------
    def step(self):
        # ---------- SAFETY FIRST ----------
        if not self._gps_with_grace():
            self._go_rtl("GPS lost beyond grace")
            return

        if not self.safety.attitude_ok():
            self._go_rtl("Excessive tilt")
            return

        # ---------- STATE HANDLING ----------
        state = self.sm.get_state()

        # ===== INIT =====
        if state == DroneState.INIT:
            self.spray.setup()
            if USE_VISION_ALIGN and self.vision:
                self.vision.start()
            self.sm.set_state(DroneState.IDLE)

        # ===== IDLE =====
        elif state == DroneState.IDLE:
            if self.queue.ready_for_mission():
                self.sm.set_state(DroneState.ARM_TAKEOFF)

        # ===== ARM & TAKEOFF =====
        elif state == DroneState.ARM_TAKEOFF:
            if not self.takeoff_done:
                arm_and_takeoff(self.vehicle, self.vehicle.location.global_relative_frame.alt + 5)
                self.takeoff_done = True
            self.sm.set_state(DroneState.NAVIGATE)

        # ===== NAVIGATE =====
        elif state == DroneState.NAVIGATE:
            if self.current_target is None:
                self.current_target = self.queue.pop_next_target()
                if self.current_target is None:
                    self._handle_no_targets()
                    return

            goto_location(
                self.vehicle,
                self.current_target["lat"],
                self.current_target["lon"],
                self.current_target["alt"]
            )

            dist = distance_to_target(
                self.vehicle.location.global_relative_frame,
                self.current_target
            )

            if dist <= NAVIGATION_REACHED_DIST_M:
                if USE_VISION_ALIGN and self.vision:
                    self.sm.set_state(DroneState.ALIGN)
                else:
                    self.sm.set_state(DroneState.SPRAY)

        # ===== ALIGN =====
        elif state == DroneState.ALIGN:
            aligned, err_x, err_y = self.vision.process_frame()
            self.safety.update_vision_heartbeat()

            if aligned:
                self.sm.set_state(DroneState.SPRAY)

        # ===== SPRAY =====
        elif state == DroneState.SPRAY:
            self.spray.spray_for(SPRAY_DURATION_SEC)
            self.sm.set_state(DroneState.POST_SPRAY)

        # ===== POST SPRAY =====
        elif state == DroneState.POST_SPRAY:
            self.queue.mark_current_done("sprayed")
            self.current_target = None

            if self.queue.has_pending():
                self.sm.set_state(DroneState.NAVIGATE)
            else:
                self._handle_no_targets()

        # ===== RTL =====
        elif state == DroneState.RTL:
            self.vehicle.mode = VehicleMode("RTL")
            self.spray.spray_off()

    # --------------------------------------------------
    # GPS GRACE HANDLING
    # --------------------------------------------------
    def _gps_with_grace(self):
        if self.safety.gps_ok():
            self.gps_bad_since = None
            return True

        if self.gps_bad_since is None:
            self.gps_bad_since = time.time()
            return True

        if (time.time() - self.gps_bad_since) < GPS_GRACE_SEC:
            return True

        return False

    # --------------------------------------------------
    # NO TARGET HANDLING
    # --------------------------------------------------
    def _handle_no_targets(self):
        if self.no_target_since is None:
            self.no_target_since = time.time()
            return

        if (time.time() - self.no_target_since) >= NO_TARGET_HOVER_SEC:
            self._go_rtl("No more targets")

    # --------------------------------------------------
    # RTL HELPER
    # --------------------------------------------------
    def _go_rtl(self, reason):
        print(f"⚠️ RTL triggered: {reason}")
        self.sm.set_state(DroneState.RTL)

