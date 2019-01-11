import time
import commonSocket as sock
import socket
from multiprocessing.connection import Listener
import logging
import playerInputReader as input
# change your player
import Player_Arnaud as Player
import sys
from multiprocessing.connection import Client
sys.path.insert(0, '../')
import config


logging.basicConfig(filename=config.logFile,level=logging.DEBUG, format='%(asctime)s %(message)s')

addressRender = (config.RENDER_SERVER, config.RENDER_PORT)

def writeCommandFile(vitesse, direction, stop=False):
    message = None
    if (stop):
        message = '{\"stop\":\"true\"}'
    else:
        message = '{\"direction\":\"'+str(direction)+'\", \"speed\":\"'+str(vitesse)+'\"}'
    #nbTry=3
    #while (nbTry > 0):
    #    try:
    #        with open(config.commandFile, 'w') as outfile:
    #            outfile.write(message)
    #            outfile.close
    #            print('Write command done...')
    #            break
    #    except:
    #        nbTry = nbTry-1
    #        print('Write command delayed...')
    #        time.sleep(0.001)
    clientSocket = Client((config.COMMAND_SERVER, config.COMMAND_PORT), 'AF_INET')
    #clientSocket.send(struct.pack("L", len(message)))
    clientSocket.send(message)
    clientSocket.close()
    logging.debug("write command done... ")
            
    
def readGameResultFile():
    global gameResultListener
    logging.debug("listening for game result... ")
    gameResultSocket = gameResultListener.accept()
    data = sock.read_json(gameResultSocket)
    logging.debug("Json game result read: "+str(data))
    
    return data        

player = Player.Player()

waitStateChanged = False
time1 = 0
time2 = 0
cpt = 0


gameResultListener = None
try:
    gameResultListener = Listener(addressRender, 'AF_INET')   
except OSError:  
    #socket is already in use... reuse it
    gameResultListener = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    gameResultListener.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    gameResultListener.bind((addressRender[0], addressRender[1]))    

 
# Nouvelle partie
writeCommandFile(2, 0)
data = readGameResultFile()
# Launch exe
#subprocess.Popen(['d:/dev/ironcar/ironcarAgfa/sport-ironcar/blender/roadGameEngineWithSocket.exe'])
# on boucle sur les steps...
while True:
    if data['done']:
        player = Player.Player()    
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
        vitesse, direction = player.compute(frame) 
        time2 = time.time() * 1000
        print('direction taken : '+str(direction))
        print('analyse en '+str(time2-time1)+'ms')
        #On ecrit l'action
        writeCommandFile(vitesse, direction)
        data = readGameResultFile()