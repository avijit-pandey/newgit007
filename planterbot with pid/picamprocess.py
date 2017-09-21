import cv2
import numpy as np
import threading
import time
import datetime
import os
from multiprocessing import Queue as q
import picamera
from picamera.array import PiRGBArray
from picamera import PiCamera
import RPi.GPIO as rgp
import ConfigParser as configp

settings = configp.ConfigParser()
settings.read('Config.ini')

frames = q(int(settings.get('SectionSeven','NumQs')))
jpgImages = q(int(settings.get('SectionSeven','NumQs')))
dispImages = q(int(settings.get('SectionSeven','NumQs')))
projImages = q(int(settings.get('SectionSeven','NumQs')))
motorControlq = q(int(settings.get('SectionSeven','NumQs')))

rgp.setmode(rgp.BOARD)
rgp.setup(int(settings.get('SectionSix','LeftPin')),rgp.OUT)
rgp.setup(int(settings.get('SectionSix','RightPin')),rgp.OUT)

#ImageGrabber code courtesy: http://answers.opencv.org/question/12081/python-frame-grabbing-from-ip-camera-and-process-in-a-different-thread/
class ImageGrabber(threading.Thread):
    def __init__(self, ID):
        threading.Thread.__init__(self)
        self.ID=ID
        self.cam=PiCamera()
        self.cam.framerate = int(settings.get('SectionOne','FrameRate'))
        self.cam.resolution = (int(settings.get('SectionOne','ResCols')),int(settings.get('SectionOne','ResRows')))
        self.rc = PiRGBArray(self.cam,(int(settings.get('SectionOne','ResCols')),int(settings.get('SectionOne','ResRows'))))

    def run(self):
        global frames
        #start_time = datetime.datetime.now()
        while True:
            self.cam.capture(self.rc,format='bgr',use_video_port=True,splitter_port=2,resize=(int(settings.get('SectionOne','ResCols')),int(settings.get('SectionOne','ResRows'))))
            frame = self.rc.array
            frames.put(frame)
            #time.sleep(0.01)
            self.rc.truncate(0)
            #end_time = datetime.datetime.now()
            #file = open("timestamp.txt",'a')
            #file.write("%s\n"%(end_time-start_time))
            #file.close()

class ImageEncoder(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
    def run(self):
        global frames
        global jpgImages
        global dispImages
        while True:
            if(not frames.empty()):
                s =frames.get()
                ret, se = cv2.imencode('.jpg',s,[int(cv2.IMWRITE_JPEG_QUALITY),int(settings.get('SectionTwo','JPGQuality'))])
                jpgImages.put(se)
                dispImages.put(se)

class preProcessImage(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)

    def run(self):
        global dispImages
        global projImages
        while True:
            if(not dispImages.empty()):
                s =dispImages.get()
                self.Currframe = cv2.imdecode(s,1)
                gImage = cv2.cvtColor(self.Currframe[int(settings.get('SectionFour','ZoneRowStart')):int(settings.get('SectionFour','ZoneRowStop')),int(settings.get('SectionFour','ZoneColsStart')):int(settings.get('SectionFour','ZoneColsStop')),:],cv2.COLOR_BGR2GRAY)
                #print gImage.max()
                mImage = cv2.medianBlur(gImage,5)
                ret, self.threshImage = cv2.threshold(gImage,int(settings.get('SectionThree','Threshold')),int(settings.get('SectionThree','MaxWhite')),cv2.THRESH_BINARY_INV)
                projImages.put(cv2.bitwise_not(self.threshImage))             

class computeProjection(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.lenVector = int(settings.get('SectionFour','ZoneColsStop')) - int(settings.get('SectionFour','ZoneColsStart'))
        self.vectorOfZeros = np.zeros((self.lenVector,1),np.uint8)
        
    def run(self):
        global projImages
        global motorControlq
        while True:
            if(not projImages.empty()):
                self.image = projImages.get()
                #print self.image.shape
                for cols in range(0,self.lenVector):
                    vectorI = self.image[:,cols]
                    vI = np.array(vectorI,np.uint8)
                    self.vectorOfZeros[cols] = self.lenVector-(np.sum(vI,axis=0)/int(settings.get('SectionThree','MaxWhite')))

                if(np.count_nonzero(self.vectorOfZeros) > 0):
                    sa1 = self.vectorOfZeros[0:int(settings.get('SectionFive','Zone1'))]
                    sa2 = self.vectorOfZeros[int(settings.get('SectionFive','Zone1')):int(settings.get('SectionFive','Zone2'))]
                    sa3 = self.vectorOfZeros[int(settings.get('SectionFive','Zone2')):int(settings.get('SectionFive','Zone3'))]
                    
                    s1 = np.sum(sa1,axis=0)
                    s2 = np.sum(sa2,axis=0)*3
                    s3 = np.sum(sa3,axis=0)
                    sumArr = np.array([s1,s2,s3],np.uint8)
                    #print sumArr
                    maxVal = sumArr.max()
                    #print maxVal
                    idx = np.argmax(sumArr)
                    motorControlq.put(idx)
                else:
                    motorControlq.put(3)

class motorControl(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        
    def run(self):
        global motorControlq
        while True:
            if(not motorControlq.empty()):
                self.mode = motorControlq.get()
                #print self.mode
                if(self.mode == 0):
                    #print "Forward"
                    rgp.output(int(settings.get('SectionSix','LeftPin')),rgp.HIGH)
                    rgp.output(int(settings.get('SectionSix','RightPin')),rgp.HIGH)
                if(self.mode==1):
                    #print "Left"
                    rgp.output(int(settings.get('SectionSix','LeftPin')),rgp.HIGH)
                    rgp.output(int(settings.get('SectionSix','RightPin')),rgp.LOW)
                if(self.mode==2):
                    #print "Right"
                    rgp.output(int(settings.get('SectionSix','LeftPin')),rgp.LOW)
                    rgp.output(int(settings.get('SectionSix','RightPin')),rgp.HIGH)
                if(self.mode==3):
                    #print "Stop"
                    rgp.output(int(settings.get('SectionSix','LeftPin')),rgp.LOW)
                    rgp.output(int(settings.get('SectionSix','RightPin')),rgp.LOW)
                    
class displayImage(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        
    def run(self):
        global jpgImages
        while True:
            if(not jpgImages.empty()):
                s =jpgImages.get()
                self.Currframe = cv2.imdecode(s,1)
                cv2.imshow("Vid feed", self.Currframe)
                cv2.waitKey(1)


def startUp():
    
    grabber = ImageGrabber(0)
    ie = ImageEncoder()
    pp = preProcessImage()
    cp = computeProjection()
    mc = motorControl()
    di = displayImage()

    grabber.start()
    ie.start()
    pp.start()
    cp.start()
    mc.start()
    di.start()
    
    di.join()
    mc.join()
    cp.join()
    ppjoin()
    ie.join()
    grabber.join()

if __name__ == "__main__":
    startUp()
