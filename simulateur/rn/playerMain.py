import time
import logging
import numpy
import sys
import matplotlib
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
maxTotalScore = 0
maxGameNb = 0
minTotalScoreForSaving = 440




try:
    #Boucle sur les tests
    nb_tests = 1
    numTest = 0
    while numTest < nb_tests:
        
        numTest += 1
        
        
        numGame = 0
        gamePlayer = Player.Player()
        
        # On boucle sur les parties... avec le meme Player
        nb_episodes = 10000
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
            startIndex = 0
            if ('startIndex' in data):
                startIndex = data['startIndex']
            
            #reset RN
            gamePlayer.startNewGame(startIndex)
            
            while True:
                
                    if ('stop' in data):
                        print("STOP...")
                        logging.debug("STOP...")
                        stop = True
                        break
                    elif ('done' in data) and (data['done'] == True):
                        print ('GAME OVER...')
                        logging.info('GAME OVER... '+str(numGame)+' en '+str(numStep)+' steps score='+str(data['totalScore']) + '  maxTotalScore = '+str(maxTotalScore) + ' for game ' + str(maxGameNb))
                        logging.info('ACTIONS : '+str(actions))
                        # store results
                        totalScore = data['totalScore']
                        reward_store.append(totalScore)
                        nb_step_store.append(numStep)
                        if totalScore > maxTotalScore:
                            maxTotalScore = totalScore
                            maxGameNb = numGame
                            logging.info('New high score of '+str(maxTotalScore) + ' for game ' + str(maxGameNb))
                        # store rn state
                        if totalScore > minTotalScoreForSaving:
                            logging.info('SAVING new HIGHSCORE')
                            minTotalScoreForSaving = totalScore
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
                        vitesse, direction, isRandomChoice = gamePlayer.compute(reward, frame, numGame, numStep)     
                        directionStr = str(direction)
                        if isRandomChoice:
                            directionStr = directionStr + '*'
                            logging.debug('playerMain : random action '+directionStr)
                            actions.append(directionStr)
                        else:
                            logging.debug('playerMain : action '+directionStr)
                            actions.append(directionStr)
        
                        #On ecrit l'action
                        writeCommandFile(vitesse, directionStr)
                        
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
    
    print('maxTotalScore = '+str(maxTotalScore) + ' for game ' + str(maxGameNb))
    logging.info('maxTotalScore = '+str(maxTotalScore) + ' for game ' + str(maxGameNb))
        
    # draw results
    fig = matplotlib.pyplot.gcf()
    fig.set_size_inches(100, 10.5)
    fig.suptitle('Total Score')
    ax = matplotlib.pyplot.gca()
    ax.xaxis.set_major_locator(matplotlib.pyplot.MultipleLocator(200))
    #ax.xaxis.set_minor_locator(matplotlib.pyplot.MultipleLocator(200))
    matplotlib.pyplot.scatter(numpy.arange(len(reward_store)), reward_store)
    fig.savefig(config.debugDir+'/result.png', dpi=100)
        
    
    resultat = []
    for i in range(0, 30):    
        nb = len([ val for val in reward_store if val>=i*100 and val<(i+1)*100 ])
        resultat.append(nb)
    import matplotlib.pylab as plt
    plt.title('Repartition des scores')
    plt.plot(resultat)
    plt.show()
    # write results

    

