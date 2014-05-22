#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  pyElphel.py
#  
#  author: chauvet <chauvet[at]ipgp[dot]com>
#  version: 0.1
#  date: 21.05.2014
#
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2 of the License, or
#  (at your option) any later version.
#  
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#  
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#  MA 02110-1301, USA.
import cv2
import urllib2
from xml.etree import ElementTree
import time

class Elphel:
        """
        Class pour controler les camera elphel
        """   
    
        def __init__(self, ip='192.168.0.9', debug=False):

                #Ip address of the camera
                self.ip = ip 
                self.baseurl = "http://%s/"%ip
                
                #Intialise parameters dictionnary 
                self.init_params()
                
                #debug flag to print requests and etc...
                self.bug = debug
                
        def set_params(self):
                """
                SET A PARAMETER TO THE CAMERA using parsedit.php
                http://wiki.elphel.com/index.php?title=Changing_camera_parameters
                """

                set_url = self.baseurl + "parsedit.php?immediate"

                #For each key complete the adress &NAME=VALUE
                for k in self.params.keys():
                        set_url += "&%s=%s"%(k,self.params[k])
                        
                #Send param to WWW
                resp = urllib2.urlopen(set_url)
                
                if self.bug:
                        print set_url
                
        def get_all_params(self):
                """
                Retrive all parameters from the www
                """
                
                all_param_url = self.baseurl + "parsedit.php?immediate&SENSOR_RUN&BAYER&FP1000SLIM&CLK_FPGA&CLK_SENSOR&FPGA_XTRA&TRIG&EXPOS&VIRT_KEEP&VIRT_WIDTH&VIRT_HEIGHT&WOI_LEFT&WOI_TOP&WOI_WIDTH&WOI_HEIGHT&FLIPH&FLIPV&FPSFLAGS&DCM_HOR&DCM_VERT&BIN_HOR&BIN_VERT&FPGATEST&TESTSENSOR&COLOR&FRAMESYNC_DLY&PF_HEIGHT&BITS&SHIFTL&FPNS&FPNM&VIRTTRIG&GAINR&GAING&GAINB&GAINGB&RSCALE_CTL&GSCALE_CTL&BSCALE_CTL&FATZERO&QUALITY&PORTRAIT&CORING_INDEX&COLOR_SATURATION_BLUE&COLOR_SATURATION_RED&VIGNET_AX&VIGNET_AY&VIGNET_BX&VIGNET_BY&VIGNET_C&VIGNET_SHL&SCALE_ZERO_IN&SCALE_ZERO_OUT&DGAINR&DGAING&DGAINGB&DGAINB&CORING_PAGE&SENSOR_PHASE&TEMPERATURE_PERIOD&AUTOEXP_ON&HISTWND_RWIDTH&HISTWND_RHEIGHT&HISTWND_RLEFT&HISTWND_RTOP&AUTOEXP_EXP_MAX&FOCUS_SHOW&FOCUS_SHOW1&RFOCUS_LEFT&RFOCUS_WIDTH&RFOCUS_TOP&RFOCUS_HEIGHT&FOCUS_FILTER&TRIG_CONDITION&TRIG_DELAY&TRIG_OUT&TRIG_PERIOD&TRIG_BITLENGTH&EXTERN_TIMESTAMP&XMIT_TIMESTAMP&SKIP_FRAMES&I2C_QPERIOD&I2C_BYTES&IRQ_SMART&OVERSIZE&GTAB_R&GTAB_G&GTAB_GB&GTAB_B&COMPRESSOR_RUN&COMPMOD_BYRSH&COMPMOD_TILSH&COMPMOD_DCSUB&DAEMON_EN&DAEMON_EN_AUTOEXPOSURE&DAEMON_EN_STREAMER&DAEMON_EN_CCAMFTP&DAEMON_EN_CAMOGM&DAEMON_EN_AUTOCAMPARS&DAEMON_EN_TEMPERATURE&AEXP_FRACPIX&AEXP_LEVEL&HDR_DUR&HDR_VEXPOS&EXP_AHEAD&AE_THRESH&WB_THRESH&AE_PERIOD&WB_PERIOD&WB_MASK&WB_EN&WB_WHITELEV&WB_WHITEFRAC&WB_MAXWHITE&WB_SCALE_R&WB_SCALE_GB&WB_SCALE_B&GAIN_MIN&GAIN_MAX&GAIN_CTRL&GAIN_STEP&ANA_GAIN_ENABLE&FTP_PERIOD&FTP_TIMEOUT&FTP_UPDATE&MAXAHEAD&HIST_DIM_01&HIST_DIM_23&TASKLET_CTL&HISTMODE_Y&HISTMODE_C&SKIP_DIFF_FRAME&PROFILING_EN&STROP_MCAST_EN&STROP_MCAST_IP&STROP_MCAST_PORT&STROP_MCAST_TTL&STROP_AUDIO_EN&STROP_AUDIO_RATE&STROP_AUDIO_CHANNEL&STROP_FRAMES_SKIP&AUDIO_CAPTURE_VOLUME&MULTI_PHASE_SDRAM&MULTI_PHASE1&MULTI_PHASE2&MULTI_PHASE3&MULTI_SEQUENCE&MULTI_FLIPH&MULTI_FLIPV&MULTI_MODE&MULTI_HBLANK&MULTI_CWIDTH&MULTI_VBLANK&MULTI_WIDTH1&MULTI_WIDTH2&MULTI_WIDTH3&MULTI_HEIGHT1&MULTI_HEIGHT2&MULTI_HEIGHT3&MULTI_LEFT1&MULTI_LEFT2&MULTI_LEFT3&MULTI_TOP1&MULTI_TOP2&MULTI_TOP3&MULTI_SELECTED&TEMPERATURE01&TEMPERATURE23&SENS_AVAIL&FPGA_TIM0&DLY359_OUT&DLY359_P1&DLY359_P2&DLY359_P3&DLY359_C1&DLY359_C2&DLY359_C3&MULTI_CFG&DEBUG"
                
                #Extract params names form the adress
                params = all_param_url.split('&')[1:]
                
                #Get values for these params the all_parmas_url gives a xml file
                xmldata = urllib2.urlopen( all_param_url, timeout=2 ) 
                tree = ElementTree.parse( xmldata )
                
                
                #Find value for each params
                for p in params:
                        #extract the param from xml
                        node = tree.find( p )
                                
                        self.params[ p ] = int(node.text)


       
        def init_params(self):
                """
                CREATE DICT WITH ALL PARAMETERS
                """
        
                #Init params dict
                self.params = {} 
                
                #Load all params from the camera
                try:
                        self.get_all_params()
                except:
                        print("""
                        Camera not connected
                        
                        Please check your connection parameters
                        
                        Example
                        -------
                        Adress: 192.168.0.10
                        Netmask: 255.255.255.0
                        Gateway: 192.168.0.9
                        """)
                        
        
                #Remove autoexposure and others
                self.optimise_params()
                
        def optimise_params(self):
                """
                Remove all atomatic crap from elphel to speed up FPS
                """
                
                for p in [ "AUTOEXP_ON", "DAEMON_EN_AUTOEXPOSURE", "DAEMON_EN", "STROP_MCAST_EN","WB_EN", "XMIT_TIMESTAMP", "ANA_GAIN_ENABLE"]:
                        self.params[ p ] = 0
                
                
        
        def grab_image_slow(self):
                """
                Grab image using imgsrv that access to the camera buffer
                this mode is slower than grab_image but can acces image 
                in full resotlution at quite the max FPS possible
                """
                
                grab_url = "http://%s:8081/towp/save/torp/wait/img/next/save"%self.ip
                cur_img = urllib2.urlopen( grab_url ).read()
                
                return cur_img
        

        def init_live(self):
                """
                Capture using opencv2 rtsp protocol
                """
                
                #La full resolution ne marche pas avec cette methode resolution max 2048x1088
                
                if self.params['WOI_WIDTH'] > 2048 and self.params['WOI_HEIGHT'] > 1088:
                        print("Resolution is to large for rtsp stream use the grab_image_slow method WOI_WIDTH > 2048 and WOI_HEIGHT > 1088")
                        print("Resolution set to WOI_WIDTH = 2048 and WOI_HEIGHT = 1088")
                        #Downscale resolution to 
                        self.params['WOI_WIDTH'] = 2048
                        self.params['WOI_HEIGHT'] = 1088
                        self.set_params()
                        
                else:
                        #check if DAEMON_EN_STREAMER is setup
                        if self.params['DAEMON_EN_STREAMER'] == 0:
                                self.params['DAEMON_EN_STREAMER'] = 1
                                self.set_params()
                                print("DEAMON_EN_STREAMER set to 1")
                                
                        #Init videocapture object
                        self.live = cv2.VideoCapture("rtsp://%s:554"%self.ip)
                        
                
        def grab_image(self):
                """
                Grab an image using RTSP protocol via openCV
                """
                
                info, img = self.live.read()
                
                return img
                

        def display(self):
                """
                Live display
                """
                #To display fps
                N = 50 # number of immage to calculate the fps
                frame = 0
                fps = 0
                ta = time.time()
                
                #Check if we need to init rtsp connection
                try:
                        self.live
                except:
                        print('Start RTSP connection in self.live')
                        self.init_live()
                  
                #Loop to display images
                while(True):
                        
                        if frame == 0:
                                #Reset time
                                ta = time.time()
                        
                        #Get image
                        img = self.grab_image()
                        
                        if frame == N :
                                #compute FPS
                                fps = N/(time.time() - ta)
                                #reset cpt
                                frame = 0
                        else:
                                frame += 1
                                
                        #Put text on image        
                        cv2.putText(img,"Live FPS=%0.2f"%fps, (5,20), cv2.FONT_HERSHEY_PLAIN, 1, (0,0,255))
                        
                        #Dispaly img
                        cv2.imshow('PRESS q TO EXIT', img) 
                                
                        
                        #Manage keys
                        if cv2.waitKey(1) & 0xFF == ord('q'):
                                break
                                
                cv2.destroyAllWindows()
                
        
        #Methode to use with statement
        def __exit__(self, type, value, traceback):
                try:
                        self.live.release()
                except:
                        pass
        
        #Methode to use with statement (with Elphel as cam:)
        def __enter__(self):
                return self
                
######################################
##           Simple Test            ##
######################################
if __name__ == '__main__':
        
        with Elphel() as cam:
                cam.params['WOI_WIDTH'] = 1280
                cam.params['WOI_HEIGHT'] = 720
                cam.params['COLOR'] = 1
                cam.params['EXPOS'] = 10000
                cam.set_params()

                #cam.init_live()

                cam.display()
