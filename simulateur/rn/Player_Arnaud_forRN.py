import logging
import RnController
# Set your detector according to your player
import sys
sys.path.insert(0, '../')
import ImageAnalyzer_DottedLine as imageAnalyzer
import config


logging.basicConfig(filename=config.logFile,level=logging.DEBUG, format='%(asctime)s %(message)s')

class Player:

    rotAnglesDegree = (-3, -2.5, -2, -1.5, -1, -0.5, 0, 0.5, 1, 1.5, 2, 2.5, 3)
    
    def __init__(self):
        self.previousDirection = None
        self.previousRotZIndex = round((len(self.rotAnglesDegree)-1)/2)
        self.previousRotAngle = 90
        self.rnController = RnController.RnController()

        
    def startNewGame(self):
        self.rnController.startNewGame()
        
    def save(self):
        self.rnController.saveRN()
        
    # normalize angle from -1 (0°) to +1 (180°)
    def _normalizeAngle(self, angleInDegrees):
        return (angleInDegrees-90)/90
                
    # retourne l'index de rotAnglesDegree pour lequel la valeur est la plus proche de la valeur specifiee
    def _getIndexFromValue(self, value):
        index = 0
        for i, valeur in enumerate(self.rotAnglesDegree):
            index = i
            if value <= valeur:
                if (i != 0):
                    if (valeur-value) > (value - self.rotAnglesDegree[i-1]):
                        index = index-1
                break
        return index
        
        
        
    def compute(self, reward, frame, numGame, numStep):
        logging.debug("compute reward"+str(reward))
        logging.debug("player_Arnaud_forRN : compute start. ")
        pointilles = imageAnalyzer.getDetection(frame, numGame, numStep)

        # angle, distance du centre, hauteur sur l'image birdeye
        vitesse, direction = self._getMove(reward, pointilles)
            
        self.previousDirection = direction

        logging.debug("player_Arnaud_forRN : compute end. ")
        return vitesse, direction

    def _sign(self, number):
        if number < 0:
            return -1
        return 1


    def _getMove(self, reward, pointilles):
        
        logging.debug("_getMove reward"+str(reward))
        indexVoulu = self.rnController.compute(reward, pointilles)
        
        print('indexVoulu '+str(indexVoulu))
        #Comme en vrai la variation ne peut pas etre instantannee on bouge d'un cran vers l'index suivant
        rotZIndex = self._getRotationAvecInertie(indexVoulu)
        print('index '+str(rotZIndex))
        #The rotZIndex is converted to direction by centering 0 value as 0
        direction = rotZIndex - round((len(self.rotAnglesDegree)-1)/2)
        #direction = rotZIndex
        
        #### Vitesse de deplacement
        vitesse = 2
        
        return vitesse, direction

    #Comme en vrai la variation ne peut pas etre instantannee on simule l'inertie de la voiture en
    #bougeant seulement d'un cran vers l'index suivant en direction de l'indexVoulu.
    def _getRotationAvecInertie(self, indexVoulu):
        index = self.previousRotZIndex
        if indexVoulu-index > 0:
            index +=1
            if index == len(self.rotAnglesDegree):
                index = len(self.rotAnglesDegree)-1
        elif indexVoulu-index < 0:
            index -=1
            if index == -1:
                index = 0
        #else (indexVoulu=previousIndex) on ne change rien
        
        self.previousRotZIndex = index
        return index 