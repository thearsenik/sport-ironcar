import cv2
import numpy as np

cap = cv2.VideoCapture(0)

font = cv2.FONT_HERSHEY_SIMPLEX

def remove_noise(img):
	kernel = np.ones((5,5),np.uint8)
	erosion = cv2.erode(img,kernel,iterations = 2)
	dilation = cv2.dilate(erosion,kernel,iterations = 2)
	return dilation

def grayscale(img):
    return cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)

def getAngle(rect):
    #if width < height
    if(rect[1][0] < rect[1][1]):
        angle = 90 - rect[2]
    else:
        angle = -rect[2]
    return angle

while(1):

    # Take each frame
    _, frame = cap.read()

    # Convert BGR to HSV
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

    # define range of blue color in HSV
    lower_blue = np.array([50,165,165])
    upper_blue = np.array([156,255,255])

    # Threshold the HSV image to get only blue colors
    mask = cv2.inRange(hsv, lower_blue, upper_blue)
    noiseless = remove_noise(mask)

    # Bitwise-AND mask and original image
    ret, thresh = cv2.threshold(noiseless, 127, 255,0)
    im2,contours,hierarchy = cv2.findContours(thresh, 1, 2)
    if(len(contours)>0):
        contour = max(contours, key=cv2.contourArea)
        rect = cv2.minAreaRect(contour)
        angle = getAngle(rect)
        box = cv2.boxPoints(rect)
        box = np.int0(box)
        cv2.drawContours(frame,[box], 0,(0,0,255),2)
        cv2.putText(frame, str(angle),(int(rect[0][0]),int(rect[0][1])), font, 1,(0,255,0),2,cv2.LINE_AA)


    cv2.imshow('frame',frame)
    #cv2.imshow('mask',noiseless)
    #cv2.imshow('res',noiseless)
    k = cv2.waitKey(5) & 0xFF
    if k == 27:
        break

cv2.destroyAllWindows()
