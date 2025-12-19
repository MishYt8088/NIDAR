

 Autonomous Spray Drone System (NIDAR Project)

This repository contains the **complete software stack for an autonomous agricultural spray drone**, designed for the **NIDAR competition**.

The system enables a spray drone (hexacopter) to:

* receive GPS coordinates of detected crop issues,
* autonomously navigate to those locations,
* accurately spray pesticide,
* log proof of spraying,
* and return safely — all with minimal human intervention.

The design is **modular, safe, testable, and competition-ready**.

---

#     High-Level System Overview

The system is built around **three core ideas**:

1. **Decoupling detection and spraying**

   * A *survey drone* (or manual tool during testing) generates GPS coordinates.
   * A *spray drone* consumes these coordinates and performs spraying.

2. **CSV-based communication (initially)**

   * GPS targets are stored in a CSV file.
   * This allows easy testing, debugging, and later replacement with wireless communication.

3. **State-machine-driven autonomy**

   * The spray drone operates using a well-defined state machine.
   * Each state performs a single responsibility (navigate, spray, RTL, etc.).

---

 #     Final Project Structure

Only the following files are part of the **final system**:

```
spray_drone_full/
│
├── main.py
├── mission_manager.py
├── state_machine.py
├── navigation.py
├── spray_controller.py
├── safety_checks.py
│
├── csv_receiver.py
├── packet_handler.py
├── queue_manager.py
│
├── vision_align.py        (optional, if camera is used)
│
├── spray_logger.py
├── manual_gps_logger.py  (testing utility)
│
├── config.py
│
├── logs/
│   └── spray_log.csv
│
└── survey_outputs/
    └── yellow_targets.csv
```

 #       Core Execution Flow

1} `main.py` — Entry Point

This is the **only file you run** to start the spray drone.

Responsibilities:

* Connects to Pixhawk
* Initializes all modules
* Runs the mission loop
* Handles safe shutdown on Ctrl+C

```bash
python3 main.py
```

---

2} `mission_manager.py` — Mission Brain

This is the **central controller** of the system.

It:

* Runs the state machine
* Reads GPS targets from CSV
* Controls navigation, spraying, and RTL
* Enforces safety rules
* Logs spray actions

All autonomy decisions happen here.

---

3} `state_machine.py` — State Control

Defines and manages drone states:

```
INIT
IDLE
ARM_AND_TAKEOFF
NAVIGATE
ALIGN
SPRAY
POST_SPRAY
RTL
```

This ensures:

* predictable behavior
* clean transitions
* easier debugging

---

#      Flight & Action Modules

4} `navigation.py`

Handles:

* arming
* takeoff
* GPS navigation
* distance calculations

Used by `mission_manager.py` to move the drone.

---

5} `spray_controller.py`

Controls the spray motor using Raspberry Pi GPIO.

* GPIO HIGH → spray ON
* GPIO LOW → spray OFF
* Spray duration is configurable

---

6} `safety_checks.py`

Continuously monitors:

* GPS health
* drone tilt (roll & pitch)
* optional vision heartbeat

If safety is violated → **RTL is triggered immediately**.

---

 #      Target Ingestion Pipeline

7} `csv_receiver.py`

* Reads new rows from `yellow_targets.csv`
* Non-blocking (safe during flight)
* Passes rows for validation

---

8} `packet_handler.py`

Validates each target:

* required fields
* confidence threshold
* packet age

Invalid targets are rejected safely.

---

9} `queue_manager.py`

Manages a FIFO queue of spray targets.

Features:

* duplicate suppression
* minimum distance filtering
* batch readiness logic

Ensures efficient spraying without repetition.

---

#      Optional Vision Alignment

10} `vision_align.py` (Optional)

If a camera is available on the spray drone:

* performs fine alignment before spraying

If no camera is available:

* system **automatically falls back to GPS-only spraying**
* no code changes required

Controlled via:

```python
USE_VISION_ALIGN = False
```

---

#     Logging & Testing Utilities

11} `spray_logger.py`

Logs **actual spray execution** to:

```
/home/pi/logs/spray_log.csv
```

Each row records:

* target ID
* GPS location
* spray duration
* timestamp
* status

This provides **ground-truth proof** of spraying (very useful for judges).

---

12} `manual_gps_logger.py` — Testing Tool

Used **only for testing**, before the survey drone is ready.

It:

* connects to Pixhawk
* shows live GPS
* logs a GPS point **each time ENTER is pressed**
* writes to `yellow_targets.csv`

This allows full system testing **without the survey drone**.

---

13} `config.py` — Single Source of Truth

All configuration lives here:

* GPIO pins
* CSV paths
* safety limits
* mission tuning
* vision enable/disable

No hard-coded values elsewhere.

---

#     End-to-End Workflow

### Testing Phase

1. Run `manual_gps_logger.py`
2. Log 2–3 GPS points
3. Close logger
4. Run `main.py`
5. Drone autonomously sprays targets
6. Watch `spray_log.csv` update live

### Competition Phase

1. Survey drone generates `yellow_targets.csv`
2. Spray drone runs `main.py`
3. Autonomous spraying
4. Logged proof available

---

#     Safety Philosophy

* **Pixhawk handles battery failsafe** (Mission Planner)
* Python code handles:

  * GPS grace period
  * tilt safety
  * mission-level RTL

Rule followed:

> **Fail safe > fail silently**

---

#      Design Highlights

* Modular & readable
* Beginner-friendly structure
* Testable without full hardware
* Vision optional
* CSV → wireless ready
* Judge-explainable

---

#      Project Status

* Core logic: **Complete**
* Testing path: **Complete**
* Safety: **Complete**
* Logging: **Complete**
* Competition readiness: **High**

No critical features are missing.

---

#      Future Extensions (Optional)

* Wireless target transfer (ESP-NOW / Wi-Fi)
* Obstacle avoidance
* Advanced failure logging
* Precision RTK refinement

---

Start by reading `main.py` → `mission_manager.py` → `state_machine.py`.


Just tell me 👍
