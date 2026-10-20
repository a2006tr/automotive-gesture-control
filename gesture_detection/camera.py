import cv2
camera = cv2.VideoCapture(0)
while True:
    captured, frame = camera.read()
    if not captured:
        print("Failed to capture image")
        break
    cv2.imshow("Car Gesture Control", frame)
    if cv2.waitKey(1) == ord('q'):
        break
camera.release()
cv2.destroyAllWindows()