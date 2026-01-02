# vision_align.py
import cv2
import numpy as np
import time
from config import VISION_DEBUG_VIEW, VISION_TIMEOUT_SEC


class VisionAlign:
    def __init__(self,
                 cam_index=0,
                 tolerance_px=15,
                 stable_frames_required=10):
        self.cam_index = cam_index
        self.tolerance_px = tolerance_px
        self.stable_frames_required = stable_frames_required

        self.cap = None
        self.stable_count = 0
        self.last_seen_time = time.time()

    # --------------------------------------------------
    # START CAMERA
    # --------------------------------------------------
    def start(self):
        print("📷 Starting vision alignment...")
        self.cap = cv2.VideoCapture(self.cam_index)

        if not self.cap.isOpened():
            print("❌ Camera open failed")
            raise RuntimeError("Camera could not be opened")

        self.stable_count = 0
        self.last_seen_time = time.time()
        print("✅ Camera opened successfully")

    # --------------------------------------------------
    # STOP CAMERA
    # --------------------------------------------------
    def stop(self):
        if self.cap:
            self.cap.release()
            self.cap = None
            if VISION_DEBUG_VIEW:
                cv2.destroyAllWindows()
            print("📷 Vision alignment stopped")

    # --------------------------------------------------
    # PROCESS ONE FRAME
    # --------------------------------------------------
    def process_frame(self):
        """
        Returns:
            aligned (bool)
            error_x (int or None)
            error_y (int or None)
        """

        # ---------------------------------
        # TIMEOUT HANDLING (TARGET LOST)
        # ---------------------------------
        if (time.time() - self.last_seen_time) > VISION_TIMEOUT_SEC:
            print("⚠️ Vision timeout — target lost")
            self.stable_count = 0
            return False, None, None

        ret, frame = self.cap.read()
        if not ret:
            return False, None, None

        h, w, _ = frame.shape
        cx_img = w // 2
        cy_img = h // 2

        # Convert to HSV
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

        # Yellow mask (tune if needed)
        lower_yellow = np.array([20, 100, 100])
        upper_yellow = np.array([35, 255, 255])
        mask = cv2.inRange(hsv, lower_yellow, upper_yellow)

        # Noise removal
        mask = cv2.medianBlur(mask, 5)

        # Find contours
        contours, _ = cv2.findContours(
            mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
        )

        if not contours:
            self.stable_count = 0
            return False, None, None

        # Target detected → reset timeout timer
        self.last_seen_time = time.time()

        # Pick largest yellow region
        largest = max(contours, key=cv2.contourArea)
        area = cv2.contourArea(largest)

        if area < 300:
            self.stable_count = 0
            return False, None, None

        # Centroid calculation
        M = cv2.moments(largest)
        if M["m00"] == 0:
            return False, None, None

        cx_obj = int(M["m10"] / M["m00"])
        cy_obj = int(M["m01"] / M["m00"])

        error_x = cx_obj - cx_img
        error_y = cy_obj - cy_img

        # Alignment check
        if abs(error_x) < self.tolerance_px and abs(error_y) < self.tolerance_px:
            self.stable_count += 1
        else:
            self.stable_count = 0

        aligned = self.stable_count >= self.stable_frames_required

        # ---------------------------------
        # DEBUG VIEW (OPTIONAL)
        # ---------------------------------
        if VISION_DEBUG_VIEW:
            debug_frame = frame.copy()

            cv2.circle(debug_frame, (cx_img, cy_img), 5, (255, 0, 0), -1)
            cv2.circle(debug_frame, (cx_obj, cy_obj), 5, (0, 0, 255), -1)

            cv2.rectangle(
                debug_frame,
                (cx_img - self.tolerance_px, cy_img - self.tolerance_px),
                (cx_img + self.tolerance_px, cy_img + self.tolerance_px),
                (0, 255, 0),
                2
            )

            cv2.imshow("Vision Debug", debug_frame)
            cv2.waitKey(1)

        return aligned, error_x, error_y
