import cv2
import numpy as np
import argparse
import time
import commonVideo as common

cap = cv2.VideoCapture(0)

font = cv2.FONT_HERSHEY_SIMPLEX


# construct the argument parse and parse the arguments
ap = argparse.ArgumentParser()
ap.add_argument("-v", "--video",
    help="path to the (optional) video file")
ap.add_argument("-b", "--buffer", type=int, default=64,
    help="max buffer size")
args = vars(ap.parse_args())


# if a video path was not supplied, grab the reference
# to the webcam
if not args.get("video", False):
    vs = VideoStream(src=0).start()

# otherwise, grab a reference to the video file
else:
    vs = cv2.VideoCapture(args["video"])

# allow the camera or video file to warm up
time.sleep(2.0)

while True:
    # grab the current frame
    frame = vs.read()

    # handle the frame from VideoCapture or VideoStream
    frame = frame[1] if args.get("video", False) else frame

    # if we are viewing a video and we did not grab a frame,
    # then we have reached the end of the video
    if frame is None:
        break

    # Convert BGR to HSV
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

    # define range of blue color in HSV
    lower_yellow = np.array([0,69,94])
    upper_yellow = np.array([255,255,255])


    # Threshold the HSV image to get only blue colors
    mask = cv2.inRange(hsv, lower_yellow, upper_yellow)
    noiseless = common.remove_noise(mask)

    # Bitwise-AND mask and original image
    ret, thresh = cv2.threshold(noiseless, 127, 255,0)
    im2,contours,hierarchy = cv2.findContours(thresh, 1, 2)
    if(len(contours)>0):
        contour = max(contours, key=cv2.contourArea)
        rect = cv2.minAreaRect(contour)
        angle = common.getAngle(rect)
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

    cv2.imshow('frame',frame)
#    cv2.imshow('mask',noiseless)
    #cv2.imshow('res',noiseless)
    k = cv2.waitKey(5) & 0xFF
    if k == 27:
        break

cv2.destroyAllWindows()




