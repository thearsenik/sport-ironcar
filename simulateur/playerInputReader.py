from PIL import Image
from pathlib import Path
import os
import json
import logging
import pathConfig
import cv2
import time


logging.basicConfig(filename=pathConfig.logFile,level=logging.DEBUG, format='%(asctime)s %(message)s')

# grab the current frame
def readImageFromBlender():
    logging.debug("Player reader : readImageFromBlender start. ")
    #Test if file exist
    #time1 = time.time() * 1000
    image = Path(pathConfig.renderedImageFile)
    if image.exists():     
        try:    
            frame = cv2.imread(pathConfig.renderedImageFile)
            #suppression du fichier d'entree
            #os.remove(pathConfig.renderedImageFile)
        except:
            #print('trt Exception '+str(time.time() * 1000-time1)+'ms')
            logging.debug("Player reader : readImageFromBlender stop.")
            return None
        logging.debug("Player reader : readImageFromBlender stop.")
        return frame
    else:
        #print('trt '+str(time.time() * 1000-time1)+'ms')
        logging.debug("Player reader : readImageFromBlender stop.")
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
    


