import cv2
import time
from hand_tracking import processImage, options, vision
from swipe import detectSwipe
from media_control import next_track, previous_track
camera = cv2.VideoCapture(0)
positions = []
lastSwipeTime = 0
cooldown = 2.0
with vision.HandLandmarker.create_from_options(options) as landmarker:
    while True:
        captured, frame = camera.read()
        if not captured:
            print("Failed to capture image")
            break
        rgbFrame, mpResult = processImage(frame, landmarker)
        if len(mpResult.hand_landmarks) > 0:
            wrist = mpResult.hand_landmarks[0][0]
            wristX = wrist.x
            wristY = wrist.y
            frameWidth = frame.shape[1]
            frameHeight = frame.shape[0]
            wristXPixels = int(wristX * frameWidth)
            wristYPixels = int(wristY * frameHeight)
            currentTime = time.monotonic()
            positions.append((wristXPixels, wristYPixels, currentTime))
            while positions and currentTime - positions[0][2] > 0.5:
                positions.pop(0)
            direction, lastSwipeTime = detectSwipe(positions, currentTime, lastSwipeTime, cooldown)
            if direction is not None:
                print(f"Swipe detected: {direction}")
                if direction == "Left":
                    previous_track()
                elif direction == "Right":
                    next_track()
                positions.clear()
        else:
            positions.clear()
        cv2.imshow("Car Gesture Control", frame)
        if cv2.waitKey(1) == ord('q'):
            break
camera.release()
cv2.destroyAllWindows()