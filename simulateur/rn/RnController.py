import numpy as np
import logging
import RnMemory
import Rn
import sys
sys.path.insert(0, '../')
import config


logging.basicConfig(filename=config.logFile,level=logging.DEBUG, format='%(asctime)s %(message)s')

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
        # init RN
        self.RN.start(False)

        
    # normalize angle from -1 (0°) to +1 (180°)
    def _normalizeAngle(self, angleInDegrees):
        return (angleInDegrees-90)/90
                


    def compute(self, reward, pointilles):
            
            ##### Formatage des inputs #####
            # chaque entree va etre de la forme : angle de -1 a +1 (angle/90), distance au centre, hauteur, wasPreviousActionAction1, wasPreviousActionAction2, ... , wasPreviousActionActionN
            # par defaut angle=90, distance=0, hauteur=1, action precedente = index nbAction/2
            #Input :
            # angle in degrees-90/90,
            # centered and normalized x (0 when at the center of screen, -1 left, +1 right),
            # normalized y from the bottom of the screen (from 1 at the top to 0 at the bottom of the screen),
            # was action 0 previously selected,
            # was action 1 previously selected,
            # ...
            # was action n previously selected
            inputs = None
            
            if len(pointilles) > 0:
                # On ne prend que le dernier pointille de la liste (le plus haut sur l'image)
                last = len(pointilles)-1
                # pointille[0] = angle, pointille[1]=distance, pointille[2]=hauteur
                inputs =  np.array([self._normalizeAngle(pointilles[last][0]), pointilles[last][1], pointilles[last][2]]); 
            else:
                inputs =  np.array([0, 0, 1])
                
            # we add previous action
            if self.previousAction is None or len(self.previousAction) != self.RN.NB_ACTIONS:
                for action in self.RN.DEFAULT_PREVIOUS_ACTION:
                    inputs = np.append(inputs, action)
            else:
                for action in self.previousAction:
                    inputs = np.append(inputs, action)
                    
            # store result in memory for batch replay and retrain RN
            if self.previous_inputs is None:
                print("previous_inputs is null...")
            else:
                print("previous_inputs length is "+str(len(self.previous_inputs)))
                # Add to memory: take the new input as the new state (next_state)
                self.memory.add_sample((self.previous_inputs, self.previousAction, reward, inputs))
                logging.debug("RnController : addsample "+str((self.previous_inputs, self.previousAction, reward, inputs)))
                
                # Modify RN with gradient according to reward
                self.RN.replay(self.memory.sample(self.NB_ITEM_IN_TRAINING_BATCH))
            
            # RN compute action to take according to the new input
            action = self.RN.compute(inputs)
            # Store result as previous action choice
            self.previousAction = action
            # Store input as previous input for next iteration
            print("Setting previous_inputs with array of length "+str(len(inputs)))
            self.previous_inputs = inputs;
            
            # Get reward
            # convert result to action. Simply return index of the most significant output.
            actionId = np.argmax(action)


            return actionId

    

