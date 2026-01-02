# ================================
# SPRAY HARDWARE CONFIG
# ================================

# GPIO pin connected to spray motor driver (BCM numbering)
SPRAY_GPIO_PIN = 18

# Spray duration per target (seconds)
SPRAY_DURATION_SEC = 2.0


# ================================
# VISION CONFIG (OPTIONAL)
# ================================

# Enable vision-based fine alignment
USE_VISION_ALIGN = True   # Set True if camera is available

# Vision timeout before declaring failure (seconds)
VISION_TIMEOUT_SEC = 10.0



# Show camera feed in VNC (DEBUG ONLY)
VISION_DEBUG_VIEW = True


# ================================
# SAFETY LIMITS
# ================================

# Minimum safe battery voltage (example for 6S LiPo)
MIN_BATTERY_VOLTAGE = 10.0

# Maximum allowed tilt during spray (degrees)
MAX_ROLL_DEG = 3.0
MAX_PITCH_DEG = 3.0

# Maximum allowed altitude (meters)
MAX_ALTITUDE_M = 10.0


# ================================
# CSV INPUT
# ================================
CSV_INPUT_PATH = "/home/pi/survey_outputs/yellow_targets.csv"

# Read existing CSV rows at startup (for testing / manual GPS)
CSV_READ_EXISTING = True


# ================================
# PACKET VALIDATION
# ================================

# Minimum confidence required to accept a target
MIN_CONFIDENCE = 0.6

# Maximum age of packet before rejection (seconds)
MAX_PACKET_AGE_SEC = 9999.0


# ================================
# QUEUE MANAGEMENT
# ================================

# Minimum number of targets before starting mission
MIN_BATCH_POINTS = 1

# Minimum distance between two spray targets (meters)
MIN_DISTANCE_BETWEEN_TARGETS_M = 1.0


# ================================
# MISSION TUNING
# ================================

# Distance considered "reached" for GPS navigation (meters)
NAVIGATION_REACHED_DIST_M = 0.4

# GPS grace period before RTL (seconds)
GPS_GRACE_SEC = 10.0

# Hover time after last target before RTL (seconds)
NO_TARGET_HOVER_SEC = 10.0
