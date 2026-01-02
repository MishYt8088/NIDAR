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
        Blocking spray sequence:
        1. Wait 3s (Stabilize water)
        2. Spray ON
        3. Wait duration
        4. Spray OFF
        5. Wait 3s (Prevent dripping while moving)
        """
        STABILIZE_TIME = 3.0  # Seconds to wait before spraying
        DRIP_TIME = 3.0       # Time to wait after spray to clear nozzle


        # 1. Pre-Spray Stabilization
        print(f"⚖️  Stabilizing drone for {STABILIZE_TIME}s before spray...")
        time.sleep(STABILIZE_TIME)

        # 2. Spray Action
        print(f"🏁 Stabilization complete. Starting spray.")
        self.spray_on()
        time.sleep(duration_sec)

        # 3. Stop Spray
        self.spray_off()

        # 4. Post-Spray Wait (Prevent dripping)
        print(f"⏳ Waiting {DRIP_TIME}s for drips to clear...")
        time.sleep(DRIP_TIME)
        print("✅ Spray sequence complete. Ready to move.")
