import cv2
import time
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision
def processImage(image, landmarker):
    rgbImage = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    mpResult=landmarker.detect_for_video(mp.Image(image_format=mp.ImageFormat.SRGB, data=rgbImage), int(time.monotonic()*1000))
    return rgbImage, mpResult
modelPath = "/Users/arturo/Desktop/automotive-gesture-control/gesture_detection/hand_landmarker.task"
options = vision.HandLandmarkerOptions(
    base_options=python.BaseOptions(model_asset_path=modelPath),
    running_mode=vision.RunningMode.VIDEO)
with vision.HandLandmarker.create_from_options(options) as landmarker:
    pass