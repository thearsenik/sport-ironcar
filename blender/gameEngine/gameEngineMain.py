import bge
import logging
import sys
sys.path.insert(0, '../simulateur')
import config
import time
import gameEngineSocket as socketUtil
import gameEngineRender as renderer


logging.basicConfig(filename=config.logFile,level=logging.DEBUG, format='%(asctime)s %(message)s')


logging.debug("GE : cycle start.")
time.sleep(0.005)
data = socketUtil.readCommandQueue()
logging.debug("data received: "+str(data))

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
    
    time1 = time.time() * 1000     
    #dict/map of the possible speed values: 5 level of speed including 0 (stop)
    speedValues = {"0":0.0, "1": 0.01, "2": 0.02, "3": 0.03, "4": 0.04, "5": 0.05}
    # default speed... used when the car is going to constant speed and is not provided in commands
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
    
    # render scene into file
    #logging.debug("GE : RENDER start.")
    bge.render.makeScreenshot(config.renderedImageFile)
    #logging.debug("GE : RENDER stop.")
    # Take a BGR picture in memory....
    #renderImg = renderer.render() 
    
    time2 = time.time() * 1000
    logging.debug("total render exec "+str(time2-time1))
    
    # Export new position of the car
    # Retrieve the car:
    # On prend la premiere (et unique) scene
    my_scene = bge.logic.getSceneList()[0]
    # Trouver l'objet "voiture" de cette scene
    car = my_scene.objects['Voiture']
    # Write the file
    socketUtil.writeCarLocationFile(car)
    #socketUtil.writeCarLocationAndRender(car, renderImg)
    
    
else:
    #Si rien a faire... on desactive tout...
    for actuator in cont.actuators:
        #logging.debug("GE : actuator desactive...")
        cont.deactivate(actuator)
        
logging.debug("GE : cycle stop.")