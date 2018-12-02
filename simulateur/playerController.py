import time
import subprocess
import commonSocket as sock
from multiprocessing.connection import Listener
import logging
import playerInputReader as input
# change your player
import Player_Arnaud as Player
import sys
from multiprocessing.connection import Client
sys.path.insert(0, '../')
import pathConfig
from PIL import Image
import binascii
import io
import numpy as np

logging.basicConfig(filename=pathConfig.logFile,level=logging.DEBUG, format='%(asctime)s %(message)s')

addressRender = ('127.0.0.1', 6559)

def writeCommandFile(action, stop=False):
    logging.debug("playerController : write command start... ")
    message = None
    if (stop):
        message = '{\"stop\":\"true\"}'
    else:
        message = '{\"direction\":\"'+str(action)+'\"}'

    clientSocket = Client(('127.0.0.1', 6549), 'AF_INET')
    clientSocket.send(message)
    clientSocket.close()
    logging.debug("playerController : write command done... ")
            
    
def readRenderFile():
    global locationListener
    logging.debug("playerController : listening for render and location... ")
    locationSocket = locationListener.accept()
    data = sock.read_json(locationSocket)
    logging.debug("playerController : Json render and location read: ")
    return data  

# decode base64
def decodeFrame(frameStr):
    bytes = binascii.a2b_base64(frameStr)
    image = Image.frombytes("RGB", (200, 150), bytes)
    return np.array(image)

player = Player.Player()

waitStateChanged = False
time1 = 0
time2 = 0
cpt = 0


locationListener = Listener(addressRender, 'AF_INET')   
# Nouvelle partie
writeCommandFile(0)
# Launch exe
#subprocess.Popen(['d:/dev/ironcar/ironcarAgfa/sport-ironcar/blender/roadGameEngineWithSocket.exe'])
# on boucle sur les steps...
while True:
    data = readRenderFile()
    frame = decodeFrame(data["render"])
    if frame is None:
        logging.debug("Unexpected error : playerController : No image !!!! ")
    else:
        # get result
        #print('New step...')
        #time1 = time.time() * 1000
        action = player.compute(frame)
        #time2 = time.time() * 1000
        #print('direction taken : '+str(action))
        #print('analyse en '+str(time2-time1)+'ms')
        
        #On ecrit l'action
        writeCommandFile(action)
        
     
