import logging
import sys
sys.path.insert(0, '../simulateur')
import pathConfig
import commonSocket as sock
import time
import queue
import threading
from multiprocessing.connection import Listener
from multiprocessing.connection import Client


addressCommands = ('127.0.0.1', 6549)
addressRender = ('127.0.0.1', 6559)

logging.basicConfig(filename=pathConfig.logFile,level=logging.DEBUG)


def readCommandFile():
    global commandsListener
    global commandQueue
    while True: 
        time1 = time.time() * 1000
        commandSocket = commandsListener.accept()
        commandData = sock.read_json(commandSocket)
        logging.debug("Json commands read: "+str(commandData))
        commandQueue.put(commandData)
        time2 = time.time() * 1000
        logging.debug("we wait for commands for "+str(time2-time1)+" ms")
    #return commandData

def readCommandQueue():
    global commandQueue
    if commandQueue.empty():
        return None
    else:
        data = commandQueue.get_nowait()
        if (data != None):
            logging.debug("Command received from queue ")
        return data
 
def writeCarLocationFile(car, stop=False):
    global addressRender
    message = None
    if (stop):
        message = '{\"stop\":true}'
    else:
        position = car.worldPosition
        rotationZ = car.worldOrientation.to_euler().z
        message = '{\"x\":\"'+str(position.x)+'\", \"y\":\"'+str(position.y)+'\", \"z\":\"'+str(position.z)+'\", \"rotZ\":\"'+str(rotationZ)+'\"}'
        
    clientSocket = Client(addressRender, 'AF_INET')
    clientSocket.send(message)
    clientSocket.close() 


logging.debug("Creating socket on : "+str(addressCommands[0])+" "+str(addressCommands[1]))
commandsListener = Listener(addressCommands, 'AF_INET') 
#create a queue to get commands
commandQueue = queue.Queue()  
# create a thread to listen to the commands
commandThread = threading.Thread(target=readCommandFile)
commandThread.start()
