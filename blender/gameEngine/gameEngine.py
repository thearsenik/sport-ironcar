import bge
import logging
import os
import json
from pathlib import Path
import sys
sys.path.insert(0, '../simulateur')
import pathConfig
import time


logging.basicConfig(filename=pathConfig.logFile,level=logging.DEBUG)


def readAndRemoveCommandFile():
    
    #Test if file exist
    inputFile=pathConfig.commandFile
    jsonFile = Path(inputFile)
    if jsonFile.exists(): 
        commandData = None 
        try:        
            with open(inputFile, 'r') as data_file: 
                commandData = json.load(data_file)
            #suppression du fichier d'entree
            os.remove(pathConfig.commandFile)
            logging.debug("commands read and removed... ")
        except:
            logging.warning("Exception while reading/deleting file !!! ")
            return None
        return commandData
    else:
        #time.sleep(0.007)
        return None
    
def writeCarLocationFile(car, stop=False):
    message = None
    if (stop):
        message = '{\"stop\":true}'
    else:
        position = car.worldPosition
        rotationZ = obj.worldOrientation.to_euler().z
        message = '{\"x\":\"'+str(position.x)+'\", \"y\":\"'+str(position.y)+'\", \"z\":\"'+str(position.z)+'\", \"rotZ\":\"'+str(rotationZ)+'\"}'
    nbTry=3
    while (nbTry > 0):
        try:
            with open(pathConfig.carLocation, 'w') as outfile:
                outfile.write(message)
                outfile.close
                break
        except:
            nbTry = nbTry-1
            time.sleep(0.001)
        
        
time1 = time.time() * 1000
data = readAndRemoveCommandFile()

cont = bge.logic.getCurrentController()
obj = cont.owner
PI_RADIAN = 3.1415/180

if data != None:
     
    if ('stop' in data):
        #Inform that we stopped
        writeCarLocationFile(None, True)
        #Stop all ('EndGame')
        endGame = cont.actuators[2]
        cont.activate(endGame)
    
         
    #dict/map of the possible speed values: 5 level of speed including 0 (stop)
    speedValues = {"0":0.0, "1": 0.01, "2": 0.02, "3": 0.03, "4": 0.04, "5": 0.05}
    # default speed use when the car is going to constant speed
    speed = speedValues["2"]
    if ('speed' in data):
        speed = speedValues[data["speed"]]

    #dict/map of the possible directions values in Pi radians
    directionValues = {"-6":-3*PI_RADIAN, "-5": -2.5*PI_RADIAN, "-4": -2*PI_RADIAN,"-3":-1.5*PI_RADIAN, "-2": -1*PI_RADIAN, "-1": -0.5*PI_RADIAN, "0": 0.0, "1": 0.5*PI_RADIAN, "2": 1*PI_RADIAN, "3": 1.5*PI_RADIAN, "4":2*PI_RADIAN, "5":2.5*PI_RADIAN, "6":3*PI_RADIAN}
    direction = directionValues[data["direction"]]

    #here we use "minus" before speed value so that users of the simulator don't have to take
    #care of the camera's orientation in its local space
    speedAct = cont.actuators["forward"]
    speedAct.dLoc = [-speed, -speed, 0.0] 
    cont.activate(speedAct)

    directionAct = cont.actuators["direction"]
    directionAct.dRot = [0.0, 0.0, direction] 
    cont.activate(directionAct)

    #useful instruction to see properties and function accessible in any object
    #print (dir(directionAct))
    
    # render scene

    bge.render.makeScreenshot(pathConfig.renderedImageFile)
    
    
    # Export new position of the car
    # Retrieve the car:
    # On prend la premiere (et unique) scene
    my_scene = bge.logic.getSceneList()[0]
    # Trouver l'objet "voiture" de cette scene
    car = my_scene.objects['Voiture']
    # Write the file
    writeCarLocationFile(car)
    time2 = time.time() * 1000
    logging.debug("total exec "+str(time2-time1))
    
else:
    #Si rien a faire... on desactive tout...
    for actuator in cont.actuators:
        cont.deactivate(actuator)
    
    