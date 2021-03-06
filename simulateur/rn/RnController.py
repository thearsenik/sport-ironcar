import numpy as np
import logging
import RnMemory
import Rn
import sys
sys.path.insert(0, '../')
import config


logging.basicConfig(filename=config.logFile,level=config.logLevelPlayer, format='%(asctime)s %(message)s')

class RnController:

    NB_ITEM_IN_TRAINING_BATCH = 50


    def __init__(self, playInTrainingMode):
        self.isTrainingOn = playInTrainingMode
        if self.isTrainingOn:
            self.memory = RnMemory.RnMemory(50000)
        else:
            self.memory = None
        self.RN = Rn.Rn(self.isTrainingOn)
        self.previousAction = None
        self.previous_inputs = None
        self.previousInversed = False

    def startNewGame(self, startIndex):
        # Store result as previous action choice
        self.previousAction = None
        self.previous_inputs = None
        self.RN.startNewGame(startIndex)

    def saveRN(self):
        self.RN.save()
        
    # normalize angle from -1 (0°) to +1 (180°)
    # et on retourne 0 (90°) si 180 ou 0
    def _normalizeAngle(self, angleInDegrees):
        if angleInDegrees == 0 or angleInDegrees == 180:
            return 0
        return (angleInDegrees-90)/90
    
    # normalize previous action to be one 1 for the choosen action and 0 for others
    def _normalizePreviousAction(self):
        if self.previousAction is None:
            return self.RN.DEFAULT_PREVIOUS_ACTION
        
        elif len(self.previousAction) != self.RN.NB_ACTIONS:
            return self.RN.DEFAULT_PREVIOUS_ACTION

        else:
            normalized = np.zeros(self.RN.NB_ACTIONS)
            normalized[np.argmax(self.previousAction)] = 1
            return normalized
                
    # comme on veut un rn symetrique, on symetrise tout de façon a ce que la
    # distance soit toujours positive 
    def _symetrizeInput(self, inputs):
        if inputs[1] < 0:
            inputs[0] = -inputs[0]
            inputs[1] = -inputs[1]     
            return True
        return False

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
            
            outOfRoad = False
            
            if pointilles is None:
                # On a perdu...
                if self.isTrainingOn:
                    # On stocke juste la reward
                    # Add to memory: take the new input as the new state (next_state)
                    self.memory.add_sample((self.previous_inputs, self.previousAction, reward, None))
                    #logging.debug("RnController : addsample "+str((self.previous_inputs, self.previousAction, reward, inputs)))
                    
                    # Modify RN with gradient according to reward
                    self.RN.replay(self.memory.sample(self.NB_ITEM_IN_TRAINING_BATCH))
                
                # On renvoit n'importe quoi car de toutes facons on a perdu et
                # on ne fera rien de la reponse...
                print('perdu...')
                return 0, False
                    
                
            elif len(pointilles) > 0:
                print('on a au moins un pointille')
                # On ne prend que le dernier pointille de la liste (le plus haut sur l'image)
                last = len(pointilles)-1
                # pointille[0] = angle, pointille[1]=distance, pointille[2]=hauteur
                angle = self._normalizeAngle(pointilles[last][0])
                distance = pointilles[last][1]
                hauteur = pointilles[last][2]
                inputs =  np.array([angle, distance, hauteur]); 
                logging.debug('pointille angle='+str(angle)+' distance='+str(distance)+' hauteur='+str(hauteur))
            else:
                # Pas de pointilles !!!
                if self.previous_inputs is None:
                    # Premier step... c'est normal...
                    inputs =  np.array([0, 0, 1])
                    print('No dot, first step')
                else:
                    # Gloups ! Sortie de route !
                    # On ne devrait jamais arrive la...
                    print('out of road !!!')
                    logging.info('out of road !!!')
                
            # we normalize previous action
            normalizedAction = self._normalizePreviousAction()
                
            # keep distance positive to get rn symetry insensive
            inversed = self._symetrizeInput(inputs)
            # when inversion changed we inverse previous action
            if inversed != self.previousInversed:
                normalizedAction = np.flip(normalizedAction)
            
            # we add normalized previous action to input
            for action in normalizedAction:
                inputs = np.append(inputs, action)
                    
            # store result in memory for batch replay and retrain RN
            if self.isTrainingOn:
                if self.previous_inputs is None:
                    print("previous_inputs is null...")
                else:
                    # Add to memory: take the new input as the new state (next_state)
                    self.memory.add_sample((self.previous_inputs, self.previousAction, reward, inputs))
                    #logging.debug("RnController : addsample "+str((self.previous_inputs, self.previousAction, reward, inputs)))
                    
                    # Modify RN with gradient according to reward
                    self.RN.replay(self.memory.sample(self.NB_ITEM_IN_TRAINING_BATCH))
            
            
            # RN compute action to take according to the new input
            action, isRandomChoice = self.RN.compute(inputs)
            #logging.debug("Action = "+str(action))
            # Store result as previous action choice
            self.previousAction = action
            
            # Get reward
            # convert result to action. Simply return index of the most significant output. 
            actionId = np.argmax(action)
            # but if inputs was inverted we also invert the output
            if inversed:
                if outOfRoad:
                    print('inversion de l action...')
                    logging.info('inversion de l action...')
                if actionId == 0:
                    actionId = 2
                elif actionId == 2:
                    actionId = 0
                    
            if outOfRoad:
                print('inputs = ')
                print(inputs)
                print('action = ')
                print(action)
                logging.info('inputPrecedent = ')
                logging.info(self.previous_inputs)
                logging.info('inversed='+str(inversed))
                logging.info('previousInversed='+str(self.previousInversed))
                logging.info('inputs = ')
                logging.info(inputs)
                logging.info('action = ')
                logging.info(action)
                randomChoiceStr = ''
                if isRandomChoice:
                    randomChoiceStr = '*'
                logging.info('action choisie (-1,0,1) = '+str(actionId-1)+randomChoiceStr)
                logging.info('------------------------------------------')
                print ('action choisie (-1,0,1) = '+str(actionId-1))
                print ('------------------------------------------')
            logging.debug('choosen action id='+str(actionId))
            
            # Store input as previous input for next iteration
            self.previous_inputs = inputs
            self.previousInversed = inversed

            return actionId, isRandomChoice

    

