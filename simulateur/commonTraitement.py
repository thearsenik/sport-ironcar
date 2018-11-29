import numpy as np
import cv2

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

def getDistance(rect):
    #if width < height
    distancePx = (rect[0][0]-100) #100 = img_Width/2
    
    distance = distancePx/100 #100 = img_Width/2
    
    return distance

def getHauteur(rect):
    #if width < height
    hauteurPy = (150-rect[0][1])
    
    hauteur = hauteurPy/150
    
    return hauteur

def perspective_warp(img, 
                     dst_size=(1200,900),
                     src=np.float32([(0,26),(200,26),(-239,150),(239+200,150)]),
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