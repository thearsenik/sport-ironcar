import bge
import logging
import sys
sys.path.insert(0, '../simulateur')
import config
import time
import gameEngineSocket as socketUtil
import Environnement

# reload files in blender if they changed
import importlib
importlib.reload(config)


logging.basicConfig(filename=config.logFile,level=config.logLevelGameEngine, format='%(asctime)s %(message)s')


logging.debug("GE : cycle start.")
# wait for the socket to receive command file before checking the queue
time.sleep(0.003)
data = socketUtil.readCommandQueue()
logging.debug("data received: "+str(data))
    
cont = bge.logic.getCurrentController()

if data != None:
     
    if ('stop' in data):
        #Inform that we stopped
        socketUtil.writeStepResult(None, None, None, True)
        #Stop all ('EndGame')
        endGame = cont.actuators[2]
        cont.activate(endGame)

    
    # calculate reward for the new position and render
    reward, totalScore, done = Environnement.instance.next(data["speed"], data["direction"])  
        
    # Write result on socket
    socketUtil.writeStepResult(reward, totalScore, done)

    
    
else:
    #Si rien a faire... on desactive tout...
    for actuator in cont.actuators:
        #logging.debug("GE : actuator desactive...")
        cont.deactivate(actuator)
        
logging.debug("GE : cycle stop.")