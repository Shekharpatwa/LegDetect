import cv2 as cv
import numpy as np
import os
import math
#manually done
from django.conf import settings


#class to contain some operations to try on frame
class FrameOperationss():

    def __init__(self):
        self.CWD = os.getcwd()
        self.RES_F = os.path.join(self.CWD,'resources')
        self.FILTER_F = os.path.join(self.RES_F,'FILTERS')
        self.SPEED_FILTER = cv.imread(os.path.join(self.FILTER_F,"SPEED.png"))
        self.CONT_FILTER = cv.imread(os.path.join(self.FILTER_F,"CONTINUE.png"))


    def average_blur(self,frame,kernel_size):
        conversion = cv.blur(frame,kernel_size)
        return conversion
    
    def gauss_blur(self,frame, kernel_size,sigX):
        conversion = cv.GaussianBlur(frame,kernel_size,sigX)
        return conversion

    def convert_scale_abs(self,frame, alpha, beta):
        """alpha must be float, beta must be int!"""
        #alpha for contrast control, beta for brightness control

        conversion = cv.convertScaleAbs(frame,alpha=alpha,beta=beta)

        return conversion

    def contrast_brightness(self,frame,brightness,contrast):

        conversion = np.int16(frame)
        conversion = conversion * (contrast/127+1) - contrast + brightness
        conversion = np.clip(conversion,0,255)
        # unsigned int
        conversion = np.uint8(conversion)

        return conversion

    def clahe(self,frame):
        # CLAHE (Contrast Limited Adaptive Histogram Equalization)
        clahe = cv.createCLAHE(clipLimit=3., tileGridSize=(8,8))

        lab = cv.cvtColor(frame, cv.COLOR_BGR2LAB)  # convert from BGR to LAB color space
        l, a, b = cv.split(lab)  # split on 3 different channels

        l2 = clahe.apply(l)  # apply CLAHE to the L-channel

        lab = cv.merge((l2,a,b))  # merge channels
        conversion = cv.cvtColor(lab, cv.COLOR_LAB2BGR)  # convert from LAB to BGR

        return conversion

    def increase_red(self,frame):
        B,G,R = cv.split(frame)
        B = self.contrast_brightness(B,10,10)
        G = self.contrast_brightness(G,1,1)
        R = self.contrast_brightness(R,1000,1000)


        # merge B,G,R
        higher_red = cv.merge([B,G,R])

        return higher_red

    def apply_filters(self,frame):
        frame_h,frame_w = frame.shape[:2]

        trans_mask = self.CONT_FILTER[:,:,2] == 0
        self.CONT_FILTER[trans_mask] = [-1,-1,-1]

        self.CONT_FILTER = cv.resize(self.CONT_FILTER,(frame_w,frame_h),interpolation=cv.INTER_LINEAR)
        self.SPEED_FILTER = cv.resize(self.SPEED_FILTER,(frame_w,frame_h),interpolation=cv.INTER_LINEAR)

        filtered = cv.addWeighted(frame,1,self.CONT_FILTER,0.3,-15)
        filtered = cv.addWeighted(filtered,0.7,self.SPEED_FILTER,0.3,-15)

        return filtered


    def found_frame_operation(self,frame):
        """Performs all operations on the found frame
        Use if you want to test out multiple options"""

        frame = self.apply_filters(frame)


        return frame

#FO = FrameOperations()
#path = "my_did_it.png"
#img = cv.imread(path)

#img = FO.found_frame_operation(img)

#cv.imshow('in',img)
#cv.waitKey(0)


class PoseEstimators():

    def __init__(self):
        self.FRAME_OPS = FrameOperationss()


        self.BODY_PARTS =  { "Nose": 0, "Neck": 1, "RShoulder": 2, "RElbow": 3, "RWrist": 4,
               "LShoulder": 5, "LElbow": 6, "LWrist": 7, "RHip": 8, "RKnee": 9,
               "RAnkle": 10, "LHip": 11, "LKnee": 12, "LAnkle": 13, "REye": 14,
               "LEye": 15, "REar": 16, "LEar": 17, "Background": 18 }
            
        self.POSE_PAIRS = [ ["Neck", "RShoulder"], ["Neck", "LShoulder"], ["RShoulder", "RElbow"],
               ["RElbow", "RWrist"], ["LShoulder", "LElbow"], ["LElbow", "LWrist"],
               ["Neck", "RHip"], ["RHip", "RKnee"], ["RKnee", "RAnkle"], ["Neck", "LHip"],
               ["LHip", "LKnee"], ["LKnee", "LAnkle"], ["Neck", "Nose"], ["Nose", "REye"],
               ["REye", "REar"], ["Nose", "LEye"], ["LEye", "LEar"] ]

        self.CWD = os.getcwd()
        self.RESOURCES = os.path.join(self.CWD,'resources')
        self.GRAPH_OPT = os.path.join(self.RESOURCES,'graph_opt.pb')

        self.NET = cv.dnn.readNetFromTensorflow(self.GRAPH_OPT)
        self.THR = 0.1
        self.IN_WIDTH = 396
        self.IN_HEIGHT = 368

        self.POINTS = []

        # key angles: RightArm is the angle between Rshoulder, RElbow,RWrist
        # note for some calcs we can reuse the same connects!
        self.KEY_DISTANCES = {"RArm":{"RShoulder-RElbow":None,"RElbow-RWrist":None,"Neck-RShoulder":None},
        "LArm":{"LShoulder-LElbow":None,"LElbow-LWrist":None,"Neck-LShoulder":None},
        "RLeg":{"RHip-RKnee":None,"RKnee-RAnkle":None},
        "LLeg":{"LHip-RKnee":None,"LKnee-RAnkle":None}}

        self.KEY_ANGLES = {"RArm": [],"LArm":[],"RLeg":[],"LLeg":[]}

        self.TEXT_COLOR = (0,0,0)

    def rad_to_deg(self,rad):
        return rad * (180/math.pi)

    def get_pose_key_angles(self, frame, wantBlank = False):
        """applies pose estimation on frame, gets the distances between points"""

        # for the key points that do not come in pairs
        RShoulder_pos = None
        RWrist_pos = None

        LShoulder_pos = None
        LWrist_pos = None

        Neck_pos = None
        
        RElbow_pos = None
        LElbow_pos = None

        RHip_pos = None
        RKnee_pos = None
        RAnkle_pos = None

        LHip_pos = None
        LKnee_pos = None
        LAnkle_pos = None


        frame_h,frame_w = frame.shape[0:2]
            
        self.NET.setInput(cv.dnn.blobFromImage(frame, 1.0, (self.IN_WIDTH, self.IN_HEIGHT), (127.5, 127.5, 127.5), swapRB=True, crop=False))
        out = self.NET.forward()

        out = out[:, :19, :, :]  # MobileNet output [1, 57, -1, -1], we only need the first 19 elements

        assert(len(self.BODY_PARTS) == out.shape[1])

        #clear to get new points
        self.POINTS.clear()

        for i in range(len(self.BODY_PARTS)):
            # Slice heatmap of corresponging body's part.
            heatMap = out[0, i, :, :]

            # Originally, we try to find all the local maximums. To simplify a sample
            # we just find a global one. However only a single pose at the same time
            # could be detected this way.
            _, conf, _, point = cv.minMaxLoc(heatMap)
            x = (frame_w * point[0]) / out.shape[3]
            y = (frame_h * point[1]) / out.shape[2]

            # Add a point if it's confidence is higher than threshold.
            if(conf > self.THR):
                self.POINTS.append((int(x),int(y)))
            else:
                self.POINTS.append(None)

        # create blank frame overlay once OpenPose has read original frame so as to work
        if wantBlank:

            frame = np.zeros((frame_h,frame_w,3),np.uint8)

            self.TEXT_COLOR = (255,255,255)

        for pair in self.POSE_PAIRS:
            # ex: pair 1: [["Neck","RShoulder"]]
            # partFrom = Neck, partTo = RShoulder
            partFrom = pair[0]
            partTo = pair[1]
            assert(partFrom in self.BODY_PARTS)
            assert(partTo in self.BODY_PARTS)

            # continuing ex: idFrom = BODY_PART["Neck"] returns 1
            # similarly, idTo = BODY_PARTS["RShoulder"] returns 2
            idFrom = self.BODY_PARTS[partFrom]
            idTo = self.BODY_PARTS[partTo]

            # if found points (if not found, returns None)
            if self.POINTS[idFrom] and self.POINTS[idTo]:
                

                # now we check each of the key points.
                # "a", "b" correspond to the lengths of the limbs, "c" is the length between the end dots on the triangle. See video.
                # we use law of cosines to find angle c: 
                # cos(C) = (a^2 + b^2 - c^2) / 2ab
                # we first check for the points that do not come in pairs (make up the longest side of the triangle in the vid)

                if(partFrom == "RShoulder"):
                    RShoulder_pos = self.POINTS[idFrom]

                if(partTo == "RWrist"):
                    RWrist_pos = self.POINTS[idTo]

                if(partFrom == "LShoulder"):
                    LShoulder_pos = self.POINTS[idFrom]

                if(partTo == "LWrist"):
                    LWrist_pos = self.POINTS[idTo]

                if(partFrom == "Neck"):
                    Neck_pos = self.POINTS[idFrom]
                
                if(partTo == "RElbow"):
                    RElbow_pos = self.POINTS[idTo]

                if(partTo == "LElbow"):
                    LElbow_pos = self.POINTS[idTo]

                if(partFrom == "RHip"):
                    RHip_pos = self.POINTS[idFrom]
                
                if(partTo == "RKnee"):
                    RKnee_pos = self.POINTS[idTo]
                
                if(partTo == "RAnkle"):
                    RAnkle_pos = self.POINTS[idTo]
                    
                if(partFrom == "LHip"):
                    LHip_pos = self.POINTS[idFrom]
                
                if(partTo == "LKnee"):
                    LKnee_pos = self.POINTS[idTo]
                
                if(partTo == "LAnkle"):
                    LAnkle_pos = self.POINTS[idTo]


                # START (R) Shoulder -> Elbow -> Wrist

                if(partFrom == "RShoulder" and partTo == "RElbow"):
                    dist_2 = (self.POINTS[idFrom][0] - self.POINTS[idTo][0]) **2 + (self.POINTS[idFrom][1] - self.POINTS[idTo][1]) **2
                    self.KEY_DISTANCES["RArm"]["RShoulder-RElbow"] = dist_2

                elif(partFrom == "RElbow" and partTo == "RWrist"):
                    dist_2 = (self.POINTS[idFrom][0] - self.POINTS[idTo][0]) **2 + (self.POINTS[idFrom][1] - self.POINTS[idTo][1]) **2
                    self.KEY_DISTANCES["RArm"]["RElbow-RWrist"] = dist_2

                # END (R) Shoulder -> Elbow -> Wrist

                # START (L) Shoulder -> Elbow -> Wrist

                elif(partFrom == "LShoulder" and partTo == "LElbow"):
                    dist_2 = (self.POINTS[idFrom][0] - self.POINTS[idTo][0]) **2 + (self.POINTS[idFrom][1] - self.POINTS[idTo][1]) **2
                    self.KEY_DISTANCES["LArm"]["LShoulder-LElbow"] = dist_2

                elif(partFrom == "LElbow" and partTo == "LWrist"):
                    dist_2 = (self.POINTS[idFrom][0] - self.POINTS[idTo][0]) **2 + (self.POINTS[idFrom][1] - self.POINTS[idTo][1]) **2
                    self.KEY_DISTANCES["LArm"]["LElbow-LWrist"] = dist_2

                # END (L) Shoulder -> Elbow -> Wrist

                # START (R) Neck -> Shoulder -> Elbow, (L) Neck -> Shoulder -> Elbow
                # note we have already gotten Shoulder-Elbow values!

                elif(partFrom == "Neck" and partTo == "RShoulder"):
                    dist_2 = (self.POINTS[idFrom][0] - self.POINTS[idTo][0]) **2 + (self.POINTS[idFrom][1] - self.POINTS[idTo][1]) **2
                    self.KEY_DISTANCES["RArm"]["Neck-RShoulder"] = dist_2

                elif(partFrom == "Neck" and partTo == "LShoulder"):
                    dist_2 = (self.POINTS[idFrom][0] - self.POINTS[idTo][0]) **2 + (self.POINTS[idFrom][1] - self.POINTS[idTo][1]) **2
                    self.KEY_DISTANCES["LArm"]["Neck-LShoulder"] = dist_2

                # END (R) Neck -> Shoulder -> Elbow, (L) Neck -> Shoulder -> Elbow

                # START (R) Hip -> Knee -> Ankle
                
                elif(partFrom == "RHip" and partTo == "RKnee"):
                    dist_2 = (self.POINTS[idFrom][0] - self.POINTS[idTo][0]) **2 + (self.POINTS[idFrom][1] - self.POINTS[idTo][1]) **2
                    self.KEY_DISTANCES["RLeg"]["RHip-RKnee"] = dist_2

                elif(partFrom == "RKnee" and partTo == "RAnkle"):
                    dist_2 = (self.POINTS[idFrom][0] - self.POINTS[idTo][0]) **2 + (self.POINTS[idFrom][1] - self.POINTS[idTo][1]) **2
                    self.KEY_DISTANCES["RLeg"]["RKnee-RAnkle"] = dist_2

                # END (R) Hip -> Knee -> Ankle

                # START (L) Hip -> Knee -> Ankle
                
                elif(partFrom == "LHip" and partTo == "LKnee"):
                    dist_2 = (self.POINTS[idFrom][0] - self.POINTS[idTo][0]) **2 + (self.POINTS[idFrom][1] - self.POINTS[idTo][1]) **2
                    self.KEY_DISTANCES["LLeg"]["LHip-LKnee"] = dist_2

                elif(partFrom == "LKnee" and partTo == "LAnkle"):
                    dist_2 = (self.POINTS[idFrom][0] - self.POINTS[idTo][0]) **2 + (self.POINTS[idFrom][1] - self.POINTS[idTo][1]) **2
                    self.KEY_DISTANCES["LLeg"]["LKnee-LAnkle"] = dist_2



                # check if you want to return just the blank, or the image with the angles.

                cv.line(frame, self.POINTS[idFrom], self.POINTS[idTo], (0, 255, 0), 3) #last value is thickness
                cv.ellipse(frame, self.POINTS[idFrom], (3, 3), 0, 0, 360, (0, 0, 255), cv.FILLED)
                cv.ellipse(frame, self.POINTS[idTo], (3, 3), 0, 0, 360, (0, 0, 255), cv.FILLED)
                

        # we get the angles at the end.
        if(RShoulder_pos is not None and RWrist_pos is not None):

            c_2 = (RShoulder_pos[0] - RWrist_pos[0])**2 + (RShoulder_pos[1] - RWrist_pos[1])**2

            a_2 = self.KEY_DISTANCES["RArm"]["RShoulder-RElbow"]
            b_2 = self.KEY_DISTANCES["RArm"]["RElbow-RWrist"]

            # because degrees are easily to visualize for me:
            try:
                theta = self.rad_to_deg(math.acos((a_2 + b_2 - c_2)/(2*math.sqrt(a_2*b_2))))

            except ZeroDivisionError:
                theta = "Error"

            self.KEY_ANGLES["RArm"].append(theta)

            # display the angle at the center joint. Use self.BODY_PARTS to find joint indices
            
            if(theta is not None):
                cv.putText(frame,"{:.1f}".format(theta),self.POINTS[3],cv.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255))
        
        if(LShoulder_pos is not None and LWrist_pos is not None):

            c_2 = (LShoulder_pos[0] - LWrist_pos[0])**2 + (LShoulder_pos[1] - LWrist_pos[1])**2

            a_2 = self.KEY_DISTANCES["LArm"]["LShoulder-LElbow"]
            b_2 = self.KEY_DISTANCES["LArm"]["LElbow-LWrist"]

            # because degrees are easily to visualize for me:
            try:
                theta = self.rad_to_deg(math.acos((a_2 + b_2 - c_2)/(2*math.sqrt(a_2*b_2))))

            except ZeroDivisionError:
                theta = None

            self.KEY_ANGLES["LArm"].append(theta)

            # display the angle at the center joint. Use self.BODY_PARTS to find joint indices

            if(theta is not None):
                cv.putText(frame,"{:.1f}".format(theta),self.POINTS[6],cv.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255))

        if(Neck_pos is not None and LElbow_pos is not None):

            c_2 = (Neck_pos[0] - LElbow_pos[0])**2 + (Neck_pos[1] - LElbow_pos[1])**2

            a_2 = self.KEY_DISTANCES["LArm"]["Neck-LShoulder"]
            b_2 = self.KEY_DISTANCES["LArm"]["LShoulder-LElbow"]

            # because degrees are easily to visualize for me:
            try:
                theta = self.rad_to_deg(math.acos((a_2 + b_2 - c_2)/(2*math.sqrt(a_2*b_2))))

            except ZeroDivisionError:
                theta = None
            self.KEY_ANGLES["LArm"].append(theta)

            # display the angle at the center joint. Use self.BODY_PARTS to find joint indices
            if(theta is not None):
                cv.putText(frame,"{:.1f}".format(theta),self.POINTS[5],cv.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255))

        if(Neck_pos is not None and RElbow_pos is not None):

            c_2 = (Neck_pos[0] - RElbow_pos[0])**2 + (Neck_pos[1] - RElbow_pos[1])**2

            a_2 = self.KEY_DISTANCES["RArm"]["Neck-RShoulder"]
            b_2 = self.KEY_DISTANCES["RArm"]["RShoulder-RElbow"]

            # because degrees are easily to visualize for me:
            try:
                theta = self.rad_to_deg(math.acos((a_2 + b_2 - c_2)/(2*math.sqrt(a_2*b_2))))

            except ZeroDivisionError:
                theta = None

            self.KEY_ANGLES["RArm"].append(theta)

            # display the angle at the center joint. Use self.BODY_PARTS to find joint indices

            if(theta is not None):
                cv.putText(frame,"{:.1f}".format(theta),self.POINTS[2],cv.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255))

        if(RHip_pos is not None and RAnkle_pos is not None):

            c_2 = (RHip_pos[0] - RAnkle_pos[0])**2 + (RHip_pos[1] - RAnkle_pos[1])**2

            a_2 = self.KEY_DISTANCES["RLeg"]["RHip-RKnee"]
            b_2 = self.KEY_DISTANCES["RLeg"]["RKnee-RAnkle"]

            # because degrees are easily to visualize for me:
            try:
                theta = self.rad_to_deg(math.acos((a_2 + b_2 - c_2)/(2*math.sqrt(a_2*b_2))))
                print(theta)

            except ZeroDivisionError:
                theta = None

            self.KEY_ANGLES["RLeg"].append(theta)

            # display the angle at the center joint. Use self.BODY_PARTS to find joint indices

            if(theta is not None):
                cv.putText(frame,"{:.1f}".format(theta),self.POINTS[9],cv.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255))

        if(LHip_pos is not None and LAnkle_pos is not None):

            c_2 = (LHip_pos[0] - LAnkle_pos[0])**2 + (LHip_pos[1] - LAnkle_pos[1])**2

            a_2 = self.KEY_DISTANCES["LLeg"]["LHip-LKnee"]
            b_2 = self.KEY_DISTANCES["LLeg"]["LKnee-LAnkle"]

            # because degrees are easily to visualize for me:
            try:
                theta = self.rad_to_deg(math.acos((a_2 + b_2 - c_2)/(2*math.sqrt(a_2*b_2))))
                print(theta)


            except ZeroDivisionError:
                theta = None

            self.KEY_ANGLES["LLeg"].append(theta)

            # display the angle at the center joint. Use self.BODY_PARTS to find joint indices

            if(theta is not None):
                cv.putText(frame,"{:.1f}".format(theta),self.POINTS[12],cv.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255))


        t, _ = self.NET.getPerfProfile()
        freq = cv.getTickFrequency() / 1000

        cv.putText(frame, '%.2fms' % (t / freq), (10, 20), cv.FONT_HERSHEY_SIMPLEX, 0.5, self.TEXT_COLOR)

        return frame



class VideoImgManagers():

    def __init__(self,webcam_id=1):
        self.POSE_ESTIMATOR = PoseEstimators()
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
            
    
   
