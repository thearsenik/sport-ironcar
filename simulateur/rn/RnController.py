import numpy as np
import logging
import RnMemory
import Rn
import itertools
import sys
sys.path.insert(0, '../')
import pathConfig


logging.basicConfig(filename=pathConfig.logFile,level=logging.DEBUG)

class RnController:

    NB_ITEM_IN_TRAINING_BATCH = 50


    def __init__(self):
        self.memory = RnMemory.RnMemory(50000)
        self.RN = Rn.Rn()
        self.previousAction = None
        self.previous_inputs = None

    def startNewGame(self):
        # Store result as previous action choice
        self.previousAction = None
        self.previous_inputs = None

        
    # normalize angle from -1 (0°) to +1 (180°)
    def _normalizeAngle(self, angleInDegrees):
        return (angleInDegrees-90)/90
                


    def compute(self, reward, pointilles):
            
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
            inputs = [(0, 0, 1, (0, 0, 1, 0, 0))]
            
            # On ne prend qu'un des pointilles
            last = len(pointilles)-1
            if len(pointilles) > 0:
                # On ne prend que le dernier pointille de la liste (le plus haut sur l'image)
                inputs = [(self._normalizeAngle(pointilles[last]["angle"]), pointilles[last]["distance"], pointilles[last]["hauteur"], self.previousAction)];  
            elif self.previousAction != None:
                inputs = [(0, 0, 1, self.previousAction)]    
            # flatten the inputs into a one dimension array
            flatInputs = list(itertools.chain.from_iterable(inputs))
            #inputs = inputs.reshape((-1,inputs.size))
            
            # store result in memory for batch replay and retrain RN
            if self.previousAction != None:
                # Add to memory: take the new input as the new state (next_state)
                self.memory.add_sample((self.previous_inputs, self.previousAction, reward, flatInputs))
                
                # Modify RN with gradient according to reward
                self.RN.replay(self.memory.sample(self.NB_ITEM_IN_TRAINING_BATCH))
            
            # RN compute action to take according to the new input
            action = self.RN.compute(flatInputs)
            # Store result as previous action choice
            self.previousAction = action
            # Store input as previous input for next iteration
            self.previous_inputs = flatInputs;
            
            # Get reward
            # convert result to action. Simply return index of the most significant output.
            actionId = action.index(max(action)) # ou sinon np.argmax


            return actionId

    

