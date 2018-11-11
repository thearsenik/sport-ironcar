import bge
import os
import json
from pathlib import Path
import sys
sys.path.insert(0, '../simulateur')
import pathConfig


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
        except:
            return None
        return commandData
    else:
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
        
        

data = readAndRemoveCommandFile()
cont = bge.logic.getCurrentController()
obj = cont.owner

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

    #dict/map of the possible directions values
    directionValues = {"-3":0.05, "-2": 0.03, "-1": 0.01, "0": 0.0, "1": -0.01, "2": -0.03, "3": -0.05}
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
    
else:
    #Si rien a faire... on desactive tout...
    for actuator in cont.actuators:
        cont.deactivate(actuator)
    
    