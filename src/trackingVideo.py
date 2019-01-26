import cv2
import numpy as np
import argparse
import time
import commonVideo as common
import commonTraitement as utils

cap = cv2.VideoCapture(0)

font = cv2.FONT_HERSHEY_SIMPLEX

# Set there the file to use as input or comment the line to use the webcam
videoInputFile = "D:\\dev\\ironcar\\video\\film\\roadGameExtract1.mp4"
useVideoFile = True

# Set to True if we want to export the result in a video
outToFile = True

# construct the argument parse and parse the arguments
ap = argparse.ArgumentParser()
ap.add_argument("-v", "--video",
    help="path to the (optional) video file")
ap.add_argument("-b", "--buffer", type=int, default=64,
    help="max buffer size")
args = vars(ap.parse_args())


# video path was not supplied as argument 
if args.get("video", False):
    vs = cv2.VideoCapture(args["video"])
    useVideoFile = True
# constant path to video file
elif useVideoFile:
    vs = cv2.VideoCapture(videoInputFile)

# no input file... grab the reference to the webcam
else:
    vs = VideoStream(src=0).start()

# allow the camera or video file to warm up
time.sleep(2.0)

def detectAngle(frame, usingBirdEye=True):
    
    # Convert to birdeye
    if (usingBirdEye == True):
        frame = utils.perspective_warp(frame, dst_size=(1280,720))
        
    # Convert BGR to HSV
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

    # define range of blue color in HSV
    lower_yellow = np.array([0,69,94])
    upper_yellow = np.array([255,255,255])


    # Threshold the HSV image to get only blue colors
    mask = cv2.inRange(hsv, lower_yellow, upper_yellow)
    noiseless = utils.remove_noise(mask)

    # Bitwise-AND mask and original image
    ret, thresh = cv2.threshold(noiseless, 127, 255,0)
    im2,contours,hierarchy = cv2.findContours(thresh, 1, 2)
    if(len(contours)>0):
        contour = max(contours, key=cv2.contourArea)
        rect = cv2.minAreaRect(contour)
        angle = utils.getAngle(rect)
        box = cv2.boxPoints(rect)
        box = np.int0(box)
        cv2.drawContours(frame,[box], 0,(0,0,255),2)
        cv2.putText(frame, str(angle),(frame.shape[1] - 100, frame.shape[0] - 20), font, 1,(0,255,0),2,cv2.LINE_AA)
        if(angle>100):
            cv2.putText(frame, "turn left",(frame.shape[1] // 2, frame.shape[0] - 200), font, 1,(0,255,0),2,cv2.LINE_AA)
        elif(angle<80):
            cv2.putText(frame, "turn right",(frame.shape[1] // 2, frame.shape[0] - 200), font, 1,(0,255,0),2,cv2.LINE_AA)
        else:
            cv2.putText(frame, "straight",(frame.shape[1] // 2, frame.shape[0] - 200), font, 1,(0,255,0),2,cv2.LINE_AA)
    return frame

def detectAngleAndDistance(frame):
    global previousAngle
    
    # Convert to birdeye
    frame = utils.perspective_warp(frame, (1200,900))
    
    # Convert BGR to HSV
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

    # define range of blue color in HSV
    lower_yellow = np.array([0,69,94])
    upper_yellow = np.array([255,255,255])


    # Threshold the HSV image to get only blue colors
    mask = cv2.inRange(hsv, lower_yellow, upper_yellow)
    noiseless = utils.remove_noise(mask)

    # Bitwise-AND mask and original image
    ret, thresh = cv2.threshold(noiseless, 127, 255,0)
    im2,contours,hierarchy = cv2.findContours(thresh, 1, 2)
    

    
    if(len(contours)>0):
        contour = max(contours, key=cv2.contourArea)
        rectMax = cv2.minAreaRect(contour)
        print (rectMax)
        #contour le plus bas
        #plusBas = utils.getPlusBasContour(contours)
        
        #contour le plus bas dont taille superieure a max/2
        rects = [cv2.minAreaRect(forme) for forme in contours]
        aireMin = rectMax[1][0]*rectMax[1][1]/2
        contoursEntiers = [rect for rect in rects if rect[1][0]*rect[1][1] > aireMin]
        plusBasRectangle = utils.getPlusBasContour(contoursEntiers)
        rect = plusBasRectangle #cv2.minAreaRect(contour)
        angle = utils.getAngle(rect)
        print(angle)
        box = cv2.boxPoints(rect)
        box = np.int0(box)
        cv2.drawContours(frame,[box], 0,(0,0,255),2)
        cv2.putText(frame, str(angle),(frame.shape[1] - 100, frame.shape[0] - 20), font, 1,(0,255,0),2,cv2.LINE_AA)
        previousAngle = angle
    else:
        angle = previousAngle
    return frame, angle

def detectAngleDebug(frame):
    frame1 = detectAngle(frame, usingBirdEye=True)
    frame2 = detectAngle(frame, usingBirdEye=False)
    frameMerge = np.concatenate((frame1, frame2), axis=0)
    return frameMerge

if useVideoFile == False or outToFile == False:
    while True:
        # grab the current frame
        frame = vs.read()
    
        # handle the frame from VideoCapture or VideoStream
        frame = frame[1] if useVideoFile else frame
    
        # if we are viewing a video and we did not grab a frame,
        # then we have reached the end of the video
        if frame is None:
            break
    
        frame = detectAngleAndDistance(frame, usingBirdEye=true)
        
        cv2.imshow('frame',frame)
    #    cv2.imshow('mask',noiseless)
        #cv2.imshow('res',noiseless)
        k = cv2.waitKey(5) & 0xFF
        if k == 27:
            break
    
    cv2.destroyAllWindows()

else:
    from moviepy.editor import VideoFileClip
    
    #video birdeye
    videoInputFile="D:\\dev\\ironcar\\video\\film\\vueNormale\\vueNormale.avi"
    myclip = VideoFileClip(videoInputFile)
    output_vid = '../output/tracking.mp4'
    clip = myclip.fl_image(lambda image: detectAngle(image))
    clip.write_videofile(output_vid, audio=False)
