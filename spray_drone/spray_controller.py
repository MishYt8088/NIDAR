# spray_controller.py
import time
from gpiozero import OutputDevice
from config import SPRAY_GPIO_PIN


class SprayController:
    def __init__(self):
        # active_high=True → 3.3V turns spray ON
        self.sprayer = OutputDevice(SPRAY_GPIO_PIN, active_high=True)
        self.spraying = False

    def setup(self):
        self.sprayer.off()
        self.spraying = False
        print("💧 Spray system initialized (OFF)")

    def spray_on(self):
        if not self.spraying:
            self.sprayer.on()
            self.spraying = True
            print("🚿 Spray ON")

    def spray_off(self):
        self.sprayer.off()
        self.spraying = False
        print("🛑 Spray OFF")

    def spray_for(self, duration_sec):
        """
        Blocking spray — used ONLY in SPRAY state
        """
        self.spray_on()
        time.sleep(duration_sec)
        self.spray_off()

