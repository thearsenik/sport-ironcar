import cv2
import numpy as np
import time
import commonVideo as commonVideo
import commonTraitement as utils
from PIL import Image
from pathlib import Path
import os
import json
from variables import *
import math

font = cv2.FONT_HERSHEY_SIMPLEX

# global var
previousAngle = 90
previousHauteur = 0

# constantes
NB_ITERATIONS = 3976

def detectAngleAndDistance(frame):
    global previousAngle
    global previousHauteur
    
    # Convert to birdeye
    vueDessus = utils.perspective_warp(frame, (1200,900))
    
    # Convert BGR to HSV
    hsv = cv2.cvtColor(vueDessus, cv2.COLOR_BGR2HSV)

    # define range of blue color in HSV
    lower_yellow = np.array([0,69,94])
    upper_yellow = np.array([255,255,255])
    
    lower_white = np.array([72,14,180])
    upper_white = np.array([255,44,255])


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
    
    # Threshold the HSV image to get only blue colors
    mask2 = cv2.inRange(hsv, lower_white, upper_white)
    noiseless2 = utils.remove_noise(mask2)
    ret, thresh2 = cv2.threshold(noiseless2, 127, 255,0)
    #thresh2 = cv2.adaptiveThreshold(thresh2, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV,11,2)
#    im3,contours2,hierarchy2 = cv2.findContours(thresh2, cv2.RETR_LIST, cv2.CHAIN_APPROX_NONE )
    im3 = cv2.cvtColor(thresh2, cv2.COLOR_GRAY2BGR)
    
    rects = contours
    if(len(rects)>0):        
        #contour le plus bas
        rects = [cv2.minAreaRect(forme) for forme in contours]
        
        rects = list(filter(lambda rect: not isBehindWhiteLine(rect, thresh2), rects))
        
    if (len(rects)>0):
        rect = utils.getContoursPlusEloigne(rects)
        angle = utils.getAnglePoints(rect[0], [600, 1277])
        hauteur = utils.getHauteur(rect) #hauteur en 0 et 1
        drawOtherRects(vueDessus, rects, rect)
    else:
        if (previousAngle < 90):
            angle = 0
        else :
            angle = 180
        hauteur = 0
        rect = None
        
    
    previousAngle = angle
    previousHauteur = hauteur
    
    direction, vitesse = getMoveInfos(angle, hauteur)
        
    drawContoursEtInfos(vueDessus, rect, direction, vitesse)
    return vueDessus, im3, direction, vitesse

def isBehindWhiteLine(rect, whiteLineImg):
    goalX = int(rect[0][0])
    goalY = int(rect[0][1])
    vx = goalX - 600
    vy = goalY - 900
    valMax = math.fabs(vx) + math.fabs(vy)
    ratioX = vx / valMax
    ratioY = vy / valMax
    i = 0
    while True:
        testX = 599 + int((ratioX *i) + 0.001)
        testY = 899 + int((ratioY *i) + 0.001)
        if math.fabs(goalX - testX) <= 2 and math.fabs(goalY - testY) <= 2:
            return False
        if whiteLineImg[testY, testX] == 255:
            return True
        i=i+1

def drawOtherRects(vueDessus, rects, ignoreRect):
    for rect in rects:
        if rect != ignoreRect:
            box = cv2.boxPoints(rect)
            box = np.int0(box)
            cv2.drawContours(vueDessus,[box], 0,(255,0,0),1)
            

def getMoveInfos(angle, hauteur):
    hInverse = 1 - hauteur
    if math.fabs(angle -90) > 10:
        direction = ((angle - 90) / 50) * (1 + hInverse)
    else:
        direction = 0
    if (direction > 1):
        direction = 1
    else:
        if (direction < -1):
            direction = -1
    return direction, 1

def drawContoursEtInfos(vueDessus, rect, direction, vitesse):
    if rect is not None:
        box = cv2.boxPoints(rect)
        box = np.int0(box)
        cv2.drawContours(vueDessus,[box], 0,(0,0,255),2)
    cv2.putText(vueDessus, 'd='+str(direction)+',v='+str(vitesse),(0, vueDessus.shape[0] - 20), font, 1,(0,255,0),2,cv2.LINE_AA)


# grab the current frame
def readImageFromBlender():
    #Test if file exist
    image = Path(renderingImageFile)
    if image.exists():      
        frame = cv2.imread(renderingImageFile)
        #suppression du fichier d'entree
        try:
            os.remove(renderingImageFile)
        except:
            return None
        return frame
    else:
        return None  



numImg = 0
while True:
    if (numImg == 0):
        with open(imageAnalyserJsonFile, 'w') as outfile:
            outfile.write('{\"direction\":0, \"vitesse\":1}')
            outfile.close
        
    frame = readImageFromBlender()
    if frame is None:
        print('Nothing to read...')
        #On attend un peu
        time.sleep(0.1)
    else:     
        # Pour l instant on limite le traitement a 300 frames
        if numImg > NB_ITERATIONS:
            #write empty file to stop blender
            with open(imageAnalyserJsonFile, 'w') as outfile:
                outfile.write('{\"stop\":true}')
                outfile.close
            break
    
        # get angle from image
        vueDessus, lignesBlanches, direction, vitesse = detectAngleAndDistance(frame)
        
        # from angle, perform move and render new view into png
        numImg = numImg+1
        #write json file with angle value. It s the new blender input...
        with open(imageAnalyserJsonFile, 'w') as outfile:
            outfile.write('{\"direction\":'+str(direction)+', \"vitesse\":'+str(vitesse)+'}') 
            outfile.close
        
        # For debug, save inputImage with detection and angle
        frame = commonVideo.concat_images(lignesBlanches, vueDessus)
        pngOutputFile = renderingDebugImagesFolder+"\\debugOutput"+str(numImg).zfill(5)+'.png'
        cv2.imwrite(pngOutputFile, frame)
        
        k = cv2.waitKey(5) & 0xFF
        if k == 27:
            break
        
        #On attend un peu que blender nous fasse un rendu...
        print("new image done : "+str(numImg))
        time.sleep(0.1)
    
cv2.destroyAllWindows()


#make a video from images
print('Starting video packaging')
firstNumImg=1
lastNumImg=NB_ITERATIONS
imagePrefix='debugOutput'
imagesSuffix=''
imagesExtension='png'
listImages = [renderingDebugImagesFolder+'/'+imagePrefix+str(numImg).zfill(5)+imagesSuffix+'.'+imagesExtension for numImg in list(range(firstNumImg, lastNumImg+1))]
print('video module')
commonVideo.video_from_images(listImages, renderingVideoFile, 24)


