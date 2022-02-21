
import cv2 as cv

from home.frameoperations import FrameOperations
from home.poseEstimator import PoseEstimator

class VideoImgManager():

    def __init__(self):
        self.POSE_ESTIMATOR = PoseEstimator()
        self.FRAME_OPS = FrameOperations()

        self.FIRST = True

    def estimate_vid(self,webcam_id=0):
        """reads webcam, applies pose estimation on webcam"""
        cap = cv.VideoCapture(webcam_id)

        while(True):
            has_frame, frame = cap.read()

            if self.FIRST:
                self.WEB_CAM_H,self.WEB_CAM_W = frame.shape[0:2]
                self.FIRST = False

            frame = self.POSE_ESTIMATOR.get_pose_key_angles(frame)

            cv.imshow('frame',frame)
            if cv.waitKey(1) & 0xFF == ord('q'):
                break
    
    def estimate_img(self,img_path):
        """applies pose estimation on img"""

        img = cv.imread(img_path)

        img = self.POSE_ESTIMATOR.get_pose_key_angles(img)
        
        #cv.imshow("Image Pose Estimation",img)
        def rescaleFrame(frame, scale=0.7):
            width = int(frame.shape[1] * scale)
            height = int(frame.shape[0] * scale)
            dimensions = (width,height)

            return cv.resize(frame,dimensions, interpolation=cv.INTER_AREA)
        resized_image = rescaleFrame(img)
        cv.imshow('Image', resized_image)

        cv.waitKey(0)
        cv.destroyAllWindows()
