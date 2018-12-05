import bge

IMG_SIZE = [200,150]


def render():
    global renderer
    global IMG_SIZE
    data_array = bytearray(IMG_SIZE[0]*IMG_SIZE[1]*4)
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
    img_w = 200
    img_h = 150
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
tex.source.capsize = IMG_SIZE
tex.source.background = [0, 0, 0, 0]
renderer = tex.source

 