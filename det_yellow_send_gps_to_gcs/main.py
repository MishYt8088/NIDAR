import cv2

from camera import Camera
from vision import detect_yellow_and_centroid
from tracker import YellowTracker

def main():
    cam = Camera(cam_index=0)
    tracker = YellowTracker(stable_frames=10)

    frame_center_tolerance = 20  # pixels

    while True:
        frame = cam.read()
        if frame is None:
            break

        h, w, _ = frame.shape
        center_x = w // 2
        center_y = h // 2

        detected, cx, cy, mask = detect_yellow_and_centroid(frame)
        locked = tracker.update(detected)

        # Draw frame center box
        cv2.rectangle(
            frame,
            (center_x - frame_center_tolerance, center_y - frame_center_tolerance),
            (center_x + frame_center_tolerance, center_y + frame_center_tolerance),
            (255, 0, 0),
            2,
        )

        if detected:
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

        cv2.imshow("Camera Feed", frame)
        cv2.imshow("Yellow Mask", mask)

        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

    cam.release()

if __name__ == "__main__":
    main()
