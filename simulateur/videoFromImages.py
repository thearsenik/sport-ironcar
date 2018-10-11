# -*- coding: utf-8 -*-
"""
Created on Fri Sep 21 18:34:13 2018

@author: Utilisateur
"""

import commonVideo

#commonVideo.video_from_imagesDir('D:/dev/ironcar/output/debug/', 'D:/dev/ironcar/output/tracking.mp4')

firstNumImg=1
lastNumImg=949
imagePrefix='debugOutput'
imagesSuffix=''
imagesExtension='png'
listImages = ['D:/dev/ironcar/output/debug/'+imagePrefix+str(numImg).zfill(5)+imagesSuffix+'.'+imagesExtension for numImg in list(range(firstNumImg, lastNumImg+1))]
commonVideo.video_from_images(listImages, 'D:/dev/ironcar/output/blenderOutput.mp4', 24)