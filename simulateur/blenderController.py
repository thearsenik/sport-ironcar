import numpy as np
import bpy
from mathutils import Vector, Matrix
from pathlib import Path
import os
import json
import time
import logging


logging.basicConfig(filename='D:/dev/ironcar/ironcarAgfa/sport-ironcar/output/outputRenderer/render_log.txt',level=logging.DEBUG)
renderedImageFile='D:/dev/ironcar/ironcarAgfa/sport-ironcar/output/outputRenderer/road.jpg'
detectionFile='D:/dev/ironcar/ironcarAgfa/sport-ironcar/output/outputAnalyser/detection.json'
rotAngles = (-3, -2.5, -2, -1.5, -1, -0.5, 0, 0.5, 1, 1.5, 2, 2.5, 3)
rotMax = 3
indexAngle = round((len(rotAngles)-1)/2)
piRadian = 3.1415/180

def getIndexFromValue(myArray, value):
    index = 0
    for i, valeur in enumerate(myArray):
        index = i
        if value <= valeur:
            if (i != 0):
                if (valeur-value) > (value - myArray[i-1]):
                    index = index-1
            break
    return index

def getMove(angle, distance, hauteur):
    global rotAngles
    global indexAngle
    global rotMax
    
    ### Rotation
    rotAngle = (angle-90)
    
    # Rotation pour recentrer la ligne, plus c'est loin, plus on tourne
    rotDistance = -90*distance
    
    #On ajoute les deux en rajoutant un biais pour augmenter le pouvoir de la distance
    rotCorrigee = (rotAngle + rotDistance)*distance*distance+rotAngle*(1-hauteur)*(1-hauteur)*(1-hauteur)*(1-hauteur)
    
    
    #On determine le vrai angle en le discretisant
#    rotDiscret = 0
#    if rotCorrigee > 0 :
#        rotDiscret = min(rotMax, round(rotCorrigee))
#    else:
#        rotDiscret = max(-rotMax, round(rotCorrigee))
    #On retrouve l'index correspondant dans les valeurs possibles
    indexVoulu = getIndexFromValue(rotAngles, rotCorrigee)
    #Comme la variation ne peut etre instantannee on bouge d'un cran vers l'index suivant
    if indexVoulu-indexAngle > 0:
        indexAngle +=1
        if indexAngle == len(rotAngles):
            indexAngle = len(rotAngles)-1
    elif indexVoulu-indexAngle < 0:
        indexAngle -=1
        if indexAngle == -1:
            indexAngle = 0
    #else on ne change rien
    
    # pi radian
    message = 'd='+str(distance)+' angle='+str(angle)+' rotAngle='+str(rotAngle)+' rotDistance='+str(rotDistance)+' rotCorrigee='+str(rotCorrigee)+' indexVoulu='+str(indexVoulu) +' indexAngle='+str(indexAngle) + ' angleRot='+str(rotAngles[indexAngle])
    print(message)
    logging.debug(message)
    rotZ = rotAngles[indexAngle]*piRadian
    
    #### Vitesse de deplacement
    movx = -0.03
    movy = -0.03
    if(angle>100):
        #actionText = "turn left"
        movx = -0.02
        movy = -0.02
    elif(angle<80):
        #actionText = "turn right"
        movx = -0.02
        movy = -0.02
    
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
   
def initializeVoiturePosition(location = (18.3535,14.8599,0.348387), rotation = (0,0,4.3*3.1415/180)):
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
    

initializeVoiturePosition((18.3535,14.8599,0.348387), (0,0,4.3*3.1415/180))
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
        movX, movY, rotZ = getMove(data["angle"], data["distance"], data["hauteur"])
        moveAndRender(movX, movY, rotZ, renderedImageFile)
        #On attend un peu
        time.sleep(0.1)
