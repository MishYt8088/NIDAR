import cv2
import numpy as np

def detect_yellow_and_centroid(frame):
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

    # HSV range for yellow (field-tested range)
    lower_yellow = np.array([20, 100, 100])
    upper_yellow = np.array([35, 255, 255])

    mask = cv2.inRange(hsv, lower_yellow, upper_yellow)

    # Remove noise
    kernel = np.ones((5, 5), np.uint8)
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)

    contours, _ = cv2.findContours(
        mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
    )

    if not contours:
        return False, None, None, mask

    # Largest yellow area
    largest = max(contours, key=cv2.contourArea)

    if cv2.contourArea(largest) < 500:
        return False, None, None, mask

    M = cv2.moments(largest)

    if M["m00"] == 0:
        return False, None, None, mask

    cx = int(M["m10"] / M["m00"])
    cy = int(M["m01"] / M["m00"])

    return True, cx, cy, mask
