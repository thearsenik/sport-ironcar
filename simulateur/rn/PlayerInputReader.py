from PIL import Image
from pathlib import Path
import os
import json
import sys
sys.path.insert(0, '../')
import config
import cv2



# grab the current frame
def readImageFromBlender():
    
    #Test if file exist
    image = Path(config.renderedImageFile)
    if image.exists():     
        try:    
            frame = cv2.imread(config.renderedImageFile)
            #suppression du fichier d'entree
            os.remove(config.renderedImageFile)
        except:
            return None
        return frame
    else:
        return None  




def readInputFile():
    
    #Test if file exist
    jsonFile = Path(config.gameOutputFile)
    if jsonFile.exists(): 
        data = None     
        try:
            with open(config.gameOutputFile) as data_file: 
                data = json.load(data_file)
                #suppression du fichier d'entree
                os.remove(config.gameOutputFile)
        except:
            return None
        return data
    else:
        return None
    


