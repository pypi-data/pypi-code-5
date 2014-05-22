#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  LiveExample.py
#

from pyElphel import Elphel

cam = Elphel()

#Reduce the image size (full resolution is not workirg with RTSP streaming
cam.params['WOI_WIDTH'] = 300
cam.params['WOI_HEIGHT'] = 400

#Adjust exposure time
cam.params['EXPOS'] = 5000

#Set parameters to camera
cam.set_params()

#Start RTSP streaming
cam.init_live()

#Display the video
cam.display()

