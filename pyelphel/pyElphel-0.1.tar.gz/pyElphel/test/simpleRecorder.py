#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  simpleRecorder.py
import time
import cPickle as pkl
from pyElphel import Elphel

cam = Elphel()

#Reduce the image size (full resolution is not workirg with RTSP streaming
cam.params['WOI_WIDTH'] = 300
cam.params['WOI_HEIGHT'] = 400

#Adjust exposure time
cam.params['EXPOS'] = 6000

#Set parameters to camera
cam.set_params()

#Start RTSP streaming
cam.init_live()


#Loop to record images
listImg = []
N = 200
tstart = time.time()

for i in range(N):
    listImg.append( cam.grab_image().copy() )
    
fps = N/(time.time() - tstart)
print("FPS = %0.2f"%fps)

#Save image list as pikle
pkl.dump(listImg, open('test_mov.pkl','wb'), protocol=2 )

#Display images with matplotlib
from pylab import *

f = imshow( listImg[0] )
show( block = False )

for img in listImg:
    f.set_data( img )
    draw()
    
show()
