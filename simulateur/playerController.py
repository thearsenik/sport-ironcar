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


logging.basicConfig(filename=pathConfig.logFile,level=logging.DEBUG, format='%(asctime)s %(message)s')

addressRender = ('127.0.0.1', 6559)

def writeCommandFile(action, stop=False):
    logging.debug("playerController : write command start... ")
    message = None
    if (stop):
        message = '{\"stop\":\"true\"}'
    else:
        message = '{\"direction\":\"'+str(action)+'\"}'
    #nbTry=3
    #while (nbTry > 0):
    #    try:
    #        with open(pathConfig.commandFile, 'w') as outfile:
    #            outfile.write(message)
    #            outfile.close
    #            print('Write command done...')
    #            break
    #    except:
    #        nbTry = nbTry-1
    #        print('Write command delayed...')
    #        time.sleep(0.001)
    clientSocket = Client(('127.0.0.1', 6549), 'AF_INET')
    #clientSocket.send(struct.pack("L", len(message)))
    clientSocket.send(message)
    clientSocket.close()
    logging.debug("playerController : write command done... ")
            
    
def readLocationFile():
    global locationListener
    logging.debug("playerController : listening for location... ")
    locationSocket = locationListener.accept()
    data = sock.read_json(locationSocket)
    logging.debug("playerController : Json location read: "+str(data))
    
    return data        

player = Player.Player()

waitStateChanged = False
time1 = 0
time2 = 0
cpt = 0


locationListener = Listener(addressRender, 'AF_INET')   
# Nouvelle partie
writeCommandFile(0)
readLocationFile()
# Launch exe
#subprocess.Popen(['d:/dev/ironcar/ironcarAgfa/sport-ironcar/blender/roadGameEngineWithSocket.exe'])
# on boucle sur les steps...
while True:
    
    frame = input.readImageFromBlender()
    if frame is None:
        logging.debug("Unexpected error : playerController : No image !!!! ")
        if waitStateChanged == False:
            waitStateChanged = True
            time1 = time.time() * 1000
            print('No image from game... wait...')
        cpt = cpt+1
        time.sleep(0.002)
    else:
        if waitStateChanged == True:
            time2 = time.time() * 1000
            #print('On a attendu pendant '+str(time2-time1)+'ms en '+str(cpt)+' cycles')
            waitStateChanged = False
        cpt = 0
        # get result
        #print('New step...')
        #time1 = time.time() * 1000
        action = player.compute(frame) 
        #time2 = time.time() * 1000
        #print('direction taken : '+str(action))
        #print('analyse en '+str(time2-time1)+'ms')
        
        #On ecrit l'action
        writeCommandFile(action)
        readLocationFile()
     
