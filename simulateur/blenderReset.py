import numpy as np
import bpy
from mathutils import Vector, Matrix
from pathlib import Path
import os
import json
import time

renderedImageFile='D:/dev/ironcar/ironcarAgfa/sport-ironcar/output/outputRenderer/road.jpg'

def initializeVoiturePosition():
    voiture = bpy.data.objects['Voiture']
    voiture.location = (18.3535,14.8599,0.348387)
    voiture.rotation_euler = (0,0,94.3)
    

initializeVoiturePosition()

