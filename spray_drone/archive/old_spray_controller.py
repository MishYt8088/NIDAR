# spray_controller.py
import time
import RPi.GPIO as GPIO
from config import SPRAY_GPIO_PIN, SPRAY_ACTIVE_HIGH


class SprayController:
    def __init__(self):
        self.spraying = False

    # --------------------------------------------------
    # GPIO SETUP
    # --------------------------------------------------
    def setup(self):
        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)

        GPIO.setup(SPRAY_GPIO_PIN, GPIO.OUT)

        # Ensure spray is OFF at startup
        self.spray_off()
        print("💧 Spray system initialized (OFF)")

    # --------------------------------------------------
    # SPRAY ON
    # --------------------------------------------------
    def spray_on(self):
        if not self.spraying:
            GPIO.output(
                SPRAY_GPIO_PIN,
                GPIO.HIGH if SPRAY_ACTIVE_HIGH else GPIO.LOW
            )
            self.spraying = True
            print("🚿 Spray ON")

    # --------------------------------------------------
    # SPRAY OFF
    # --------------------------------------------------
    def spray_off(self):
        GPIO.output(
            SPRAY_GPIO_PIN,
            GPIO.LOW if SPRAY_ACTIVE_HIGH else GPIO.HIGH
        )
        self.spraying = False
        print("🛑 Spray OFF")

    # --------------------------------------------------
    # TIMED SPRAY (NON-BLOCKING FRIENDLY)
    # --------------------------------------------------
    def spray_for(self, duration_sec):
        """
        Blocking version — used ONLY inside SPRAY state
        """
        self.spray_on()
        time.sleep(duration_sec)
        self.spray_off()

    # --------------------------------------------------
    # EMERGENCY CLEANUP
    # --------------------------------------------------
    def cleanup(self):
        self.spray_off()
        GPIO.cleanup()
        print("🧹 Spray system cleaned up safely")
