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

def perspective_warp(img, 
                     dst_size=(1280,720),
                     src=np.float32([(0.43,0.65),(0.58,0.65),(0.1,1),(1,1)]),
                     dst=np.float32([(0,0), (1, 0), (0,1), (1,1)])):
    img_size = np.float32([(img.shape[1],img.shape[0])])
    src = src* img_size
    # For destination points, I'm arbitrarily choosing some points to be
    # a nice fit for displaying our warped result 
    # again, not exact, but close enough for our purposes
    dst = dst * np.float32(dst_size)
    # Given src and dst points, calculate the perspective transform matrix
    M = cv2.getPerspectiveTransform(src, dst)
    # Warp the image using OpenCV warpPerspective()
    warped = cv2.warpPerspective(img, M, dst_size)
    return warped