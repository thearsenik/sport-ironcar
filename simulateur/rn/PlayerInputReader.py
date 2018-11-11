from PIL import Image
from pathlib import Path
import os
import json
import sys
sys.path.insert(0, '../')
import pathConfig



# grab the current frame
def readImageFromBlender():
    
    #Test if file exist
    image = Path(imageInputFile)
    if image.exists():     
        try:    
            frame = cv2.imread(imageInputFile)
            #suppression du fichier d'entree
            os.remove(imageInputFile)
        except:
            return None
        return frame
    else:
        return None  




def readInputFile():
    
    #Test if file exist
    jsonFile = Path(pathConfig.gameOutputFile)
    if jsonFile.exists(): 
        data = None     
        try:
            with open(pathConfig.detectionFile) as data_file: 
                data = json.load(data_file)
                #suppression du fichier d'entree
                os.remove(pathConfig.detectionFile)
        except:
            return None
        return data
    else:
        return None
    


