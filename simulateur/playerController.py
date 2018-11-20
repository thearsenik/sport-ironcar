import time
import subprocess
import logging
import playerInputReader as input
# change your player
import Player_Arnaud as Player
import sys
from multiprocessing.connection import Client
import struct
sys.path.insert(0, '../')
import pathConfig


logging.basicConfig(filename=pathConfig.logFile,level=logging.DEBUG)


def writeCommandFile(action, stop=False):
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
            
            

player = Player.Player()

waitStateChanged = False
time1 = 0
time2 = 0
cpt = 0


# Nouvelle partie
writeCommandFile(0)
# Launch exe
#subprocess.Popen(['d:/dev/ironcar/ironcarAgfa/sport-ironcar/blender/roadGameEngineWithSocket.exe'])
# on boucle sur les steps...
while True:
    frame = input.readImageFromBlender()
    if frame is None:
        if waitStateChanged == False:
            waitStateChanged = True
            time1 = time.time() * 1000
            print('No image from game... wait...')
        cpt = cpt+1
        time.sleep(0.002)
    else:
        if waitStateChanged == True:
            time2 = time.time() * 1000
            print('On a attendu pendant '+str(time2-time1)+'ms en '+str(cpt)+' cycles')
            waitStateChanged = False
        cpt = 0
        # get result
        #print('New step...')
        time1 = time.time() * 1000
        action = player.compute(frame) 
        time2 = time.time() * 1000
        print('direction taken : '+str(action))
        print('analyse en '+str(time2-time1)+'ms')
        #On ecrit l'action
        writeCommandFile(action)
     
