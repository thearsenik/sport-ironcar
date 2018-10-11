import numpy as np
from mathutils import Vector, Matrix
import logging
import pathConfig

logging.basicConfig(filename=pathConfig.logFile,level=logging.DEBUG)


rotAngles = (-3, -2.5, -2, -1.5, -1, -0.5, 0, 0.5, 1, 1.5, 2, 2.5, 3)
rotMax = 3
indexAngle = round((len(rotAngles)-1)/2)
piRadian = 3.1415/180

def getIndexFromValue(myArray, value):
    index = 0
    for i, valeur in enumerate(myArray):
        index = i
        if value <= valeur:
            if (i != 0):
                if (valeur-value) > (value - myArray[i-1]):
                    index = index-1
            break
    return index

def getMove(action):
    global rotAngles
    global indexAngle
    global rotMax
    

    if (len(pointilles) > 0):
        angle=pointilles[0]["angle"]
        distance=pointilles[0]["distance"]
        hauteur=pointilles[0]["hauteur"]
    
        ### Rotation
        rotAngle = (angle-90)
        
        # Rotation pour recentrer la ligne, plus c'est loin, plus on tourne
        rotDistance = -90*distance
        
        #On ajoute les deux en rajoutant un biais pour augmenter le pouvoir de la distance
        rotCorrigee = (rotAngle + rotDistance)*distance*distance+rotAngle*(1-hauteur)*(1-hauteur)*(1-hauteur)*(1-hauteur)
        
        
        #On determine le vrai angle en le discretisant
        #On retrouve l'index correspondant dans les valeurs possibles
        indexVoulu = getIndexFromValue(rotAngles, rotCorrigee)
        #Comme la variation ne peut etre instantannee on bouge d'un cran vers l'index suivant
        if indexVoulu-indexAngle > 0:
            indexAngle +=1
            if indexAngle == len(rotAngles):
                indexAngle = len(rotAngles)-1
        elif indexVoulu-indexAngle < 0:
            indexAngle -=1
            if indexAngle == -1:
                indexAngle = 0
        #else on ne change rien
    
        
        # pi radian
        message = 'd='+str(distance)+' angle='+str(angle)+' rotAngle='+str(rotAngle)+' rotDistance='+str(rotDistance)+' rotCorrigee='+str(rotCorrigee)+' indexVoulu='+str(indexVoulu) +' indexAngle='+str(indexAngle) + ' angleRot='+str(rotAngles[indexAngle])
        print(message)
        logging.debug(message)
        
    rotZ = rotAngles[indexAngle]*piRadian
    
    #### Vitesse de deplacement
    movx = -0.03
    movy = -0.03
    if(angle>100):
        #actionText = "turn left"
        movx = -0.02
        movy = -0.02
    elif(angle<80):
        #actionText = "turn right"
        movx = -0.02
        movy = -0.02
    
    return movx, movy, rotZ