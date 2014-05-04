# -*- coding: utf-8 -*-
#
#  pinselection.py
#  
#  Copyright 2014 Gabriel Hondet <gabrielhondet@gmail.com>
#
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.

#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.

#  You should have received a copy of the GNU General Public License
#  along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
#


from Adafruit_CharLCDPlate import Adafruit_CharLCDPlate
import os
import sys
import time

def display_selection(analogSensors, lcd, selectedPin):
    """
    :param analogSensors: nombre de capteurs
    :type analogSensors: integer
    
    :param lcd: classe lcd
    :type lcd: Adafuit_CharLCDPlate()
    
    :param selectedPin: sélection à la boucle d'avant
    :type selectedPin: integer
    
    :returns: numéro de l'entrée analogique à afficher
    :rtype: integer
    """
    
    
    # Read buttons activity
    if lcd.buttonPressed(lcd.UP):
        print('--UP PRESSED--')
        selectedPin += 1
    elif lcd.buttonPressed(lcd.DOWN):
        print('--DOWN PRESSED--')
        selectedPin -= 1
    
    # If we go inferior than 0, go back to max, and the opposite
    if selectedPin >= analogSensors:
        selectedPin = 0
    elif selectedPin < 0:
        selectedPin = analogSensors - 1  # -1 because pins start to 0
        
    return selectedPin
