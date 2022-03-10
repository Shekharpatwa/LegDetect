
import cv2 as cv

from home.frameoperations import FrameOperations
from home.poseEstimator import PoseEstimator

class VideoImgManager():

    def __init__(self,webcam_id=0):
        self.POSE_ESTIMATOR = PoseEstimator()
        self.video = cv.VideoCapture(webcam_id)

        self.FIRST = True

    def __del__(self):
            self.video.release()

    def estimate_vid(self):
        """reads webcam, applies pose estimation on webcam"""

        while(True):
            has_frame, frame = self.video.read()
            
            if self.FIRST:
                self.WEB_CAM_H,self.WEB_CAM_W = frame.shape[0:2]
                self.FIRST = False

            frame = self.POSE_ESTIMATOR.get_pose_key_angles(frame)

            has_frame,jpg=cv.imencode('.jpg',frame)
            return jpg.tobytes()
            
            

            
        
            
    
    