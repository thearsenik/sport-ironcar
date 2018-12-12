import bpy
import logging
#import moveController
import sys
sys.path.insert(0, '../')
import pathConfig
#import bmesh 
from mathutils import Vector, Matrix

# reload files in blender if they changed
import importlib
importlib.reload(pathConfig)
#importlib.reload(moveController)


logging.basicConfig(filename=pathConfig.logFile,level=logging.DEBUG)


class Environnement:

    REWARD_FULL = 10
    GAMEOVER = -1
    RAYON = 1.78


    def __init__(self):
        self.targets = []
        self.reward = self.REWARD_FULL
        self.target_index = 0
        self.totalScore = 0
        
        
    def reset(self):
        self._stop()
        self._start()
        
        
    def _initializeVoiturePosition(self, location = (18.3535,14.8599,0.348387), rotation = (0,0,4.3*3.1415/180)):
        voiture = bpy.data.objects['Voiture']
        voiture.location = location
        voiture.rotation_euler = rotation
    
    
    def _start(self): 
        
        self.reward = self.REWARD_FULL
        self.totalScore = 0
        self.target_index = 0
        
        #get road object
        roadOriginal = bpy.data.objects['roadPart']
        #make it active
        #bpy.context.active_object = roadOriginal
        bpy.context.scene.objects.active = roadOriginal
        
        # dupplicate
        road = roadOriginal.copy()
        road.data = roadOriginal.data.copy()
        bpy.data.scenes[0].objects.link(road)
        # rename
        road.name = 'roadPartCopy'

        # set the object to active to apply modifiers
        for ob in bpy.context.selected_objects:
            ob.select = False
        bpy.context.scene.objects.active = road
        bpy.ops.object.modifier_apply(apply_as='DATA', modifier="Array")
        bpy.ops.object.modifier_apply(apply_as='DATA', modifier="Curve")
        
        # targets tous les N intervalles
        # marche pas : self.targets = road.data.polygons[0::2]...
        # bon ben target a chaque tuile...
        self.targets = road.data.polygons

        #for face in road.data.polygons[0::2]:
        #    print (face.center)
        
        self._initializeVoiturePosition()
            
    
    def _stop(self):
        roadItems = [obj for obj in bpy.data.objects if obj.name == 'roadPartCopy']
        if roadItems:
            road = roadItems[0]
            #make it active
            road.select = True
            # remove it
            bpy.ops.object.delete()
        
    
    # Check if the car (point1) is close to the goal (point2)
    # check that distance^2 < R^2
    def _isCloseTo(self, point1, point2):
        # distance ^2
        distance2 = (point1[0]-point2[0])**2 + (point1[1]-point2[1])**2 + (point1[2]-point2[2])**2
        return distance2 < self.RAYON**2
    
    # Move the car
    def _move(self, movx, movy, rotZ):
        global logging
    
        #get object
        voiture = bpy.data.objects['Voiture']
        #move object
        loc = Matrix.Translation((movx, movy, 0))
        voiture.matrix_basis *= loc
        voiture.rotation_euler[2] = voiture.rotation_euler[2] + rotZ
    #    trans_local = Vector((movx, movy, 0.0))
    #    trans_world = voiture.matrix_world.to_3x3() * trans_local
    #    voiture.matrix_world.translation += trans_world
        
    #    logging.debug('new position = ('+str(voiture.location[0])+','+str(voiture.location[1])+','+str(voiture.location[2])+')')
    #    logging.debug('new angle = '+str(voiture.rotation_euler[2]/3.1415*180))
    
    
    def _render(self):
        #render frame
        bpy.data.scenes["Scene"].render.filepath = pathConfig.renderedImageFile
        bpy.ops.render.render( write_still=True )

    def _writeStepResult(self, gain, totalScore, done):
        message = '{\"reward\":'+str(gain)+', \"done\":'+str(done)+', \"totalScore\":'+str(totalScore)+'}'
        nbTry=3
        while (nbTry > 0):
            try:
                with open(pathConfig.gameOutputFile, 'w') as outfile:
                    outfile.write(message)
                    outfile.close
                    break
            except:
                nbTry = nbTry-1
                time.sleep(0.001)

    # move, render and calculate reward. Say if the game is over
    def next(self, x, y, z, rotZ):

       
        #By default no gain
        gain = 0
        done = False
           
        voiturePoint = [float(x), float(y), float(z)]
        
        target = self.targets[self.target_index].center
        
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
        
        
        # Render
        #self._render()
        
                
        # output result
        self._writeStepResult(gain, self.totalScore, done)
                
        return gain, done

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
    
