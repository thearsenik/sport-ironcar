import bge
import sys
sys.path.insert(0, '../simulateur')
import config



def render():
    global renderer

    data_array = bytearray(config.IMG_WIDTH*config.IMG_HEIGHT*4)
    renderer.refresh(data_array, 'BGRA')
    
    #remove alpha chanel
    size = (int)(len(data_array)*3/4)
    newBy = bytearray(size)
    i=0
    for j,x in enumerate(data_array):
        if (j+1)%4 != 0:
            newBy[i] = x
            i = i+1
            
    #image is flipped upside-down due to wrong texture mapping ?
    #we flip it by code...
    flipped = bytearray(size)
    img_w = config.IMG_WIDTH
    img_h = config.IMG_HEIGHT
    for i in range(img_h):
        for k in range(img_w):
            flipped[3*(i*img_w+k)] = newBy[3*((img_h-1-i)*img_w+k)]
            flipped[3*(i*img_w+k)+1] = newBy[3*((img_h-1-i)*img_w+k)+1]
            flipped[3*(i*img_w+k)+2] = newBy[3*((img_h-1-i)*img_w+k)+2]
    return flipped
    

cont = bge.logic.getCurrentController()
obj = cont.owner

camera_obj = obj.scene.objects['NOT_ACTIVE_CAMERA']
textured_obj = obj.scene.objects['sol']
tex = bge.texture.Texture(textured_obj, 0, 0)
tex.source = bge.texture.ImageRender(
    camera_obj.scene,
    camera_obj,
)
tex.source.capsize = [config.IMG_WIDTH,config.IMG_HEIGHT]
tex.source.background = [0, 0, 0, 0]
renderer = tex.source

 