import numpy as np
import cv2


def concat_images(frame1, frame2, axis=0):
    frameMerge = np.concatenate((frame1, frame2), axis=0)
    return frameMerge

def concat_videos(
                     video1,
                     video2,
                     outputVideo = '../output/merge2Videos.mp4',
                     tmpDir = '../output/tmp',
                     axis=0 #0 vertical, 1 horizontal
                     ):
    v1 = cv2.VideoCapture(video1)
    v2 = cv2.VideoCapture(video2)
    
    i=0
    from PIL import Image
    while True:
            # grab the current frame
            frame1 = v1.read()
            frame2 = v2.read()
            frame3 = v3.read()
        
            # handle the frame from VideoStream
            frame1 = frame1[1]
            frame2 = frame2[1]
            frame3 = frame3[1]
        
            # if we are viewing a video and we did not grab a frame,
            # then we have reached the end of the video
            if frame1 is None:
                break
            if frame2 is None:
                break
            if frame3 is None:
                break
        
            frame = concat_images(frame1, frame2, axis)
            outputImg = tmpDir+'/'+str(i).zfill(4)+'.jpg'
            output = Image.fromarray(frame)
            output.save(outputImg)
            i = i+1
            
    v1.release()
    v2.release()
    
    #make a video from images
    from moviepy.editor import ImageSequenceClip
    clip = ImageSequenceClip(tmpDir, fps=24)
    clip.write_videofile(outputVideo, audio=False)

    
    
    
def concat_3_videos(
                     video1,
                     video2,
                     video3,
                     outputVideo = '../output/merge3Videos.mp4',
                     tmpDir = '../output/tmp',
                     axis=0 #0 vertical, 1 horizontal
                     ):
    v1 = cv2.VideoCapture(video1)
    v2 = cv2.VideoCapture(video2)
    v3 = cv2.VideoCapture(video3)
    
    i=0
    from moviepy.editor import ImageClip
    from PIL import Image
    while True:
            # grab the current frame
            frame1 = v1.read()
            frame2 = v2.read()
            frame3 = v3.read()
        
            # handle the frame from VideoCapture or VideoStream
            frame1 = frame1[1]
            frame2 = frame2[1]
            frame3 = frame3[1]
        
            # if we are viewing a video and we did not grab a frame,
            # then we have reached the end of the video
            if frame1 is None:
                break
            if frame2 is None:
                break
            if frame3 is None:
                break
        
            frame = concat_images(frame1, frame2, axis)
            frame = concat_images(frame, frame3, axis)
            outputImg = tmpDir+'/'+str(i).zfill(4)+'.jpg'
            #imClip = ImageClip(frame)
            #imClip.
            output = Image.fromarray(frame)
            output.save(outputImg)
            #cv2.imwrite(outputImg, frame)
            i = i+1
            
    v1.release()
    v2.release()
    v3.release()
    
    #make a video from images
    from moviepy.editor import ImageSequenceClip
    clip = ImageSequenceClip(tmpDir, fps=24)
    clip.write_videofile(outputVideo, audio=False)
    
def video_from_imagesDir(dirImages, videoOuputFile):
    from moviepy.editor import ImageSequenceClip
    clip = ImageSequenceClip(dirImages, fps=24)
    clip.write_videofile(videoOuputFile, audio=False)
    
def video_from_images(listImagesFiles, videoOuputFile, fps=24):
    from moviepy.editor import ImageSequenceClip
    clip = ImageSequenceClip(listImagesFiles, fps)
    clip.write_videofile(videoOuputFile, audio=False)
 
