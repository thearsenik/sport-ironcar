import logging
import bge
import sys
sys.path.insert(0, '../simulateur')
import config
#import bmesh 
from mathutils import Vector, Matrix

# reload files in blender if they changed
import importlib
importlib.reload(config)
#importlib.reload(moveController)


logging.basicConfig(filename=config.logFile,level=logging.DEBUG, format='%(asctime)s %(message)s')


class Environnement:

    REWARD_FULL = 10
    GAMEOVER = -1
    RAYON = 1.78
    PI_RADIAN = 3.1415/180
    #dict/map of the possible speed values: 5 level of speed including 0 (stop)
    SPEED_VALUES = {"0":0.0, "1": 0.02, "2": 0.08, "3": 0.1, "4": 0.12, "5": 0.16}
    DEFAULT_SPEED = SPEED_VALUES["2"]
    #dict/map of the possible directions values in Pi radians
    DIRECTION_VALUES = {"-6":-3*PI_RADIAN, "-5": -2.5*PI_RADIAN, "-4": -2*PI_RADIAN,"-3":-1.5*PI_RADIAN, "-2": -1*PI_RADIAN, "-1": -0.5*PI_RADIAN, "0": 0.0, "1": 0.5*PI_RADIAN, "2": 1*PI_RADIAN, "3": 1.5*PI_RADIAN, "4":2*PI_RADIAN, "5":2.5*PI_RADIAN, "6":3*PI_RADIAN}
        


    def __init__(self):
        self.reward = self.REWARD_FULL
        self.target_index = 0
        self.totalScore = 0
        self.numGame = 0
        self.roadPoints = []
        self._reset()
        
        
    def _reset(self):
        self._stop()
        self._start()
        
        
    def _initializeVoiturePosition(self, location = (19.3912,23.88,0.348387), rotation = (0,0,69.2*3.1415/180)):
        my_scene = bge.logic.getCurrentScene()
        # Trouver l'objet "voiture" de cette scene
        voiture = my_scene.objects['Voiture']

        voiture.worldPosition = location
        voiture.worldOrientation = rotation
    
    
    def _start(self): 
        
        self.numGame += 1
        logging.debug('New game: '+str(self.numGame))
        
        self.reward = self.REWARD_FULL
        self.totalScore = 0
        self.target_index = 0
        
        #get road object
        my_scene = bge.logic.getCurrentScene()
        # Trouver l'objet "voiture" de cette scene
        road = my_scene.objects['roadPart']
        
        #logging.debug('ROAD: '+str(dir(road)))
        #logging.debug('meshes len: '+str(len(road.meshes)))
        logging.debug('ENV : nb tuiles sur road: meshes[0] numPolygons: '+str((road.meshes[0].numPolygons)))
        
        # apply scale and offset to polygons and calculate center of these polygons
        self.roadPoints = []
        point = None
        pointPrevious = None
        for i in range(road.meshes[0].numPolygons):
            
            polygon = road.meshes[0].getPolygon(i)
#            logging.debug('POLYGON'+str(i)+' : point1 '+str(road.meshes[0].getVertex(0, polygon.v1).x*0.324)+' '+str(road.meshes[0].getVertex(0, polygon.v1).y*0.892)+' '+str(road.meshes[0].getVertex(0, polygon.v1).z))
#            logging.debug('           : point2 '+str(road.meshes[0].getVertex(0, polygon.v2).x*0.324)+' '+str(road.meshes[0].getVertex(0, polygon.v2).y*0.892)+' '+str(road.meshes[0].getVertex(0, polygon.v2).z))
#            logging.debug('           : point3 '+str(road.meshes[0].getVertex(0, polygon.v3).x*0.324)+' '+str(road.meshes[0].getVertex(0, polygon.v3).y*0.892)+' '+str(road.meshes[0].getVertex(0, polygon.v3).z))
#            if road.meshes[0].getPolygon(i).v4 != 0:
#                logging.debug('           : point4 '+str(road.meshes[0].getVertex(0, polygon.v4).x*0.324)+' '+str(road.meshes[0].getVertex(0, polygon.v4).y*0.892)+' '+str(road.meshes[0].getVertex(0, polygon.v4).z))
#            pointPrevious = point
            point = self._calculateCenter(polygon, road.meshes[0])
            point = (point[0]*0.324+3.54, point[1]*0.892+0.778866, 0)
            self.roadPoints.append(point)
#           if (pointPrevious):
#                logging.debug('Polygon center '+str(point[0])+' '+str(point[1]))
#                logging.debug('distance2 with previous '+str(self._distance2(pointPrevious, point)))

        
        self._initializeVoiturePosition()
            
    
    def _stop(self):
        #nothing to do...
        logging.debug('Env: stop')
        
    def _distance2(self, point1, point2):
        return (point1[0]-point2[0])**2 + (point1[1]-point2[1])**2 #pas de z... + (point1[2]-point2[2])**2

    # Check if the car (point1) is close to the goal (point2)
    # check that distance^2 < R^2
    def _isCloseTo(self, point1, point2):
        logging.debug('ENV: Distance between: '+str(point1)+' and '+str(point2))
        # distance ^2
        distance2 = self._distance2(point1, point2)
        return distance2 < self.RAYON**2
    
    # Move the car
    def _move(self, speedCommand, directionCommand):
        global logging
        cont = bge.logic.getCurrentController()
        
        
        # default speed... used when the car is going to constant speed and is not provided in commands
        speed = self.DEFAULT_SPEED
        if (speedCommand):
            speed = self.SPEED_VALUES[speedCommand]
    
        direction = -self.DIRECTION_VALUES[directionCommand]
        logging.debug('ENV : rotation : '+str(direction))

    
        #here we use "minus" before speed value so that users of the simulator don't have to take
        #care of the camera's orientation in its local space
        speedAct = cont.actuators["forward"]
        speedAct.dLoc = [-speed, -speed, 0.0] 
        cont.activate(speedAct)
    
        directionAct = cont.actuators["direction"]
        directionAct.dRot = [0.0, 0.0, direction] 
        cont.activate(directionAct)
    
        my_scene = bge.logic.getSceneList()[0]
        # Trouver l'objet "voiture" de cette scene
        voiture = my_scene.objects['Voiture']
    
        return voiture.worldPosition
    
    
    def _render(self):
        #render frame
        bge.render.makeScreenshot(config.renderedImageFile)

    def _calculateCenter(self, polygon, vertexs):
        nbPoints = 3
        
        sx = vertexs.getVertex(0, polygon.v1).x + vertexs.getVertex(0, polygon.v2).x + vertexs.getVertex(0, polygon.v3).x
        sy = vertexs.getVertex(0, polygon.v1).y + vertexs.getVertex(0, polygon.v2).y + vertexs.getVertex(0, polygon.v3).y
        sz = vertexs.getVertex(0, polygon.v1).z + vertexs.getVertex(0, polygon.v2).z + vertexs.getVertex(0, polygon.v3).z
 #       logging.debug('ENV: addind x : '+str(vertexs.getVertex(0, polygon.v1).x*0.324)+' '+str(vertexs.getVertex(0, polygon.v2).x*0.324)+' '+str(vertexs.getVertex(0, polygon.v3).x*0.324))
 #       logging.debug('ENV: addind y : '+str(vertexs.getVertex(0, polygon.v1).y*0.892)+' '+str(vertexs.getVertex(0, polygon.v2).y*0.892)+' '+str(vertexs.getVertex(0, polygon.v3).y*0.892))
 #       logging.debug('ENV: addind z : '+str(vertexs.getVertex(0, polygon.v1).z)+' '+str(vertexs.getVertex(0, polygon.v2).z)+' '+str(vertexs.getVertex(0, polygon.v3).z))
        
        if polygon.v4 != 0:
            nbPoints = 4
            sx = sx + vertexs.getVertex(0, polygon.v4).x
            sy = sy + vertexs.getVertex(0, polygon.v4).y
            sz = sz + vertexs.getVertex(0, polygon.v4).z
 #           logging.debug('ENV: addind 4e x : '+str(vertexs.getVertex(0, polygon.v4).x*0.324))
 #           logging.debug('ENV: addind 4e y : '+str(vertexs.getVertex(0, polygon.v4).y*0.892))
 #           logging.debug('ENV: addind 4e z : '+str(vertexs.getVertex(0, polygon.v4).z))
 
            
        return (sx/nbPoints, sy/nbPoints, sz/nbPoints)

		
    # move, render and calculate reward. Say if the game is over
    def next(self, vitesse, direction):

       
        #By default no gain
        gain = 0
        score = 0
        done = False
           
        voiturePoint = self._move(vitesse, direction)
        
        target = self.roadPoints[self.target_index]
        
        if self._isCloseTo(voiturePoint, target):
            # Target is reached !
            # change of target
            self.target_index = self.target_index +1

            # gain the reward
            gain = self.reward
            # reset the reward
            self.reward = self.REWARD_FULL
        else :
            # we decrease the reward every step in order to force the car to reach the 
            # target as soon as possible
            self.reward = self.reward-1
            
            # if the target is still not reached, the game is over (-1)
            if self.reward <= 0:
                gain = self.GAMEOVER
                done = True
        
        # score de la partie
        self.totalScore = self.totalScore + gain
        score = self.totalScore
        
        if done:
            
            logging.debug('ENV: score of the game: '+str(self.totalScore))
            self._reset()
        # Render
        else :
            self._render()
        
        
        
                
        return gain, score, done



# static init of an instance for gameEngine
instance = Environnement()


#On passe en edit mode
#bm = bmesh.from_edit_mesh(road.data) 

#for f in bm.faces:
    #for v in f.verts:
    #    print(v.co)


# Add cube
#bpy.ops.mesh.primitive_cube_add(radius=2)
#newCube = bpy.context.active_object

  
#render frame
#bpy.data.scenes["Scene"].render.filepath = outputFile
#bpy.ops.render.render( write_still=True )
    
