import numpy as np
import bpy
from mathutils import Vector, Matrix
from pathlib import Path
import matplotlib.pylab as plt
import os
import json
import time
import logging
import Environnement
import RnMemory
import Rn
import itertools
import sys
sys.path.insert(0, '../')
import pathConfig


# reload files in blender if they changed
import importlib
importlib.reload(pathConfig)
importlib.reload(Environnement)


logging.basicConfig(filename=pathConfig.logFile,level=logging.DEBUG)

NB_ITEM_IN_TRAINING_BATCH = 50


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

    
# normalize angle from -1 (0°) to +1 (180°)
def _normalizeAngle(self, angleInDegrees):
	return (angleInDegrees-90)/90
				


def playGame():
    global env
    global logging
	global RN
	global memory
	global NB_ITEM_IN_TRAINING_BATCH
	global reward_store
	global nb_step_store
    numImg = 0
    
    env.reset()
     
	# Store result as previous action choice
    previousAction = None
	reward = 0
	previous_inputs = None
     
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
			
			##### Formatage des inputs #####
			# chaque entree va etre de la forme : angle/180, distance au centre, hauteur, wasPreviousActionAction1, wasPreviousActionAction2, ... , wasPreviousActionActionN
			# par defaut angle=90, distance=0, hauteur=1, action precedente = index nbAction/2
			#Input :
			# angle in degrees-90/90,
			# centered and normalized x (0 when at the center of screen, -1 left, +1 right),
			# normalized y from the bottom of the screen (from 1 at the top to 0 at the bottom of the screen),
			# was action 0 previously selected,
			# was action 1 previously selected,
			# ...
			# was action n previously selected
			inputs =DEFAULT_INPUT = [(0, 0, 1, (0, 0, 1, 0, 0))]
			
			# On ne prend qu'un des pointilles
			last = len(pointilles)-1
			if len(pointilles) > 0:
				# On ne prend que le dernier pointille de la liste (le plus haut sur l'image)
				inputs = [(_normalizeAngle([pointilles[last]["angle"]), pointilles[last]["distance"], pointilles[last]["hauteur"]), previousAction];  
			elif previousAction != None:
				inputs = [(0, 0, 1, previousAction)]	
			# flatten the inputs into a one dimension array
			flatInputs = list(itertools.chain.from_iterable(inputs))
			#inputs = inputs.reshape((-1,inputs.size))
			
			# store result in memory for batch replay and retrain RN
			if previousAction != None:
				# Add to memory: take the new input as the new state (next_state)
				memory.add_sample((previous_inputs, previousAction, reward, flatInputs))
				
				# Modify RN with gradient according to reward
				RN.replay(memory.sample(NB_ITEM_IN_TRAINING_BATCH))
			
			# RN compute action to take according to the new input
            action = RN.compute(flatInputs)
			# Store result as previous action choice
			previousAction = action
			# Store input as previous input for next iteration
			previous_inputs = flatInputs;
			
			# Get reward
			# convert result to action. Simply return index of the most significant output.
			actionId = action.index(max(action)) # ou sinon np.argmax
            reward, done = env.calculateRewardForAction(actionId)
            
            if done:
                print ('GAME OVER...')
                logging.debug('GAME OVER...')
				# store results
				reward_store.append(env.totalScore)
                nb_step_store.append(numImg)
				# Exit game...
				break

			
            # Render  
            print('render img '+str(numImg))
            logging.debug('render img '+str(numImg))
            env.getNewState(pathConfig.renderedImageFile)
			
			# Copy rendered view to party folder...
			
			
            #On attend un peu
            time.sleep(0.1)

    return env.totalScore
    



env = Environnement()
env.start()
memory = RnMemory(50000)
RN = Rn()
numGame = 0
reward_store = []
nb_step_store = []

# On boucle sur les parties
num_episodes = 300
while numGame < num_episodes:

	numGame += 1
	print('New game: '+str(numGame))
    logging.debug('Start a new game: '+str(numGame))
	
			
    result = playGame()
	
    logging.debug('end game: '+str(result))

	
# draw results
plt.plot(reward_store)
plt.show()
plt.close("all")
plt.plot(nb_step_store)
plt.show()
    

