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
import subprocess

font = cv2.FONT_HERSHEY_SIMPLEX

CONST_ANGLE_CAMERA = 50 # Camera's view horizontal angle is 50° (change it if we use fish eye cam)
CONST_MARGIN_X = 213
CONST_MARGIN_Y = 0

# global var
previousAngle = 90
previousHauteur = 0

def getCameraOrigin(image):
    global CONST_ANGLE_CAMERA
    imageWidth = image.shape[1]
    originY = (imageWidth / 2) / math.tan(utils.deg2rad(CONST_ANGLE_CAMERA / 2))
    return imageWidth / 2, originY

def detectAngleAndDistance(frame):
    global previousAngle
    global previousHauteur

    # Convert to birdeye
    vueDessus = utils.perspective_warp(frame)
    imgHeight = vueDessus.shape[0]
    imgWidth = vueDessus.shape[1]

    # Convert BGR to HSV
    hsv = cv2.cvtColor(vueDessus, cv2.COLOR_BGR2HSV)

    # define range of blue color in HSV
    lower_yellow = np.array([0,69,94])
    upper_yellow = np.array([255,255,255])

    lower_white = np.array([80,14,138])
    upper_white = np.array([100,44,180])


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
        rect = utils.getContoursPlusEloigne(rects, imgWidth, imgHeight)
        originX, originY = getCameraOrigin(vueDessus)
        angle = utils.getAnglePoints(rect[0], [originX, originY])
        hauteur = utils.getHauteur(rect, imgHeight) #hauteur en 0 et 1
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
    imageMiddleX = round(whiteLineImg.shape[1] / 2)
    imageHeight = whiteLineImg.shape[0]
    goalX = int(rect[0][0])
    goalY = int(rect[0][1])
    vx = goalX - imageMiddleX
    vy = goalY - imageHeight
    valMax = math.fabs(vx) + math.fabs(vy)
    ratioX = vx / valMax
    ratioY = vy / valMax
    i = 0
    while True:
        testX = imageMiddleX - 1 + int((ratioX *i) + 0.001)
        testY = imageHeight - 1 + int((ratioY *i) + 0.001)
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
        direction = ((angle - 90) / CONST_ANGLE_CAMERA) * (1 + hInverse)
    else:
        direction = 0
    if (direction > 1):
        direction = 1
    else:
        if (direction < -1):
            direction = -1
    direction = round(direction*-3)
    speed = round(5-math.fabs(direction)) - 1
    print('d='+str(direction)+',s='+str(speed))
    return direction, speed

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


# launch the game simulator
subprocess.Popen([gameSimulatorPath])

numImg = 0
while True:
    if (numImg == 0):
        with open(imageAnalyserJsonFile, 'w') as outfile:
            outfile.write('{\"direction\":"0", \"speed\":"1"}')
            outfile.close

    frame = readImageFromBlender()
    if frame is None:
        print('Nothing to read...')
        #On attend un peu
    else:
        # crop image
        frameWidth = frame.shape[1]
        frameHeight = frame.shape[0]
        startX = CONST_MARGIN_X
        endX = frameWidth - CONST_MARGIN_X
        startY = CONST_MARGIN_Y
        endY = frameHeight - CONST_MARGIN_Y
        frame = frame[startY:endY, startX:endX]
        print(frame.shape)
        
        # get angle from image
        vueDessus, lignesBlanches, direction, vitesse = detectAngleAndDistance(frame)

        # from angle, perform move and render new view into png
        numImg = numImg+1
        #write json file with angle value. It s the new blender input...
        with open(imageAnalyserJsonFile, 'w') as outfile:
            outfile.write('{\"direction\":\"'+str(direction)+'\", \"speed\":\"'+str(vitesse)+'\"}')
            outfile.close

        # For debug, save inputImage with detection and angle
        frame = commonVideo.concat_images(frame, vueDessus, 1)
        frame = commonVideo.concat_images(frame, lignesBlanches, 1)
        pngOutputFile = renderingDebugImagesFolder+"\\debugOutput"+str(numImg).zfill(5)+'.png'
        cv2.imwrite(pngOutputFile, frame)
        cv2.imshow('vueDessus',lignesBlanches)

        #On attend un peu que blender nous fasse un rendu...
        print("new image done : "+str(numImg))

    k = cv2.waitKey(5) & 0xFF
    if k == 27:
        break

cv2.destroyAllWindows()


#make a video from images
print('Starting video packaging')
firstNumImg=1
lastNumImg=numImg
imagePrefix='debugOutput'
imagesSuffix=''
imagesExtension='png'
listImages = [renderingDebugImagesFolder+'/'+imagePrefix+str(numImg).zfill(5)+imagesSuffix+'.'+imagesExtension for numImg in list(range(firstNumImg, lastNumImg+1))]
print('video module')
commonVideo.video_from_images(listImages, renderingVideoFile, 24)
