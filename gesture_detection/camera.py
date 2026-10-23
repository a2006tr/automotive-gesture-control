import cv2
import time
from hand_tracking import processImage, options, vision
from swipe import detectSwipe
from media_control import next_track, previous_track, volume_down, volume_up
from volume import detectPinch
camera = cv2.VideoCapture(0)
positions = []
pinchYHistory = []
lastSwipeTime = 0
pinchStartY = None
cooldown = 2.0
isPinching = False
with vision.HandLandmarker.create_from_options(options) as landmarker:
    while True:
        captured, frame = camera.read()
        if not captured:
            print("Failed to capture image")
            break
        rgbFrame, mpResult = processImage(frame, landmarker)
        # Draw hand landmarks
        for hand in mpResult.hand_landmarks:
            for landmark in hand:
                x = int(landmark.x * frame.shape[1])
                y = int(landmark.y * frame.shape[0])

                cv2.circle(frame, (x, y), 4, (0, 255, 0), -1)
        if len(mpResult.hand_landmarks) > 0:
            hand = mpResult.hand_landmarks[0]
            isPinching = detectPinch(hand, isPinching)

            if isPinching:
                if pinchStartY is None:
                    pinchStartY = hand[8].y
                pinchYHistory.append(hand[8].y)
                if len(pinchYHistory) > 5:
                    pinchYHistory.pop(0)
                if len(pinchYHistory) >= 3:
                    lastY = pinchYHistory[-2]
                    secondLastY = pinchYHistory[-3]
                    if (hand[8].y < lastY and secondLastY < lastY ) or (hand[8].y > lastY and secondLastY > lastY):
                        pinchStartY = hand[8].y
                changeY = hand[8].y - pinchStartY
                if changeY < -0.05:
                    print("VOLUME UP")
                    volume_up()
                    pinchStartY = hand[8].y
                elif changeY > 0.05:
                    print("VOLUME DOWN")
                    volume_down()
                    pinchStartY = hand[8].y
            else:
                pinchStartY = None
                pinchYHistory.clear()
            if not isPinching:
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
        else:
            positions.clear()
            isPinching = False
            pinchStartY = None
            pinchYHistory.clear()
        cv2.imshow("Car Gesture Control", frame)
        if cv2.waitKey(1) == ord('q'):
            break
camera.release()
cv2.destroyAllWindows()