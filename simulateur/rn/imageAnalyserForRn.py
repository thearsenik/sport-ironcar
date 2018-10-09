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

font = cv2.FONT_HERSHEY_SIMPLEX

imageInputFile = "D:/dev/ironcar/ironcarAgfa/sport-ironcar/output/outputRenderer/road.jpg"
jsonOutputFile = "D:/dev/ironcar/ironcarAgfa/sport-ironcar/output/outputAnalyser/detection.json"
imageDebugDir = "D:/dev/ironcar/output/debug"
videoOuputFile = "D:/dev/ironcar/output/blenderOutput.mp4"
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


# grab the current frame
def readImageFromBlender():
    
    #Test if file exist
    image = Path(imageInputFile)
    if image.exists():      
        frame = cv2.imread(imageInputFile)
        #suppression du fichier d'entree
        try:
            os.remove(imageInputFile)
        except:
            return None
        return frame
    else:
        return None  



numImg = 0
while True:
    if (numImg == 0):
        with open(jsonOutputFile, 'w') as outfile:
            outfile.write('{\"pointilles\":[{\"angle\":90, \"distance\":0, \"hauteur\":1}]}')
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
            with open(jsonOutputFile, 'w') as outfile:
                outfile.write('{\"stop\":true}')
                outfile.close
            break
    
        # get angle from image
        frame2, pointilles = detectAngleAndDistance(frame)
        
        # from angle, perform move and render new view into png
        numImg = numImg+1
        #write json file with angle value. It s the new blender input...
        with open(jsonOutputFile, 'w') as outfile:
            outfile.write('{\"pointilles\":[')
            for i, point in enumerate(pointilles):
                fin=''
                if i < len(pointilles)-1:
                   fin=','
                outfile.write('{\"angle\":'+str(point[0])+', \"distance\":'+str(point[1])+', \"hauteur\":'+str(point[2])+'}'+fin) 
            outfile.write(']}')
            outfile.close
        
        # For debug, save inputImage with detection and angle
        frame = commonVideo.concat_images(frame, frame2)
        output = Image.fromarray(frame)
        pngOutputFile = imageDebugDir+"\\debugOutput"+str(numImg).zfill(5)+'.png'
        output.save(pngOutputFile)
        
        k = cv2.waitKey(5) & 0xFF
        if k == 27:
            break
        
        #On attend un peu que blender nous fasse un rendu...
        print("new image done : "+str(numImg))
        time.sleep(0.1)
    
cv2.destroyAllWindows()


#make a video from images
firstNumImg=1
lastNumImg=NB_ITERATIONS
imagePrefix='debugOutput'
imagesSuffix=''
imagesExtension='png'
listImages = [imageDebugDir+'/'+imagePrefix+str(numImg).zfill(5)+imagesSuffix+'.'+imagesExtension for numImg in list(range(firstNumImg, lastNumImg+1))]
commonVideo.video_from_images(listImages, videoOuputFile, 24)


