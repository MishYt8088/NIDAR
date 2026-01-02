# mission_manager.py
import time
from dronekit import VehicleMode

from spray_logger import log_spray
from state_machine import StateMachine, DroneState
from spray_controller import SprayController
from safety_checks import SafetyChecks
from packet_handler import PacketHandler
from comms.csv_receiver import CSVReceiver

# NEW IMPORTS from updated navigation.py
from navigation import (
    smart_takeoff,
    navigate_to_target_blocking,
    change_altitude
)

from config import (
    CSV_INPUT_PATH,
    USE_VISION_ALIGN,
    SPRAY_DURATION_SEC,
    GPS_GRACE_SEC,
    NO_TARGET_HOVER_SEC
)

# --- FLIGHT SETTINGS ---
SAFE_TRAVEL_ALT = 4.0   # Meters (Travel height)
SPRAY_WORK_ALT = 2.0    # Meters (Spraying height)


class MissionManager:
    def __init__(self, vehicle, queue_manager, vision_align=None):
        self.vehicle = vehicle
        self.sm = StateMachine()
        self.queue = queue_manager
        self.vision = vision_align
        self.spray = SprayController()
        self.safety = SafetyChecks(vehicle)
        self.packet_handler = PacketHandler()
        self.csv_receiver = CSVReceiver(
            csv_path=CSV_INPUT_PATH,
            packet_handler=self.packet_handler,
            queue_manager=self.queue
        )
        self.current_target = None
        self.takeoff_done = False
        self.gps_bad_since = None
        self.no_target_since = None

    # ==================================================
    # MAIN STEP
    # ==================================================
    def step(self):
        # 1. Safety
        if not self._gps_with_grace():
            self._go_rtl("GPS lost beyond grace period")
            return

        # 2. Ingest Data
        self.csv_receiver.poll()
        if self.queue.has_pending():
            self.no_target_since = None

        # 3. State Machine
        state = self.sm.get_state()

        # --- INIT ---
        if state == DroneState.INIT:
            self.spray.setup()
            if USE_VISION_ALIGN and self.vision:
                self.vision.start()
            self.sm.set_state(DroneState.IDLE)

        # --- IDLE ---
        elif state == DroneState.IDLE:
            if self.queue.ready_for_mission():
                self.sm.set_state(DroneState.ARM_TAKEOFF)

        # --- ARM & TAKEOFF ---
        elif state == DroneState.ARM_TAKEOFF:
            if not self.takeoff_done:
                # Use SMART TAKEOFF to Safe Travel Altitude
                smart_takeoff(self.vehicle, SAFE_TRAVEL_ALT)
                self.takeoff_done = True
                print("⏳ Stabilizing after takeoff...")
                time.sleep(2)

            self.sm.set_state(DroneState.NAVIGATE)

        # --- NAVIGATE (High -> Low Logic) ---
        elif state == DroneState.NAVIGATE:
            if self.current_target is None:
                self.current_target = self.queue.pop_next_target()

                # IF NO TARGETS: Wait here. Do not ascend/descend.
                if self.current_target is None:
                    self._handle_no_targets()
                    return

            # STEP 1: Fly to Target at SAFE_TRAVEL_ALT (2m)
            arrived = navigate_to_target_blocking(
                self.vehicle,
                self.current_target["lat"],
                self.current_target["lon"],
                SAFE_TRAVEL_ALT
            )

            if arrived:
                # STEP 2: Descend to SPRAY_WORK_ALT (1m)
                change_altitude(self.vehicle, SPRAY_WORK_ALT)

                # STEP 3: Proceed to Align or Spray
                if USE_VISION_ALIGN and self.vision:
                    self.sm.set_state(DroneState.ALIGN)
                else:
                    self.sm.set_state(DroneState.SPRAY)
            else:
                # If navigation failed/interrupted
                self.current_target = None

        # --- ALIGN ---
        elif state == DroneState.ALIGN:
            if not (USE_VISION_ALIGN and self.vision):
                self.sm.set_state(DroneState.SPRAY)
                return
            aligned, err_x, err_y = self.vision.process_frame()
            self.safety.update_vision_heartbeat()
            if aligned:
                self.sm.set_state(DroneState.SPRAY)

        # --- SPRAY ---
        elif state == DroneState.SPRAY:
            # Delays and Logic handled inside spray_for
            self.spray.spray_for(SPRAY_DURATION_SEC)
            self.sm.set_state(DroneState.POST_SPRAY)

        # --- POST SPRAY (Ascend Logic) ---
        elif state == DroneState.POST_SPRAY:
            # STEP 4: Ascend back to SAFE_TRAVEL_ALT (5m) before moving
            change_altitude(self.vehicle, SAFE_TRAVEL_ALT)

            finished_target = self.queue.mark_current_done("sprayed")
            if finished_target:
                log_spray(finished_target, SPRAY_DURATION_SEC, status="sprayed")

            self.current_target = None

            # --- CRITICAL FIX: ALWAYS GO TO NAVIGATE ---
            # Even if queue is empty, we go to NAVIGATE.
            # NAVIGATE will see it's empty and handle the "Wait/Hover" logic.
            self.sm.set_state(DroneState.NAVIGATE)

        # --- RTL ---
        elif state == DroneState.RTL:
            if self.vehicle.mode.name != "RTL":
                self.vehicle.mode = VehicleMode("RTL")

            if self.spray.spraying:
                self.spray.spray_off()

    # Helpers
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

    def _handle_no_targets(self):
        if self.no_target_since is None:
            self.no_target_since = time.time()
            return
        if (time.time() - self.no_target_since) >= NO_TARGET_HOVER_SEC:
            self._go_rtl("No pending spray targets")

    def _go_rtl(self, reason):
        print(f"⚠️ RTL triggered: {reason}")
        self.sm.set_state(DroneState.RTL)
