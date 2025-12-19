# spray_controller.py
import time
import RPi.GPIO as GPIO
from config import SPRAY_GPIO_PIN


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
        GPIO.output(SPRAY_GPIO_PIN, GPIO.LOW)
        self.spraying = False
        print("💧 Spray system initialized (OFF)")

    # --------------------------------------------------
    # SPRAY ON
    # --------------------------------------------------
    def spray_on(self):
        if not self.spraying:
            GPIO.output(SPRAY_GPIO_PIN, GPIO.HIGH)  # 3.3V → ON
            self.spraying = True
            print("🚿 Spray ON")

    # --------------------------------------------------
    # SPRAY OFF
    # --------------------------------------------------
    def spray_off(self):
        GPIO.output(SPRAY_GPIO_PIN, GPIO.LOW)  # 0V → OFF
        self.spraying = False
        print("🛑 Spray OFF")

    # --------------------------------------------------
    # TIMED SPRAY
    # --------------------------------------------------
    def spray_for(self, duration_sec):
        """
        Blocking spray used ONLY in SPRAY state
        """
        self.spray_on()
        time.sleep(duration_sec)
        self.spray_off()

    # --------------------------------------------------
    # EMERGENCY CLEANUP
    # --------------------------------------------------
    def cleanup(self):
        GPIO.output(SPRAY_GPIO_PIN, GPIO.LOW)
        GPIO.cleanup()
        print("🧹 Spray system cleaned up safely")

