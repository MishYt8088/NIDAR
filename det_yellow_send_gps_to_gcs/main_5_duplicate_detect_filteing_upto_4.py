
from dronekit import VehicleMode
from mission_step1_polygon import upload_rectangle_mission, start_step1_mission

import cv2
from dronekit import connect
from pymavlink import mavutil

from camera import Camera
from vision import detect_yellow_and_centroid
from tracker import YellowTracker
from drone_state import DroneState
from gps_utils import GPSUtils


def main():
    # --------------------------------------------------
    # CAMERA + TRACKER
    # --------------------------------------------------
    cam = Camera(cam_index=0)
    tracker = YellowTracker(stable_frames=10)

    frame_center_tolerance = 20  # pixels (blue box half size)

    # --------------------------------------------------
    # DRONEKIT CONNECTION (SITL or REAL DRONE)
    # --------------------------------------------------
    vehicle = connect("udp:127.0.0.1:14550", wait_ready=True)

    drone_state = DroneState(vehicle)
    gps_utils = GPSUtils(vehicle)

    # --------------------------------------------------
    # STEP 1 — POLYGON MISSION (REAL DRONE)
    # --------------------------------------------------
    upload_rectangle_mission(vehicle, altitude=4.0)
    start_step1_mission(vehicle, speed=1.0)


    # --------------------------------------------------
    # GPS CAPTURE STATE
    # --------------------------------------------------
    gps_captured = False
    detected_points = []   # list of (lat, lon, alt)

    detection_count = 0

    print("✅ System started, waiting for yellow detection...")



    target_confirmed = False     # STEP 3: duplicate filter
    yellow_visible = False      # helper state



    # --------------------------------------------------
    # MAIN LOOP
    # --------------------------------------------------
    while True:
        frame = cam.read()
        if frame is None:
            break

        # -------------------------------
        # FRAME CENTER
        # -------------------------------
        h, w, _ = frame.shape
        center_x = w // 2
        center_y = h // 2

        # -------------------------------
        # YELLOW DETECTION + CENTROID
        # -------------------------------
        detected, cx, cy, mask = detect_yellow_and_centroid(frame)

        # -------------------------------
        # TEMPORAL STABILITY (LOCK)
        # -------------------------------
        locked = tracker.update(detected)

        # -------------------------------
        # BLUE BOX (SPATIAL ALIGNMENT)
        # -------------------------------
        inside_box = False
        if detected:
            inside_box = (
                abs(cx - center_x) <= frame_center_tolerance and
                abs(cy - center_y) <= frame_center_tolerance
            )

        # -------------------------------
        # ATTITUDE CHECK (ROLL & PITCH)
        # -------------------------------
        level = drone_state.is_level()

        # -------------------------------
        # FINAL DECISION FLAG
        # -------------------------------
        ready_for_gps = locked and inside_box and level

        # ==================================================
        # GPS CAPTURE LOGIC (HERE3+ SAFE)
        # ==================================================
        if ready_for_gps and not gps_captured:
            if gps_utils.position_ok():


                if not target_confirmed:

                    lat, lon, alt = gps_utils.get_position()

                    detected_points.append((lat, lon, alt))
                    gps_captured = True


                    detection_count += 1
                    print(f"🎯 Detection count = {detection_count}")




                    # -------- TERMINAL OUTPUT --------
                    print("\n✅ YELLOW TARGET GPS CAPTURED")
                    print(f"Latitude : {lat:.7f}")
                    print(f"Longitude: {lon:.7f}")
                    print(f"Altitude : {alt:.2f}")
                    print("----------------------------------")

                    # -------- MISSION PLANNER MESSAGE --------
                    msg = f"YELLOW @ {lat:.6f}, {lon:.6f}"
                    vehicle._master.mav.statustext_send(
                        mavutil.mavlink.MAV_SEVERITY_INFO,
                        msg.encode()
                    )

                    if detection_count >= 2:
                        print("🛬 Required detections reached — RTL triggered")
                        vehicle.mode = VehicleMode("RTL")

                else:
                    # Same yellow still visible → ignore
                    pass

            else:
                print("⚠️ GPS/EKF not ready — skipping capture")

            # Reset capture when yellow disappears
            if not detected:
                gps_captured = False
                yellow_visible = False
                target_confirmed = False

        # ==================================================
        # VISUAL DEBUG (FOR VNC / MONITOR USE)
        # ==================================================
        # Blue box
        cv2.rectangle(
            frame,
            (center_x - frame_center_tolerance, center_y - frame_center_tolerance),
            (center_x + frame_center_tolerance, center_y + frame_center_tolerance),
            (255, 0, 0),
            2,
        )

        if detected:
            # Red centroid dot
            cv2.circle(frame, (cx, cy), 7, (0, 0, 255), -1)

            if locked:
                cv2.putText(
                    frame,
                    "YELLOW LOCKED",
                    (10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    1,
                    (0, 255, 0),
                    2,
                )

        roll_deg, pitch_deg = drone_state.get_attitude_deg()

        cv2.putText(
            frame,
            f"INSIDE BOX: {inside_box}",
            (10, 70),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            (255, 255, 0),
            2,
        )

        cv2.putText(
            frame,
            f"ROLL: {roll_deg:.1f}  PITCH: {pitch_deg:.1f}",
            (10, 110),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            (0, 255, 255),
            2,
        )

        cv2.putText(
            frame,
            f"READY GPS: {ready_for_gps}",
            (10, 150),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            (0, 255, 0) if ready_for_gps else (0, 0, 255),
            2,
        )

        if gps_captured:
            cv2.putText(
                frame,
                "GPS CAPTURED",
                (10, 190),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.8,
                (0, 255, 0),
                2,
            )

        cv2.imshow("Camera Feed", frame)
        cv2.imshow("Yellow Mask", mask)

        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

    # --------------------------------------------------
    # CLEANUP
    # --------------------------------------------------
    cam.release()
    vehicle.close()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
