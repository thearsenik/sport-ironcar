import numpy as np
import cv2
import math

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

def getAnglePoints(point1, point2):
    distX = point2[0] - point1[0];
    distY = math.fabs(point2[1] - point1[1]);
    return rad2deg(math.atan2(distX, distY)) + 90

def rad2deg(x):
    return x * 180.0 / math.pi

def deg2rad(x):
    return x * math.pi / 180.0

def getDistance(rect):
    #if width < height
    distancePx = (rect[0][0]-600)

    distance = distancePx/600

    return distance

def getHauteur(rect):
    #if width < height
    hauteurPy = (900-rect[0][1])

    hauteur = hauteurPy/900

    return hauteur

def perspective_warp(img,
                     dst_size=(1200,900),
                     src=np.float32([(0,154),(1200,154),(-1431,900),(1431+1200,900)]),
                     dst=np.float32([(0,0), (1, 0), (0,1), (1,1)])):
 #   img_size = np.float32([(img.shape[1],img.shape[0])])
 #   src = src* img_size
    # For destination points, I'm arbitrarily choosing some points to be
    # a nice fit for displaying our warped result
    # again, not exact, but close enough for our purposes
    dst = dst * np.float32(dst_size)
    # Given src and dst points, calculate the perspective transform matrix
    M = cv2.getPerspectiveTransform(src, dst)
    # Warp the image using OpenCV warpPerspective()
    warped = cv2.warpPerspective(img, M, dst_size)
    return warped


def getPlusBasContour(contours):
    contoursOrdered = sorted(contours, key=lambda rect: rect[0][1], reverse=True)   # sort by top left corner height
    return  contoursOrdered[0]

def getPlusHautContour(contours):
    contoursOrdered = sorted(contours, key=lambda rect: rect[0][1], reverse=False)   # sort by top left corner height
    return  contoursOrdered[0]

lastContours = None
def getContoursPlusEloigne(contours):
    global lastContours
    contoursOrdered = sorted(contours, key=lambda rect: math.pow(math.fabs(rect[0][0] - 600), 2) + math.pow(rect[0][1]-900, 2), reverse=True) # get the closer top left corner to the previous one
    lastContours = contours
    return contoursOrdered[0]
