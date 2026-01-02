# mission_manager.py
import time
from dronekit import VehicleMode

from spray_logger import log_spray


# Core state machine
from state_machine import StateMachine, DroneState

# Flight + action modules
from navigation import arm_and_takeoff, goto_location, distance_to_target
from spray_controller import SprayController
from safety_checks import SafetyChecks

# Data ingestion
from packet_handler import PacketHandler
from comms.csv_receiver import CSVReceiver

# Configuration
from config import (
    CSV_INPUT_PATH,
    USE_VISION_ALIGN,
    SPRAY_DURATION_SEC,
    NAVIGATION_REACHED_DIST_M,
    GPS_GRACE_SEC,
    NO_TARGET_HOVER_SEC
)


class MissionManager:
    """
    MissionManager is the BRAIN of the spray drone.
    It:
    - Runs the state machine
    - Ingests targets (CSV now, wireless later)
    - Enforces safety
    - Calls navigation, spray, and vision modules
    """

    def __init__(self, vehicle, queue_manager, vision_align=None):
        # ------------------------------
        # Core objects
        # ------------------------------
        self.vehicle = vehicle
        self.sm = StateMachine()
        self.queue = queue_manager
        self.vision = vision_align

        # ------------------------------
        # Controllers
        # ------------------------------
        self.spray = SprayController()
        self.safety = SafetyChecks(vehicle)

        # ------------------------------
        # Packet + CSV ingestion
        # ------------------------------
        self.packet_handler = PacketHandler()
        self.csv_receiver = CSVReceiver(
            csv_path=CSV_INPUT_PATH,
            packet_handler=self.packet_handler,
            queue_manager=self.queue
        )

        # ------------------------------
        # Mission state variables
        # ------------------------------
        self.current_target = None
        self.takeoff_done = False

        # ------------------------------
        # Timers
        # ------------------------------
        self.gps_bad_since = None
        self.no_target_since = None

    # ==================================================
    # MAIN STEP (CALLED REPEATEDLY, NON-BLOCKING)
    # ==================================================
    def step(self):
        """
        One safe iteration of the mission.
        This function must NEVER block except during SPRAY.
        """

        # --------------------------------------------------
        # 1. SAFETY FIRST (HIGHEST PRIORITY)
        # --------------------------------------------------
        if not self._gps_with_grace():
            self._go_rtl("GPS lost beyond grace period")
            return

        #if not self.safety.attitude_ok():
         #   self._go_rtl("Excessive roll/pitch detected")
          #  return

        # --------------------------------------------------
        # 2. RECEIVE NEW TARGETS (CSV)
        # --------------------------------------------------
        # Safe to call every loop
        self.csv_receiver.poll()

        # If new targets arrived, cancel "no-target" timer
        if self.queue.has_pending():
            self.no_target_since = None

        # --------------------------------------------------
        # 3. STATE HANDLING
        # --------------------------------------------------
        state = self.sm.get_state()

        # ==============================
        # INIT
        # ==============================
        if state == DroneState.INIT:
            self.spray.setup()

            if USE_VISION_ALIGN and self.vision:
                self.vision.start()

            self.sm.set_state(DroneState.IDLE)

        # ==============================
        # IDLE
        # ==============================
        elif state == DroneState.IDLE:
            print(f"📦 Queue size: {self.queue.size()}")
            if self.queue.ready_for_mission():
                self.sm.set_state(DroneState.ARM_TAKEOFF)

        # ==============================
        # ARM AND TAKEOFF
        # ==============================
        elif state == DroneState.ARM_TAKEOFF:
            if not self.takeoff_done:
                print("✈️ Switching to GUIDED mode")
                self.vehicle.mode = VehicleMode("GUIDED")

                arm_and_takeoff(
                    self.vehicle,
                    self.vehicle.location.global_relative_frame.alt + 2
                )
                self.takeoff_done = True
                
                print("⏳ Waiting for GPS/EKF to settle...")
                time.sleep(8)

            self.sm.set_state(DroneState.NAVIGATE)


        # ==============================
        # NAVIGATE
        # ==============================
        elif state == DroneState.NAVIGATE:
            print("🧭 PYTHON NAVIGATING")
            if self.current_target is None:
                self.current_target = self.queue.pop_next_target()

                if self.current_target is None:
                    self._handle_no_targets()
                    return

#            goto_location(
#                self.vehicle,
#                self.current_target["lat"],
#                self.current_target["lon"],
#                self.current_target["alt"]
#            )

            current_alt = self.vehicle.location.global_relative_frame.alt

            goto_location(
                self.vehicle,
                self.current_target["lat"],
                self.current_target["lon"],
                current_alt
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

        # ==============================
        # ALIGN (VISION – OPTIONAL)
        # ==============================
        elif state == DroneState.ALIGN:
            # Absolute safety guard
            if not (USE_VISION_ALIGN and self.vision):
                self.sm.set_state(DroneState.SPRAY)
                return

            aligned, err_x, err_y = self.vision.process_frame()
            self.safety.update_vision_heartbeat()

            if aligned:
                self.sm.set_state(DroneState.SPRAY)

        # ==============================
        # SPRAY (BLOCKING – INTENTIONAL)
        # ==============================
        elif state == DroneState.SPRAY:
            self.spray.spray_for(SPRAY_DURATION_SEC)
            self.sm.set_state(DroneState.POST_SPRAY)

        # ==============================
        # POST SPRAY
        # ==============================
        elif state == DroneState.POST_SPRAY:
            
            finished_target = self.queue.mark_current_done("sprayed")

            if finished_target:
                log_spray(finished_target, SPRAY_DURATION_SEC, status="sprayed")

            self.current_target = None


            if self.queue.has_pending():
                self.sm.set_state(DroneState.NAVIGATE)
            else:
                self._handle_no_targets()

        # ==============================
        # RTL
        # ==============================
        elif state == DroneState.RTL:
            self.vehicle.mode = VehicleMode("RTL")
            self.spray.spray_off()

    # ==================================================
    # GPS GRACE HANDLING
    # ==================================================
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

    # ==================================================
    # NO TARGET HANDLING
    # ==================================================
    def _handle_no_targets(self):
        if self.no_target_since is None:
            self.no_target_since = time.time()
            return

        if (time.time() - self.no_target_since) >= NO_TARGET_HOVER_SEC:
            self._go_rtl("No pending spray targets")

    # ==================================================
    # RTL HELPER
    # ==================================================
    def _go_rtl(self, reason):
        print(f"⚠️ RTL triggered: {reason}")
        self.sm.set_state(DroneState.RTL)
