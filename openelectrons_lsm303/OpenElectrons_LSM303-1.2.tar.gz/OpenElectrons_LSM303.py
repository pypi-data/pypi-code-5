#!/usr/bin/env python
#
# Copyright (c) 2014 OpenElectrons.com
# 
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 675 Mass Ave, Cambridge, MA 02139, USA.
#
# Some of this code is derived from Adafruit_LMS303.py
#
# History:
# Date            Author            Comments
# 05/19/14        Michael Giles     Initial authoring.
# 05/23/14        Michael Giles     Error handling and documenting

## @package OpenElectrons_LSM303
# This is the OpenElectrons_i2c module for LSM303.

from OpenElectrons_i2c import OpenElectrons_i2c

## ACCEL: this class provides functions for accelerometer of the LSM303 IC
#  for read and write operations.
class ACCEL(OpenElectrons_i2c):

    #accelerometer addresses
    ACCEL_ADDRESS = (0x32)   
                                             
    #register constants
    ACCEL_REG1 = 0x20 
    ACCEL_REG4 = 0x23
    ACCEL_X_Y_Z = 0x28
    

    ## Initialize the class with the i2c address of the Accelerometer
    #  @param self The object pointer.
    #  @param i2c_address Address of your accelerometer.
    def __init__(self, accel_address = ACCEL_ADDRESS ):
        OpenElectrons_i2c.__init__(self, accel_address >> 1)
        # Enable the accelerometer
        self.writeByte(self.ACCEL_REG1, 0x27)
        # default low resolution
        self.writeByte(self.ACCEL_REG4, 0)
  
    ## Interprets signed 12 bit accelerometer data from a list
    #  @param self The object pointer.
    #  @param array The list of accelerometer data generated from the LSM303
    #  @param idx The location of the desired element in the list
    def accl(self, array, idx):
        try:
            n = array[idx] | (array[idx+1] << 8) # Low, high bytes
            if n > 32767: n -= 65536           # 2's complement signed
            return n >> 4                      # 12-bit resolution
        except: 
            print "Error: Could not read accelerometer value" 
            return ""            

    ## Reads the accelerometer
    #  @param self The object pointer.
    def read(self):
        try:
            array = self.readArray(self.ACCEL_X_Y_Z | 0x80, 6)
            res = [(self.accl(array, 0),
                    self.accl(array, 2),
                    self.accl(array, 4))]
            return res
        except:
            print "Error: Could not read accelerometer values"
            return ""

## MAG: this class provides functions for magnetometer of the LSM303 IC
#  for read and write operations.
class MAG(OpenElectrons_i2c):
    
    #magnetometer constants
    MAG_ADDRESS = (0x3C) 
    
    #register addresses
    MAG_REG1 = 0x01
    MAG_REG4 = 0x02
    MAG_X_Y_Z = 0x03
    
    #magnetometer gain constants
    MAG_G13 = 0x20 # +/- 1.3
    MAG_G19 = 0x40 # +/- 1.9
    MAG_G25 = 0x60 # +/- 2.5
    MAG_G40 = 0x80 # +/- 4.0
    MAG_G47 = 0xA0 # +/- 4.7
    MAG_G56 = 0xC0 # +/- 5.6
    MAG_G81 = 0xE0 # +/- 8.1
    
    ## Initialize the class with the i2c address of the Magnetometer
    #  @param self The object pointer.
    #  @param i2c_address Address of your magnetometer.
    def __init__(self, mag_address = MAG_ADDRESS ):
        OpenElectrons_i2c.__init__(self, mag_address >> 1)        
        # Enable the magnetometer
        self.writeByte(self.MAG_REG4, 0x00)
        
    ## Interprets signed 16 bit magnetometer data from a list
    #  @param self The object pointer.
    #  @param array The list of magnetometer data generated from the LSM303
    #  @param idx The location of the desired element in the list
    def magnet(self, array, idx):
        try:
            n = (array[idx] << 8) | array[idx+1]   # High, low bytes
            return n if n < 32768 else n - 65536 # 2's complement signed
            return n >> 4                      # 12-bit resolution
        except:
            print "Error: Could not read magnetometer value"
            return ""
        
    ## Reads the magnetometer
    #  @param self The object pointer.
    def read(self):        
        try:
            array = self.readArray(self.MAG_X_Y_Z, 6)
            res = [(self.magnet(array, 0),
                    self.magnet(array, 2),
                    self.magnet(array, 4))]
            return res
        except:
            print "Error: Could not read magnetometer values"
            return ""
    
    ## Writes a desired gain value for the magnetometer
    #  @param gain Gain value to write to the magnetometer
    def setMagnetGain(gain=MAG_G13):
            self.writeByte(MAG_REG1, gain)


# Simple example prints accel/mag data once per second:
if __name__ == '__main__':

    import time
    
    acl = ACCEL()
    mag = MAG()

    print '[(Accelerometer X, Y, Z), (Magnetometer X, Y, Z, orientation)]'
    while True:
        print acl.read() + mag.read()
        time.sleep(1) 