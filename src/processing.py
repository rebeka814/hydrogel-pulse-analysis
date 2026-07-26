import numpy as np
import cv2

def extract_signal(video_path, x, y, w, h):
    my_video  = cv2.VideoCapture(video_path)
    fps = my_video.get(cv2.CAP_PROP_FPS)
    intensity = []

    while my_video.isOpened():
        ret, frame = my_video.read()
        if ret == False:
           break
        gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        intensity.append(np.mean(gray_frame[x:x+w, y:y+h]))

    my_video.release()
    return np.array(intensity), fps

