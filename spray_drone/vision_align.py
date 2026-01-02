# state_machine.py
from enum import Enum, auto


class DroneState(Enum):
    INIT = auto()
    IDLE = auto()
    ARM_TAKEOFF = auto()
    NAVIGATE = auto()
    ALIGN = auto()
    SPRAY = auto()
    POST_SPRAY = auto()
    RTL = auto()


class StateMachine:
    def __init__(self):
        self.state = DroneState.INIT

        # Allowed transitions map
        self.allowed_transitions = {
            DroneState.INIT: [DroneState.IDLE],

            DroneState.IDLE: [DroneState.ARM_TAKEOFF],

            DroneState.ARM_TAKEOFF: [DroneState.NAVIGATE],

            DroneState.NAVIGATE: [
                DroneState.ALIGN,
                DroneState.SPRAY,
                DroneState.RTL
            ],

            DroneState.ALIGN: [
                DroneState.SPRAY,
                DroneState.NAVIGATE,
                DroneState.RTL
            ],

            DroneState.SPRAY: [DroneState.POST_SPRAY],

            DroneState.POST_SPRAY: [
                DroneState.NAVIGATE,
                DroneState.RTL
            ],

            DroneState.RTL: []
        }

    # --------------------------------------------------
    # GET CURRENT STATE
    # --------------------------------------------------
    def get_state(self):
        return self.state

    # --------------------------------------------------
    # CHECK TRANSITION VALIDITY
    # --------------------------------------------------
    def can_transition(self, next_state):
        return next_state in self.allowed_transitions[self.state]

    # --------------------------------------------------
    # SET NEW STATE (SAFE)
    # --------------------------------------------------
    def set_state(self, next_state):
        # 🔒 EMERGENCY OVERRIDE
        # RTL must be allowed from ANY state
        if next_state == DroneState.RTL:
            self.state = next_state
            return True
        
        if self.can_transition(next_state):
            self.state = next_state
            return True
        else:
            raise ValueError(
                f"Invalid transition: {self.state.name} → {next_state.name}"
            )

    # --------------------------------------------------
    # RESET MACHINE
    # --------------------------------------------------
    def reset(self):
        self.state = DroneState.INIT
