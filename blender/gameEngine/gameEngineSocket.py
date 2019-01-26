import logging
import sys
sys.path.insert(0, '../simulateur')
import config
import commonSocket as sock
import time
import queue
import threading
from multiprocessing.connection import Listener
from multiprocessing.connection import Client
import codecs

addressCommands = (config.COMMAND_SERVER, config.COMMAND_PORT)
addressRender = (config.RENDER_SERVER, config.RENDER_PORT)

logging.basicConfig(filename=config.logFile,level=config.logLevelGameEngine, format='%(asctime)s %(message)s')


def readCommandFile():
    global commandsListener
    global commandQueue
    while True: 
        logging.debug("GE : readCommandFile start.")
        #time1 = time.time() * 1000
        commandSocket = commandsListener.accept()
        commandData = sock.read_json(commandSocket)
        logging.debug("GE : readCommandFile : "+str(commandData))
        commandQueue.put(commandData)
        logging.debug("GE : readCommandFile end.")
        #time2 = time.time() * 1000
        #logging.debug("we wait for commands for "+str(time2-time1)+" ms")
    #return commandData

def readCommandQueue():
    global commandQueue
    if commandQueue.empty():
        return None
    else:
        data = commandQueue.get_nowait()
        if (data != None):
            logging.debug("Command received from queue ")
        else:
            logging.debug("Command received from queue is None ! ")
        return data
 
def writeCarLocationFile(car, stop=False):
    global addressRender
    logging.debug("GE : writeCarLocationFile start.")
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
    logging.debug("GE : writeCarLocationFile stop.")

def writeCarLocationAndRender(car, render, stop=False):
    global addressRender
    logging.debug("GE : writeCarLocationAndRender start.")
    message = None
    if (stop):
        message = '{\"stop\":true}'
    else:
        position = car.worldPosition
        rotationZ = car.worldOrientation.to_euler().z
        renderStr = codecs.encode(render, 'base64').decode()
        renderStr = renderStr.replace('\n', '').replace('\r', '')
        #print(renderStr)
        message = '{\"location\":{\"x\":\"'+str(position.x)+'\", \"y\":\"'+str(position.y)+'\", \"z\":\"'+str(position.z)+'\", \"rotZ\":\"'+str(rotationZ)+'\"}, \"render\":\"'+renderStr+'\"}'
        #logging.debug("message "+message)
    clientSocket = Client(addressRender, 'AF_INET')
    clientSocket.send(message)
    clientSocket.close() 
    logging.debug("GE : writeCarLocationAndRender stop.")
    
    

def writeStepResult(gain, totalScore, done, stop=False):
    global addressRender
    message = None
    if (stop):
        message = '{\"stop\":true}'
    else:
        message = '{\"reward\":'+str(gain)+', \"done\":'+_toBooleanStr(done)+', \"totalScore\":'+str(totalScore)+'}'
    logging.debug("GE output message :"+message)    
    clientSocket = Client(addressRender, 'AF_INET')
    clientSocket.send(message)
    clientSocket.close() 

def _toBooleanStr(boolValue):
    if boolValue:
        return 'true'
    return 'false'

    
logging.debug("Creating socket on : "+str(addressCommands[0])+" "+str(addressCommands[1]))
commandsListener = Listener(addressCommands, 'AF_INET') 
#create a queue to get commands
commandQueue = queue.Queue()  
# create a thread to listen to the commands
commandThread = threading.Thread(target=readCommandFile)
commandThread.start()
