from pathlib import Path
import os
import json
import time
import logging
import playerInputReader as input
import imageAnalyzer
import RnController
import itertools
import sys
sys.path.insert(0, '../')
import pathConfig


logging.basicConfig(filename=pathConfig.logFile,level=logging.DEBUG)


def writeCommandFile(action, stop=False):
    message = None
    if (stop):
        message = '{\"stop\":\"true\"}'
    else:
        message = '{\"direction\":\"'+str(action)+'\"}'
    nbTry=3
    while (nbTry > 0):
        try:
            with open(pathConfig.commandFile, 'w') as outfile:
                outfile.write(message)
                outfile.close
                break
        except:
            nbTry = nbTry-1
            time.sleep(0.001)
            
            

gamePlayer = RnController.RnController()
numGame = 0
reward_store = []
nb_step_store = []
jsonOutputFile = pathConfig.commandFile
stop = False

# On boucle sur les parties
num_episodes = 300
while numGame < num_episodes:

    numGame += 1
    print('New game: '+str(numGame))
    logging.debug('Start a new game: '+str(numGame))
    
    # Nouvelle partie, on boucle sur les steps...
    numStep = 0
    while True:
        gamePlayer.startNewGame()
        data = input.readInputFile()
        if (data == None):
            print('Nothing to read in player...')
            #On attend un peu
            time.sleep(0.02)
        else:
            if ('stop' in data):
                print("STOP...")
                stop = True
                break
            elif ('done' in data):
                print ('GAME OVER...')
                logging.debug('GAME OVER... en '+str(numStep)+'steps score='+str(data["totalScore"]))
                # store results
                reward_store.append(data["totalScore"])
                nb_step_store.append(numStep)
                # Exit game...
                break
            
            reward = data['reward']
            frame = input.readImageFromBlender()
            if frame is None:
                print('No image from game !!!  ABORT...')
                break;
            else:
                pointilles = imageAnalyzer.getDetection(frame, numGame, numStep);
                #pointilles = detection.getPointilles();
                numStep +=1

                # get RN result and substract to get a value between -2/2
                action = gamePlayer.compute(reward, pointilles) - 2     

                #On ecrit l'action
                writeCommandFile(action)

    
    if stop:
        logging.debug('Abort due to stop command... ')
        break
        
    
#On ecrit l'action stop pour arreter blender
writeCommandFile(None, True)
    
# draw results
#import matplotlib.pylab as plt
#plt.plot(reward_store)
#plt.show()
#plt.close("all")
#plt.plot(nb_step_store)
#plt.show()
# write results

    

