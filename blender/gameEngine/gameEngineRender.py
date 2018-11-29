import bge

IMG_SIZE = [200,150]


def render():
    global renderer
    global IMG_SIZE
    data_array = bytearray(IMG_SIZE[0]*IMG_SIZE[1]*4)
    renderer.refresh(data_array, 'BGRA')
    return data_array
    

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

 