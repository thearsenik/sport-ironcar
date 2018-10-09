import numpy as np
import bpy
from mathutils import Vector, Matrix
from pathlib import Path
import os
import json
import time
import logging
import Environnement
import sys
sys.path.insert(0, '../')
import pathConfig


# reload files in blender if they changed
import importlib
importlib.reload(pathConfig)
importlib.reload(Environnement)


logging.basicConfig(filename=pathConfig.logFile,level=logging.DEBUG)


def readDetectionFile():
    
    #Test if file exist
    jsonFile = Path(pathConfig.detectionFile)
    if jsonFile.exists(): 
        detectionData = None     
        with open(pathConfig.detectionFile) as data_file: 
            detectionData = json.load(data_file)
        #suppression du fichier d'entree
        try:
            os.remove(pathConfig.detectionFile)
        except:
            return None
        return detectionData
    else:
        return None
    
    
def getPointilles(data):
    pointilles = []
    pointsJson = data["pointilles"]
    for item in pointsJson:
        pointille = {"angle":item['angle'],
                     "distance":item['distance'],
                     "hauteur":item['hauteur']}
        pointilles.append(pointille)
        
    return pointilles
   
    
def render(outputFile):
    #render frame
    bpy.data.scenes["Scene"].render.filepath = outputFile
    bpy.ops.render.render( write_still=True )    




def playGame():
    global env
    global logging
    numImg = 0
    
    env.reset()
     # reset RN here ?
     
     
    while True:
        data = readDetectionFile()
        if (data == None):
            print('Nothing to read...')
            #On attend un peu
            time.sleep(0.1)
        else:
            if ('stop' in data):
                print("STOP...")
                env.stop()
                break
            
            numImg +=1
            
            pointilles = getPointilles(data);
            action = RN.compute(pointilles)
            reward = env.calculateRewardForAction(action)
            
            if reward == env.GAMEOVER:
                print ('GAME OVER...')
                logging.debug('GAME OVER...')
                
               
            print('render img '+str(numImg))
            logging.debug('render img '+str(numImg))
            # render
            env.getNewState(pathConfig.renderedImageFile)
            #On attend un peu
            time.sleep(0.1)

    return env.totalScore
    



env = Environnement()
env.start()
# On boucle sur les parties
while True:
    
    result = playGame()
    
    # compute RN here ??? 
    
    

