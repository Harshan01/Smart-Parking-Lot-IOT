# import the necessary packages
from picamera.array import PiRGBArray
from picamera import PiCamera
import time
import cv2
# initialize the camera and grab a reference to the raw camera capture
camera = PiCamera()
#rawCapture = PiRGBArray(camera)
# allow the camera to warmup
time.sleep(2)
# grab an image from the camera
#camera.capture(rawCapture, format="bgr")
#image = rawCapture.array
camera.capture('./Picamtestdirect.jpg')
# display the image on screen and wait for a keypress
#cv2.imwrite("./PicamTestImage.png", image)
#cv2.waitKey(0)
