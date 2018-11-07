from PIL import Image
from pathlib import Path
import os
import json
import sys
sys.path.insert(0, '../')

font = cv2.FONT_HERSHEY_SIMPLEX


# grab the current frame
def readImageFromBlender():
    
    #Test if file exist
    image = Path(imageInputFile)
    if image.exists():      
        frame = cv2.imread(imageInputFile)
        #suppression du fichier d'entree
        try:
            os.remove(imageInputFile)
        except:
            return None
        return frame
    else:
        return None  




def readInputFile():
    
    #Test if file exist
    jsonFile = Path(pathConfig.detectionFile)
    if jsonFile.exists(): 
        detectionData = None     
        with open(pathConfig.detectionFile) as data_file: 
            detectionData = json.load(data_file)
        #suppression du fichier d'entree
        try:
            os.remove(pathConfig.detectionFile)
        except:
            return None
        return detectionData
    else:
        return None
    


