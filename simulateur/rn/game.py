import logging
import sys
sys.path.insert(0, '../')
import pathConfig
#import bmesh 
from mathutils import Vector, Matrix

# reload files in blender if they changed
import importlib
importlib.reload(pathConfig)
importlib.reload(Environnement)


logging.basicConfig(filename=pathConfig.logFile,level=logging.DEBUG)



def readCommandFile():
    
    #Test if file exist
    jsonFile = Path(pathConfig.commandFile)
    if jsonFile.exists(): 
        commandData = None     
        with open(pathConfig.commandFile) as data_file: 
            commandData = json.load(data_file)
        #suppression du fichier d'entree
        try:
            os.remove(pathConfig.commandFile)
        except:
            return None
        return commandData
    else:
        return None
    
    

def playNewGame(numGame):
    global env
    global logging
    numImg = 0
    
    env.reset()

    stop = false; 
    while True:
        data = readCommandFile()
        if (data == None):
            print('Nothing to read...')
            #On attend un peu
            time.sleep(0.1)
        else:
            if ('stop' in data):
                print("STOP...")
                env.stop()
                stop = True
                break
            
            numImg +=1
            imageFile = pathConfig.gamesDir+"\\game"+str(numGame).zfill(5)+"_"+str(numImg).zfill(5)+'.png'
            actionRot = data["rotZ"]
            
                        
            # Get reward

            # calculate next position, and reward for the choosen action
            # 'imageFile' is the new render file url
            reward, done = env.next(actionRot, imageFile)
            
            # Copy rendered view to output image...
            copyfile(imageFile, pathConfig.renderedImageFile)
            
            if done:
                print ('GAME OVER...')
                logging.debug('GAME OVER...')
                # Exit game...
                break

            
            #On attend un peu avant de traiter la commande suivante
            time.sleep(0.1)

    return env.totalScore, stop
    



env = Environnement()
env.start()
numGame = 0
while True:

    numGame += 1
    print('New game: '+str(numGame))
    logging.debug('Start a new game: '+str(numGame))
    
          
    result, stop = playNewGame(numGame)
    
    if stop:
        logging.debug('Abort due to stop command... '+str(result))
        break
    else:
        logging.debug('score of the game: '+str(result))

    
