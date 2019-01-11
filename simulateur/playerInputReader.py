from PIL import Image
from pathlib import Path
import os
import json
import logging
import config
import cv2
import time


logging.basicConfig(filename=config.logFile,level=logging.DEBUG, format='%(asctime)s %(message)s')

# grab the current frame
def readImageFromBlender():
    logging.debug("Player reader : readImageFromBlender start. ")
    #Test if file exist
    #time1 = time.time() * 1000
    image = Path(config.renderedImageFile)
    if image.exists():     
        try:    
            frame = cv2.imread(config.renderedImageFile)
            #suppression du fichier d'entree
            #os.remove(config.renderedImageFile)
        except:
            #print('trt Exception '+str(time.time() * 1000-time1)+'ms')
            logging.debug("Player reader : readImageFromBlender stop. (exception)")
            return None
        logging.debug("Player reader : readImageFromBlender stop. (image lue)")
        return frame
    else:
        #print('trt '+str(time.time() * 1000-time1)+'ms')
        logging.debug("Player reader : readImageFromBlender stop. (pas d'image)")
        return None  




def readInputFile():
    
    #Test if file exist
    jsonFile = Path(config.gameOutputFile)
    if jsonFile.exists(): 
        data = None     
        try:
            with open(config.detectionFile) as data_file: 
                data = json.load(data_file)
                #suppression du fichier d'entree
                os.remove(config.detectionFile)
        except:
            return None
        return data
    else:
        return None
    


