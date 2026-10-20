import cv2
from hand_tracking import processImage, options, vision
camera = cv2.VideoCapture(0)
with vision.HandLandmarker.create_from_options(options) as landmarker:
    while True:
        captured, frame = camera.read()
        if not captured:
            print("Failed to capture image")
            break
        rgbFrame, mpResult = processImage(frame, landmarker)
        if len(mpResult.hand_landmarks) > 0:
            print("Found at least one hand")
        cv2.imshow("Car Gesture Control", frame)
        if cv2.waitKey(1) == ord('q'):
            break
camera.release()
cv2.destroyAllWindows()