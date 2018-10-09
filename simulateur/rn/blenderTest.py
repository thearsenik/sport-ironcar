import numpy as np
import bpy
import bmesh 
from mathutils import Vector, Matrix

    
#get object
road = bpy.data.objects['roadPart']

#add object a chaque intervalle
for face in road.data.polygons:
    print (face.center)

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
    
