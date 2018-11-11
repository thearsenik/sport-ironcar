import logging
import sys
import time
import os
import json
from shutil import copyfile
from pathlib import Path
sys.path.insert(0, '../simulateur/')
sys.path.insert(0, '../simulateur/rn/')
import pathConfig
import Environnement
#import bmesh 
from mathutils import Vector, Matrix

# reload files in blender if they changed
import importlib
importlib.reload(pathConfig)
importlib.reload(Environnement)


logging.basicConfig(filename=pathConfig.logFile,level=logging.DEBUG)



def readCarLocationFile():
    #Test if file exist
    jsonFile = Path(pathConfig.carLocation)
    if jsonFile.exists(): 
        data = None   
        try:        
            with open(pathConfig.carLocation) as data_file: 
                data = json.load(data_file)
            #suppression du fichier d'entree
            os.remove(pathConfig.carLocation)
        except:
            return None
        return data
    else:
        return None
    
            
            
def playNewGame(numGame):
    global env
    global logging
    numImg = 0
    
    env.reset()
    stop = False; 
    while True:
        data = readCarLocationFile()
        if (data == None):
            print('Nothing to read in game...')
            #On attend un peu
            time.sleep(0.02)
        else:
            if ('stop' in data):
                print("STOP...")
                env.stop()
                stop = True
                break
               
            # Get reward
            # calculate reward for the new position
            reward, done = env.next(data['x'], data['y'], data['z'], data['rotZ'])
                
            # To debug, copy rendered view to game output directory...
            numImg +=1
            imageFile = pathConfig.gamesDir+"\\game"+str(numGame).zfill(5)+"_"+str(numImg).zfill(5)+'.png'
            copyfile(pathConfig.renderedImageFile, imageFile)
            
            if done:
                print ('GAME OVER...')
                logging.debug('GAME OVER...')
                # Exit game...
                break
                
            #On attend un peu avant de traiter la commande suivante
            time.sleep(0.01)

    return env.totalScore, stop
    



env = Environnement.Environnement()
numGame = 0
logging.debug('################# Launching games.... ##################')
while True:

    numGame += 1
    print('New game: '+str(numGame))
    logging.debug('Start a new game: '+str(numGame))
    
          
    result, stop = playNewGame(numGame)
    
    if stop:
        logging.debug('Abort due to stop command... '+str(result))
        break
    else:
        logging.debug('score of the game: '+str(result))
    break
    
