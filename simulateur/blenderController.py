import numpy as np
import bpy
from mathutils import Vector, Matrix
from pathlib import Path
import os
import json
import time
import logging
from variables import *
import math

# files
logging.basicConfig(filename=renderingLogFile,level=logging.DEBUG)
renderedImageFile=renderingImageFile
detectionFile=imageAnalyserJsonFile

# global var
previousDirection=0

# constantes
ROT_MAX = 3
V_MAX = -0.03
PI_RAD = 3.1415/180
INERTIE_DIRECTION = 0.15


def getMove(direction, vitesse):
    global previousDirection
    global INERTIE_DIRECTION
    global ROT_MAX
    global V_MAX
    
    if (direction < -1):
        direction = -1
    else:
        if (direction > 1):
            direction = 1
    
    diffDirection = math.fabs(direction - previousDirection)
    if (diffDirection < INERTIE_DIRECTION):
        nextDirection = direction
    else:
        if (direction < previousDirection):
            nextDirection = previousDirection - INERTIE_DIRECTION
        else:
            nextDirection = previousDirection + INERTIE_DIRECTION
        
    previousDirection = nextDirection
    
    # pi radian
    rotZ = nextDirection * ROT_MAX *PI_RAD
    
    #### Vitesse de deplacement
    movx = V_MAX * vitesse 
    movy = V_MAX * vitesse
    
    return movx, movy, rotZ

def readDetectionFile():
    
    #Test if file exist
    jsonFile = Path(detectionFile)
    if jsonFile.exists(): 
        detectionData = None     
        with open(detectionFile) as data_file: 
            detectionData = json.load(data_file)
        #suppression du fichier d'entree
        try:
            os.remove(detectionFile)
        except:
            return None
        return detectionData
    else:
        return None  
   
def initializeVoiturePosition(location = (-11.45727,12.74757,0.348387), rotation = (0,0,300*3.1415/180)):
    voiture = bpy.data.objects['Voiture']
    voiture.location = location
    voiture.rotation_euler = rotation

def moveAndRender(movx, movy, rotZ, outputFile):
    
    #get object
    voiture = bpy.data.objects['Voiture']
    #move object
    loc = Matrix.Translation((movx, movy, 0))
    voiture.matrix_basis *= loc
    voiture.rotation_euler[2] = voiture.rotation_euler[2] + rotZ
#    trans_local = Vector((movx, movy, 0.0))
#    trans_world = voiture.matrix_world.to_3x3() * trans_local
#    voiture.matrix_world.translation += trans_world
  
    #render frame
    bpy.data.scenes["Scene"].render.filepath = outputFile
    bpy.ops.render.render( write_still=True )
    
    logging.debug('new position = ('+str(voiture.location[0])+','+str(voiture.location[1])+','+str(voiture.location[2])+')')
    logging.debug('new angle = '+str(voiture.rotation_euler[2]/3.1415*180))
    

initializeVoiturePosition((-11.45727,12.74757,0.348387), (0,0,300*3.1415/180))
numImg = 0
while True:
    data = readDetectionFile()
    if (data == None):
        print('Nothing to read...')
        #On attend un peu
        time.sleep(0.1)
    else:
        if ('stop' in data):
            print("STOP...")
            break
        numImg +=1
        print('render img '+str(numImg))
        logging.debug('render img '+str(numImg))
        movX, movY, rotZ = getMove(data["direction"], data["vitesse"])
        moveAndRender(movX, movY, rotZ, renderedImageFile)
        #On attend un peu
        time.sleep(0.1)
