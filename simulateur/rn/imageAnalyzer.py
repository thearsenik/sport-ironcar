import cv2
import numpy as np
import time
from PIL import Image
from pathlib import Path
import os
import json
import sys
sys.path.insert(0, '../')
import commonVideo as commonVideo
import commonTraitement as utils
import pathConfig

font = cv2.FONT_HERSHEY_SIMPLEX

previousAngle = 90
previousDistance = 0
previousHauteur = 0
NB_ITERATIONS = 10000

def detectAngleAndDistance(frame):
    global previousAngle
    global previousDistance
    global previousHauteur
    
    # Convert to birdeye
    vueDessus = utils.perspective_warp(frame, (1200,900))
    
    # Convert BGR to HSV
    hsv = cv2.cvtColor(vueDessus, cv2.COLOR_BGR2HSV)

    # define range of blue color in HSV
    lower_yellow = np.array([0,69,94])
    upper_yellow = np.array([255,255,255])


    # Threshold the HSV image to get only blue colors
    mask = cv2.inRange(hsv, lower_yellow, upper_yellow)
    #output = Image.fromarray(mask)
    #output.save("D:/dev/ironcar/output/mask.png")
    noiseless = utils.remove_noise(mask)
    #output = Image.fromarray(noiseless)
    #output.save("D:/dev/ironcar/output/noiseless.png")

    # Bitwise-AND mask and original image
    ret, thresh = cv2.threshold(noiseless, 127, 255,0)
    #output = Image.fromarray(thresh)
    #output.save("D:/dev/ironcar/output/thresh.png")
    im2,contours,hierarchy = cv2.findContours(thresh, 1, 2)
    

    pointilles = []
    if(len(contours)>0):
        contour = max(contours, key=cv2.contourArea)
        rectMax = cv2.minAreaRect(contour)
        print (rectMax)
        
        
        #contour le plus bas dont taille superieure a max/2
        rects = [cv2.minAreaRect(forme) for forme in contours]
        aireMin = rectMax[1][0]*rectMax[1][1]/2
        contoursEntiers = [rect for rect in rects if rect[1][0]*rect[1][1] >= aireMin]
        contoursBottomToTop = sorted(contoursEntiers, key=lambda rect: rect[0][1], reverse=True)
        print(str(len(contours))+" contours dont "+str(len(contoursBottomToTop))+" entiers")
        for i, contourRect in enumerate(contoursBottomToTop):
            rect = contourRect
            angle = utils.getAngle(rect)
            distance = utils.getDistance(rect)
            hauteur = utils.getHauteur(rect)
            pointille = [angle, distance, hauteur]
            pointilles.append(pointille)        
            box = cv2.boxPoints(rect)
            box = np.int0(box)
            #print("color="+str(min(i*60, 255)))
            cv2.drawContours(vueDessus,[box], 0,(0,max(255-i*60, 0),min(i*60, 255)),2)
            cv2.putText(vueDessus, str(angle),(vueDessus.shape[1] - 120, vueDessus.shape[0] - 60*i-10), font, 1,(0,max(255-i*60, 0),min(i*60, 255)),2,cv2.LINE_AA)

        
    return vueDessus, pointilles


def getDetection(frame, numGame, numImg):

        # get angle from image
        frame2, pointilles = detectAngleAndDistance(frame)
        
        # For debug, save inputImage with detection and angle
        frame = commonVideo.concat_images(frame, frame2)
        output = Image.fromarray(frame)
        pngOutputFile = pathConfig.imageDebugDir+"/debugOutput"+str(numGame).zfill(5)+'_'+str(numImg).zfill(5)+'.png'
        output.save(pngOutputFile)
        
        #On attend un peu que blender nous fasse un rendu...
        print("new image done : "+str(numImg))
        time.sleep(0.1)
    
        return pointilles

#make a video from images
#firstNumImg=1
#lastNumImg=NB_ITERATIONS
#imagePrefix='debugOutput'
#imagesSuffix=''
#imagesExtension='png'
#listImages = [imageDebugDir+'/'+imagePrefix+str(numImg).zfill(5)+imagesSuffix+'.'+imagesExtension for numImg in list(range(firstNumImg, lastNumImg+1))]
#commonVideo.video_from_images(listImages, pathConfig.videoDebugDir, 24)


