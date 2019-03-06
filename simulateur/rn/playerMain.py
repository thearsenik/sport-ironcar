import time
import logging
import sys
sys.path.insert(0, '../')
import commonSocket as sock
import socket
from multiprocessing.connection import Listener
from multiprocessing.connection import Client
import config
import playerInputReader as input
import Player_Arnaud_forRN as Player


logging.basicConfig(filename=config.logFile,level=config.logLevelPlayer, format='%(asctime)s %(message)s')

addressRender = (config.RENDER_SERVER, config.RENDER_PORT)

def writeCommandFile(vitesse, direction, stop=False):
    message = None
    if (stop):
        message = '{\"stop\":\"true\"}'
    else:
        message = '{\"direction\":\"'+str(direction)+'\", \"speed\":\"'+str(vitesse)+'\"}'
    #nbTry=3
    #while (nbTry > 0):
    #    try:
    #        with open(config.commandFile, 'w') as outfile:
    #            outfile.write(message)
    #            outfile.close
    #            print('Write command done...')
    #            break
    #    except:
    #        nbTry = nbTry-1
    #        print('Write command delayed...')
    #        time.sleep(0.001)
    clientSocket = Client((config.COMMAND_SERVER, config.COMMAND_PORT), 'AF_INET')
    #clientSocket.send(struct.pack("L", len(message)))
    clientSocket.send(message)
    clientSocket.close()
    logging.debug("write command done... ")
            

def readGameResultFile():
    global gameResultListener
    logging.debug("listening for game result... ")
    gameResultSocket = gameResultListener.accept()
    data = sock.read_json(gameResultSocket)
    logging.debug("Json game result read: "+str(data))
    
    return data          

waitStateChanged = False
time1 = 0
time2 = 0
cpt = 0

gameResultListener = None
try:
    gameResultListener = Listener(addressRender, 'AF_INET')   
except OSError:  
    #socket is already in use... reuse it
    gameResultListener = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    gameResultListener.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    gameResultListener.bind((addressRender[0], addressRender[1]))    



reward_store = []
nb_step_store = []
jsonOutputFile = config.commandFile
stop = False
maxTotalScore = 440




try:
    #Boucle sur les tests
    nb_tests = 1
    numTest = 0
    while numTest < nb_tests:
        
        numTest += 1
        
        
        numGame = 0
        gamePlayer = Player.Player()
        
        # On boucle sur les parties... avec le meme Player
        nb_episodes = 5000
        while numGame < nb_episodes:
        
            numGame += 1
            print('New game: '+str(numGame))
            logging.debug('Start a new game: '+str(numGame))
            
            # Nouvelle partie, on boucle sur les steps...
            numStep = 0
    
            writeCommandFile(2, 0)
            data = readGameResultFile() 
            noImgCounter = 0
            actions = []
            
            #reset RN
            gamePlayer.startNewGame()
            
            while True:
                
                    if ('stop' in data):
                        print("STOP...")
                        logging.debug("STOP...")
                        stop = True
                        break
                    elif ('done' in data) and (data['done'] == True):
                        print ('GAME OVER...')
                        logging.info('GAME OVER... '+str(numGame)+' en '+str(numStep)+' steps score='+str(data['totalScore']))
                        logging.info('ACTIONS : '+str(actions))
                        # store results
                        totalScore = data['totalScore']
                        reward_store.append(totalScore)
                        nb_step_store.append(numStep)
                        # store rn state
                        if totalScore > maxTotalScore:
                            logging.info('SAVING new HIGHSCORE')
                            maxTotalScore = totalScore
                            gamePlayer.save()
                        # Exit game...
                        break
                    
                    reward = data['reward']
                    frame = input.readImageFromBlender()
                    if frame is None:
                        noImgCounter = noImgCounter+1
                        if noImgCounter == 10:
                            print('No image from game... waiting...')
                        if noImgCounter == 50:
                            print('Ok we abort this game...')
                            break
                        time.sleep(0.002)
                    else:
                        noImgCounter = 0 
                        numStep +=1
        
                        # get RN result
                        #logging.debug("got reward"+str(reward))
                        vitesse, direction = gamePlayer.compute(reward, frame, numGame, numStep)     
                        logging.debug('playerMain : action '+str(direction))
                        actions.append(direction)
        
                        #On ecrit l'action
                        writeCommandFile(vitesse, direction)
                        
                        # Wait for result from game engine
                        data = readGameResultFile()
        
            
            if stop:
                logging.debug('Abort due to stop command... ')
                break
            
        if stop:
            logging.debug('Abort due to stop command... ')
            break
                
except KeyboardInterrupt:
    print('interrupted!')           
 
finally:
    #Save nn model
    #gamePlayer.save()
    
    #On ecrit l'action stop pour arreter blender
    #writeCommandFile(None, None, True)
    
    print('maxTotalScore = '+str(maxTotalScore))
    logging.info('maxTotalScore = '+str(maxTotalScore))
        
    # draw results
    if len(reward_store) < 1000:
        import matplotlib.pylab as plt
        plt.title('Total Score')
        plt.plot(reward_store)
        plt.show()
        plt.close("all")
        plt.title('Nb step')
        plt.plot(nb_step_store)
        plt.show()
    else:
        resultat = []
        for i in range(0, 30):    
            nb = len([ val for val in reward_store if val>=i*100 and val<(i+1)*100 ])
            resultat.append(nb)
        import matplotlib.pylab as plt
        plt.title('Repartition des scores')
        plt.plot(resultat)
        plt.show()
    # write results

    

