import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision
import cv2
from PIL import Image


model_path = 'pose_landmarker_full.task'

BaseOptions = mp.tasks.BaseOptions
PoseLandmarker = mp.tasks.vision.PoseLandmarker
PoseLandmarkerOptions = mp.tasks.vision.PoseLandmarkerOptions
VisionRunningMode = mp.tasks.vision.RunningMode

options = PoseLandmarkerOptions(
    base_options=BaseOptions(model_asset_path=model_path),
    running_mode=VisionRunningMode.IMAGE)


def get_landmarks(numpy_image):
    with PoseLandmarker.create_from_options(options) as landmarker:
        # mp_image = mp.Image.create_from_file('bplb.jpeg')
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=numpy_image)

        pose_landmarker_result = landmarker.detect(mp_image)

        return pose_landmarker_result


        


def crop_portrait(input_image):
    height, width, _ = input_image.shape # its a bgr image


    rgb_image = cv2.cvtColor(input_image, cv2.COLOR_BGR2RGB)
    pose_landmarker_result = get_landmarks(rgb_image)

    # Convert normalized coordinates to pixel values
    pose_landmarks = pose_landmarker_result.pose_landmarks[0]
    nose_x, nose_y = int(pose_landmarks[0].x * width), int(pose_landmarks[0].y * height)
    shldr_left_x, shldr_left_y = int(pose_landmarks[12].x * width), int(pose_landmarks[12].y * height)
    shldr_right_x, shldr_right_y = int(pose_landmarks[11].x * width), int(pose_landmarks[11].y * height)



    top_left_x = int(max((shldr_left_x - shldr_left_x*0.15) , 0))
    bottom_right_x = int(min(shldr_right_x * 1.15, width))

    top_margin = int(nose_y - abs(shldr_right_y - nose_y) * 1.8 ) 
    top_left_y = max(top_margin, 0)

    bottom_margin = int(max(shldr_left_y, shldr_right_y) * 1.4) 
    bottom_right_y = min(bottom_margin, height)


    # Crop the image
    cropped_image = input_image[top_left_y:bottom_right_y, top_left_x:bottom_right_x]
    cropped_image = Image.fromarray(cv2.cvtColor(cropped_image, cv2.COLOR_BGR2RGB))

    return cropped_image 















