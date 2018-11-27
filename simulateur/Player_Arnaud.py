import logging
import pathConfig
# Set your detector according to your player
import ImageAnalyzer_DottedLine as imageAnalyzer


logging.basicConfig(filename=pathConfig.logFile,level=logging.DEBUG)

class Player:

    rotAnglesDegree = (-3, -2.5, -2, -1.5, -1, -0.5, 0, 0.5, 1, 1.5, 2, 2.5, 3)
    
    def __init__(self):
        self.previousDirection = None
        self.numStep = 0
        self.previousRotZIndex = round((len(self.rotAnglesDegree)-1)/2)
        self.previousRotAngle = 90
        
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
        
        
        
        
    def compute(self, frame):
        self.numStep = self.numStep+1
        pointilles = imageAnalyzer.getDetection(frame, 1, self.numStep)
                          
        # On ne prend qu'un des pointilles (celui le plus haut)
        last = len(pointilles)-1
        pointille = None
        if len(pointilles) > 0:
            # On ne prend que le dernier pointille de la liste (le plus haut sur l'image)
            pointille = pointilles[last]

            vitesse, direction = self._getMove(pointille[0], pointille[1], pointille[2])
            
            self.previousDirection = direction
            
        elif self.previousDirection != None:
            direction = self.previousDirection           
        else:
            direction = 0

        
        return direction

    def _sign(self, number):
        if number < 0:
            return -1
        return 1


    def _getMove(self, angle, distance, hauteur):
        
        ### Rotation
        rotAngle = (angle-90)
        # Si la rotation passe de 90 à -90 on reste a 90...
        if abs(rotAngle-self.previousRotAngle) > 90:
            rotAngle = -self._sign(rotAngle)*90
        self.previousRotAngle = rotAngle
        
        # Rotation pour recentrer la ligne, plus c'est loin, plus on tourne
        rotDistance = -90*distance
        
        #On ajoute les deux en rajoutant un biais pour augmenter le pouvoir de la distance
        rotCorrigee = (rotAngle + rotDistance)*distance*distance+rotAngle*(1-hauteur)*(1-hauteur)*(1-hauteur)*(1-hauteur)
        print('rotCorrigee '+str(rotCorrigee))
        
        #On determine le vrai angle en le discretisant
        #On retrouve l'index correspondant dans les valeurs possibles
        indexVoulu = self._getIndexFromValue(rotCorrigee)
        print('indexVoulu '+str(indexVoulu))
        #Comme en vrai la variation ne peut pas etre instantannee on bouge d'un cran vers l'index suivant
        rotZIndex = self._getRotationAvecInertie(indexVoulu)
        print('index '+str(rotZIndex))
        #The rotZIndex is converted to direction by centering 0 value as 0
        direction = rotZIndex - round((len(self.rotAnglesDegree)-1)/2)
        #direction = rotZIndex
        
        #### Vitesse de deplacement
        vitesse = 3
        if(angle>100):
            #actionText = "turn left"
            vitesse = 2
        elif(angle<80):
            #actionText = "turn right"
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