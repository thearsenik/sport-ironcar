from pathlib import Path
import os
import json
import time
import logging
import ImageAnalizer
import PlayerInputReader as input
import itertools
import sys
sys.path.insert(0, '../')
import pathConfig


logging.basicConfig(filename=pathConfig.logFile,level=logging.DEBUG)


gamePlayer = RnController()
imageAnalyzer = ImageAnalyzer()
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
    
    # Nouvelle partie
    while True:
        numStep = 0
        gamePlayer.startNewGame()
        data = input.readInputFile()
        if (data == None):
            print('Nothing to read...')
            #On attend un peu
            time.sleep(0.1)
        else:
            if ('stop' in data):
                print("STOP...")
                stop = True
                break
            elif ('done' in data):
                print ('GAME OVER...')
                logging.debug('GAME OVER...')
                # store results
                reward_store.append(env.totalScore)
                nb_step_store.append(numStep)
                # Exit game...
                break
            
            reward = data['reward']
            frame = input.readImageFromBlender()
            if frame is None:
                print('No image from game !!!  ABORT...')
                break;
            else:
                detection = imageAnalyzer.getDetection(frame, numGame, numStep);
                pointilles = detection.getPointilles();
                numStep +=1
                imageFile = pathConfig.gamesDir+"\\game"+str(numGame).zfill(5)+"_"+str(numStep).zfill(5)+'.png'
                action = gamePlayer.compute(reward, pointilles)      

                #On ecrit l'action
                with open(jsonOutputFile, 'w') as outfile:
                    outfile.write('{\"rotZ\":\"'+str(action)+'\"}')
                    outfile.close
            
                #On attend un peu
                time.sleep(0.1)
    
    if stop:
        logging.debug('Abort due to stop command... '+str(result))
        break
    else:
        logging.debug('end game: '+str(result))

    
#On ecrit l'action stop pour arreter blender
with open(jsonOutputFile, 'w') as outfile:
    outfile.write('{\"stop\":true}')
    outfile.close
    
# draw results
#import matplotlib.pylab as plt
#plt.plot(reward_store)
#plt.show()
#plt.close("all")
#plt.plot(nb_step_store)
#plt.show()
# write results

    

