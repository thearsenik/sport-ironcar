import bpy
import logging
import moveController
import sys
sys.path.insert(0, '../')
import pathConfig

logging.basicConfig(filename=pathConfig.logFile,level=logging.DEBUG)

class Rn:

    NB_COUCHES = 2
    Y = 0.95
    ALPHA = 0.9 


    def __init__(self, alpha, y):
        self.alpha = alpha
        self.y = y
        self.V = 0
        
        
    def reset(self):
        self.V = 0
        
        
    def compute(pointilles):

        angle=90
        distance=0
        hauteur=1
        # 5 actions possibles:
        # ---------------------
        #   0=tourne a fond a gauche
        #   1=tourne un peu a gauche
        #   2=tout droit
        #   3=tourne a fond a droite
        #   4=tourne un peu a droite
        action=2
        
        last = len(pointilles)-1
        if (last >= 0):
            angle=pointilles[last]["angle"]
            distance=pointilles[last]["distance"]
            hauteur=pointilles[last]["hauteur"]
            
        # traitement ici !!!
        
        return action
        