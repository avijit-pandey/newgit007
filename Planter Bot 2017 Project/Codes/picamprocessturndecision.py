# -*- coding: utf-8 -*-
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
#threshImages = q(int(settings.get('SectionSeven','NumQs')))
#contourImages = q(int(settings.get('SectionSeven','NumQs')))
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
        self.rc = PiRGBArray(self.cam,self.cam.resolution)

    def run(self):
        global frames
        #start_time = datetime.datetime.now()
        while True:
            self.cam.capture(self.rc,format='bgr',use_video_port=True,splitter_port=2,resize=self.cam.resolution)
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
                #print gImage.max(), gImage.min()
                #mImage = cv2.medianBlur(gImage,5)
                ret, self.threshImage = cv2.threshold(gImage,int(gImage.max()/2),int(settings.get('SectionThree','MaxWhite')),cv2.THRESH_BINARY_INV)
                #print ret
                projImages.put(self.threshImage)
                #threshImages.put(self.threshImage)

class processImage(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.lenVector = int(settings.get('SectionFour','ZoneColsStop')) - int(settings.get('SectionFour','ZoneColsStart'))
        self.vectorOfZeros = np.zeros((self.lenVector,1),np.uint8)

    def run(self):
        global projImages
        #global contourImages
        while True:
            if(not projImages.empty()):
                self.image = projImages.get()
                #print self.image
                #self.bw_inv = cv2.bitwise_not(self.image)
                self.im, self.contours, self.heirarchy = cv2.findContours(self.image,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)
                if(len(self.contours) > 1):
                    c_max = max(self.contours,key=cv2.contourArea)
                    c_moment = cv2.moments(c_max)
                    self.cx = int(c_moment['m10']/c_moment['m00'])
                    self.cy = int(c_moment['m01']/c_moment['m00'])
                    x,y,w,h = cv2.boundingRect(c_max)
                #contourImages.put(([(c_x,x,w),self.im]))
                self.id = self.projection()
                self.midptx = int(settings.get('SectionOne','ResCols'))/2

                #print self.midpt
                if(self.id == 0): 
                    motorControlq.put(0)
                    
                if(len(self.contours) > 1):
                    if(self.id == 1 and ((int(self.midptx) - self.cx) > 0)):
                        motorControlq.put(1)
                    if(self.id == 2 and ((int(self.midptx) - self.cx) < 0)):
                        motorControlq.put(2)
                else:
                    if(self.id == 1):
                        motorControlq.put(1)
                    if(self.id == 2):
                        motorControlq.put(2)

                if(self.id == 3):
                    motorControlq.put(3)

    def projection(self):
        self.image = cv2.bitwise_not(self.im)
        #cv2.imshow("threshold image", self.im)
        #cv2.waitKey(1)
        #print self.image
        for cols in range(0,self.lenVector):
            vectorI = self.image[:,cols]
            vI = np.array(vectorI,np.uint8)
            #print np.sum(vI,axis=0)
            self.vectorOfZeros[cols] = self.lenVector-(np.sum(vI,axis=0)/int(settings.get('SectionThree','MaxWhite')))
            #break
        if(np.count_nonzero(self.vectorOfZeros) > 0):
            sa1 = self.vectorOfZeros[int(settings.get('SectionFour','ZoneColsStart')):int(settings.get('SectionFive','Zone1'))]
            sa2 = self.vectorOfZeros[int(settings.get('SectionFive','Zone1')):int(settings.get('SectionFive','Zone2'))]
            sa3 = self.vectorOfZeros[int(settings.get('SectionFive','Zone2')):int(settings.get('SectionFive','Zone3'))]
            #print sa1
            sl = np.sum(sa1,axis=0)
            sf = np.sum(sa2,axis=0)
            sr = np.sum(sa3,axis=0)
            #print sf,sl,sr
            sumArr = np.array([sf,sl,sr],np.uint8)
            #print sumArr
            maxVal = sumArr.max()
            #print maxVal
            idx = np.argmax(sumArr)
            #print idx
            return idx
        else:
            return 3

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
    pi = processImage()
    mc = motorControl()
    di = displayImage()

    grabber.start()
    ie.start()
    pp.start()
    pi.start()
    mc.start()
    di.start()
    
    di.join()
    mc.join()
    pi.join()
    ppjoin()
    ie.join()
    grabber.join()

if __name__ == "__main__":
    startUp()
