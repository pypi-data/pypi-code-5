#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  FullResolutionGrab.py


#At full resolution RTSP is not working 
#so we use direct access to the buffer via imgsrv.php
import cStringIO as StringIO
import time
import cPickle as pkl
from pylab import *
from pyElphel import Elphel

cam = Elphel()

#Set full resolution
cam.params['WOI_WIDTH'] = 2592
cam.params['WOI_HEIGHT'] = 1936

#Adjust exposure time
cam.params['EXPOS'] = 6000

#Set parameters to camera
cam.set_params()


#Loop to record images
listImg = []
N = 10
tstart = time.time()

for i in range(N):
    listImg.append( cam.grab_image_slow() )
    
fps = N/(time.time() - tstart)
print("FPS = %0.2f"%fps)

#Transform binary images to array
listArrayImg = []
for img in listImg:
    listArrayImg.append( imread( StringIO.StringIO(img), format='jpg' ) )
     
#Save image list as pikle
pkl.dump(listArrayImg, open('test_mov_full.pkl','wb'), protocol=2 )

#Display images with matplotlib


f = imshow( listArrayImg[0] )
show( block = False )

for img in listArrayImg:
    f.set_data( img )
    draw()
    
show()


