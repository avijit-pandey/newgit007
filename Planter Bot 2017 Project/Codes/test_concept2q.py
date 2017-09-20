import cv2
import numpy as np
import threading
import time
import datetime
import os
from multiprocessing import Queue as q

frames = q(300)
jpgImages = q(300)
dispImages = q(300)

class ImageGrabber(threading.Thread):
    def __init__(self, ID):
        threading.Thread.__init__(self)
        self.ID=ID
        self.cam=cv2.VideoCapture(ID)
        self.cam.set(cv2.CAP_PROP_FPS,30)
        self.cam.set(3,640)
        self.cam.set(3,480)

    def run(self):
        global frames
        start_time = datetime.datetime.now()
        while True:
            ret,frame=self.cam.read()
            frames.put(frame)
            #time.sleep(0.01)
            end_time = datetime.datetime.now()
            file = open("C:\\Users\\Asus\\AppData\\Local\\Programs\\Python\\Python36\\Code\\timestamp.txt",'a')
            file.write("%s\n"%(end_time-start_time))
            file.close()

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
                ret, se = cv2.imencode('.jpg',s,[int(cv2.IMWRITE_JPEG_QUALITY),25])
                jpgImages.put(se)
                dispImages.put(se)

class preProcessImage(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)

    def run(self):
        global dispImages
        while True:
            if(not dispImages.empty()):
                s =dispImages.get()
                self.Currframe = cv2.imdecode(s,1)
                gImage = cv2.cvtColor(self.Currframe,cv2.COLOR_BGR2GRAY)
                thImage = cv2.threshold(gImage,127,255,cv2.THRESH_BINARY)
                cp = computeProjection(thImage)
                #arrProj = cp.getProj()

class computeProjection:
    def __init__(self,image):
        self.image = image
        
    def getProj(self):
        

class Main(threading.Thread):
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
    main = Main()

    grabber.start()
    ie.start()
    pp.start()
    main.start()
    
    main.join()
    ppjoin()
    ie.join()
    grabber.join()

if __name__ == "__main__":
    startUp()
