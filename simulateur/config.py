#FILES
logFile='d:/dev/ironcar/sport-ironcar/output/outputRenderer/render_log.txt'
renderedImageFile='d:/dev/ironcar/sport-ironcar/output/outputRenderer/road.png'
detectionFile='d:/dev/ironcar/sport-ironcar/output/outputAnalyser/detection.json'
commandFile='d:/dev/ironcar/sport-ironcar/output/outputAnalyser/command.json'
gameOutputFile='d:/dev/ironcar/sport-ironcar/output/outputRenderer/result.json'
gamesDir='d:/dev/ironcar/sport-ironcar/output/games/'
debugDir='d:/dev/ironcar/output/debug'
analyzerDebugDir='d:/dev/ironcar/output/debug/png'
videoDebugDir = "d:/dev/ironcar/output/debug/video"
rnCheckpointsDir="d:/dev/ironcar/output/rn"
rnCheckpointsFile = rnCheckpointsDir+"/model.ckpt"
carLocation = 'd:/dev/ironcar/sport-ironcar/output/outputRenderer/carLocation.json'
gameEngineExecutable = "‪d:\\dev\\ironcar\\ironcarAgfa\\sport-ironcar\\blender\\roadGameEngine.exe"
#VARIABLES
PRODUCE_DEBUG_IMG = True
#IMG_WIDTH=200
#IMG_HEIGHT=150
IMG_WIDTH=304
IMG_HEIGHT=201
#SOCKET
COMMAND_SERVER='127.0.0.1'
COMMAND_PORT=6549
RENDER_SERVER='127.0.0.1'
RENDER_PORT=6559

#LOG LEVELS
#CRITICAL = 50
#FATAL = CRITICAL
#ERROR = 40
#WARNING = 30
#WARN = WARNING
#INFO = 20
#DEBUG = 10
#NOTSET = 0
logLevelGameEngine=20
logLevelPlayer=20

simulateInertie = False