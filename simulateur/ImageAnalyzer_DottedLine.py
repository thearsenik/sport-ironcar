import cv2
import numpy as np
import time
from PIL import Image
from pathlib import Path
import commonVideo as commonVideo
import commonTraitement as utils
import logging
import config

font = cv2.FONT_HERSHEY_SIMPLEX

previousAngle = 90
previousDistance = 0
previousHauteur = 0
NB_ITERATIONS = 10000

logging.basicConfig(filename=config.logFile,level=config.logLevelPlayer, format='%(asctime)s %(message)s')

def _detectAngleAndDistance(frame):
    global previousAngle
    global previousDistance
    global previousHauteur
    
    # Convert to birdeye
    #logging.debug("ImageAnalyzer : Convert to birdeye start. ")
    vueDessus = utils.perspective_warp(frame, (config.IMG_WIDTH,config.IMG_HEIGHT))
    #logging.debug("ImageAnalyzer : Convert to birdeye end. ")
    
    # Convert BGR to HSV
    #logging.debug("ImageAnalyzer :BGR to HSV start. ")
    hsv = cv2.cvtColor(vueDessus, cv2.COLOR_BGR2HSV)
    #logging.debug("ImageAnalyzer :BGR to HSV end. ")

    # define range of blue color in HSV
    lower_yellow = np.array([0,69,94])
    upper_yellow = np.array([255,255,255])


    # Threshold the HSV image to get only blue colors
    #logging.debug("ImageAnalyzer : inRange start. ")
    mask = cv2.inRange(hsv, lower_yellow, upper_yellow)
    #logging.debug("ImageAnalyzer : inRange end. ")
    #output = Image.fromarray(mask)
    #output.save("D:/dev/ironcar/output/mask.png")
    #logging.debug("ImageAnalyzer : remove_noise start. ")
    noiseless = utils.remove_noise(mask,2,2)
    #logging.debug("ImageAnalyzer : remove_noise end. ")
    #output = Image.fromarray(noiseless)
    #output.save("D:/dev/ironcar/output/noiseless.png")

    # Bitwise-AND mask and original image
    #logging.debug("ImageAnalyzer : threshold start. ")
    ret, thresh = cv2.threshold(noiseless, 127, 255,0)
    #logging.debug("ImageAnalyzer : threshold end. ")
    #output = Image.fromarray(thresh)
    #output.save("D:/dev/ironcar/output/thresh.png")
    #logging.debug("ImageAnalyzer : findContours start. ")

    # contours can be included the one into the others, to get only outer contour
    # we use RETR_EXTERNAL
    # if we use CHAIN_APPROX_NONE : all points of the contour are returned
    # if we use CHAIN_APPROX_SIMPLE : only boundary point are provided
    contours,hierarchy = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    #logging.debug("ImageAnalyzer : findContours end. ")
    
    #logging.debug("ImageAnalyzer : filtrage contours start. ")
    pointilles = []
    if(len(contours)>0):
        contour = max(contours, key=cv2.contourArea)
        # minAreaRect returns a Box2D structure which contains 
        # ( center (x,y), (width, height), angle of rotation ).
        rectMax = cv2.minAreaRect(contour)
        print (rectMax)
        
        
        #contour le plus haut
        # //on ne prend que celui dont la taille est superieure a max/2 afin de filtrer les bouts de 
        # //pointille qui apparaissent et dont le calcul de l'angle est hazardeux...
        # minAreaRect returns a Box2D structure which contains 
        # ( center (x,y), (width, height), angle of rotation ).
        rects = [cv2.minAreaRect(forme) for forme in contours]
        #aireMin = rectMax[1][0]*rectMax[1][1]/2
        #contoursEntiers = [rect for rect in rects if rect[1][0]*rect[1][1] >= aireMin]
        contoursEntiers = rects
        contoursBottomToTop = sorted(contoursEntiers, key=lambda rect: rect[0][1], reverse=True)
        #print(str(len(contours))+" contours dont "+str(len(contoursBottomToTop))+" entiers")
        for i, contourRect in enumerate(contoursBottomToTop):
            rect = contourRect
            angle = utils.getAngle(rect)
            distance = utils.getDistance(rect)
            hauteur = utils.getHauteur(rect)
            pointille = [angle, distance, hauteur]
            pointilles.append(pointille)        
            if config.PRODUCE_DEBUG_IMG:
                box = cv2.boxPoints(rect)
                box = np.int0(box)
                #print("color="+str(min(i*60, 255)))
                cv2.drawContours(vueDessus,[box], 0,(0,max(255-i*60, 0),min(i*60, 255)),2)
                cv2.putText(vueDessus, str(angle),(vueDessus.shape[1] - 120, vueDessus.shape[0] - 60*i-10), font, 1,(0,max(255-i*60, 0),min(i*60, 255)),2,cv2.LINE_AA)

    #logging.debug("ImageAnalyzer : filtrage contours end. ")
    return vueDessus, pointilles


def getDetection(frame, numGame, numImg):
    
        
        #logging.debug("ImageAnalyzer : getDetection start. ")
        # get angle from image
        frame2, pointilles = _detectAngleAndDistance(frame)
        
        # For debug, save inputImage with detection and angle
        if config.PRODUCE_DEBUG_IMG:
            logging.debug("ImageAnalyzer : output debug start. ")
            frame = commonVideo.concat_images(frame, frame2)
            output = Image.fromarray(frame)
            pngOutputFile = config.analyzerDebugDir+"/debugOutput"+str(numGame).zfill(5)+'_'+str(numImg).zfill(5)+'.png'
            output.save(pngOutputFile)
            logging.debug("ImageAnalyzer : output debug end: "+pngOutputFile)
        
        #On attend un peu que blender nous fasse un rendu...
        #print("new image done : "+str(numImg))
        #time.sleep(0.1)
        #logging.debug("ImageAnalyzer : getDetection end. ")
        return pointilles

#make a video from images
#firstNumImg=1
#lastNumImg=NB_ITERATIONS
#imagePrefix='debugOutput'
#imagesSuffix=''
#imagesExtension='png'
#listImages = [imageDebugDir+'/'+imagePrefix+str(numImg).zfill(5)+imagesSuffix+'.'+imagesExtension for numImg in list(range(firstNumImg, lastNumImg+1))]
#commonVideo.video_from_images(listImages, config.videoDebugDir, 24)


