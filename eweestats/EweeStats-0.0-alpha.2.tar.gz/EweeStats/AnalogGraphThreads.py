# -*- coding: utf-8 -*-
#
#  AnlogGraphThreads.py
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

import threading
import Queue
import time
import os
import sys
from pyfirmata import Arduino, util
from Adafruit_CharLCDPlate import Adafruit_CharLCDPlate
import graph
import pinselection
import ods
import convert_data


class AnalogGraphThreads(object):
    """
        Classe destinée aux threads de lecture des valeurs analogiques
        et de création du graph
    """

    def __init__(
        self, analogSensors, file_list, time_file, graph_name,
        datapath):
        """
        Constructeur de la classe : va créer transmit_is_ready
        pour contrôler l'état des threads et créer une queue d'un
        élément
        :param analogSensors: nombre de capteurs analogiques
        :type analogSensors: integer
        """

        self.transmit_is_ready = True
        self.my_queue = Queue.Queue(maxsize=1)
        self.stop = False
        self.analogSensors = analogSensors
        
        self.listValueLists = [[] for i in range(analogSensors)]
        self.timelist = []
        self.file_list = file_list
        self.time_file = time_file
        self.graph_name = graph_name
        self.datapath = datapath

    def threadAnalogData(self):
        """
            Ce thread relève les valeurs analogiques, les stocke dans
            des fichiers et attent que le thread 2 soit prêt pour
            commencer le graph
        """
        # Init lcd display
        lcd = Adafruit_CharLCDPlate()
        lcd.clear()

        # Boolean indicating init state, for timestamp and pinselection
        initDone = False
        # List of values
        value_list = [0.0 for i in range(self.analogSensors)]

        # Init Arduino and iterator
        lcd.message("Connection de \nl'Arduino ...")
        board = Arduino('/dev/ttyACM0')
        lcd.clear()
        print('Arduino connected')
        lcd.message("Arduino connecte !")
        # Création itérateur
        iter8 = util.Iterator(board)
        iter8.start()

        
        # Start listening ports
        for i in range(self.analogSensors):
            board.analog[i].enable_reporting()


        # Wait for a valid value to avoid None
        start = time.time()
        while board.analog[0].read() is None:
                print("nothing after {t}".format(
                    t = time.time() - start))

        print("first val after {t}".format(t = time.time() - start))
        lcd.clear()
        lcd.message("Debut des \nmesures")

        # init some more variables
        displayPin = 0
        timeDisplay = 0

    
        # Main loop
        while not lcd.buttonPressed(lcd.SELECT):
            
            # Calcule last display time
            timeLastDisplay = time.time() - timeDisplay
            
            # Buttons activity
            if timeLastDisplay >= 0.25:
                displayPin = pinselection.display_selection(
                    self.analogSensors, lcd, displayPin)


            if not initDone:
                timestampInit = time.time()
                initDone = True


            # Timestamping
            timestamp = time.time()
            timestamp = timestamp - timestampInit
            self.timelist.append(str(round(timestamp, 4))) # for pygal

            # Data reading
            for i in range(self.analogSensors):
                value_list[i] = board.analog[i].read()

            # Data converting
            value_list = convert_data.convert(value_list)
            
            # Data stocking
            for i in range(self.analogSensors):
                self.listValueLists[i].append(round(value_list[i], 4))

            #print(value_list)    # affiche dans la console les valeurs

            # Thread managing
            if self.transmit_is_ready == True:
                self.my_queue.put(1)  # if ready, 1 in the queue

            #LCD displaying every 250ms
            if timeLastDisplay >= 0.25:
                lcd.clear()
                lcd.message("Pot {dp} :\n".format(dp = str(displayPin)))
                lcd.message(value_list[displayPin])
                timeDisplay = time.time() # for lagging

        # Poweroff
        self.stop = True
        board.exit()
        lcd.clear()
        lcd.message('Ecriture des \nfichiers texte')
        # writing text data files
        for i, file in enumerate(self.file_list):
            for j in self.listValueLists[i]:
                file.write(str(j))
                file.write('\n')
        # writing timestamp file
        for i in self.timelist:
            self.time_file.write(i)
            self.time_file.write('\n')

        for i in self.file_list:
            i.close()
        self.time_file.close()
        lcd.clear()
        lcd.message("Ecriture du\nfichier ODS")
        ods.write_ods(
            self.datapath, self.analogSensors,
            self.listValueLists, self.timelist)
        lcd.clear()


    def threadGraph(self):
        """
            Thread construisant le graph :
            lit les valeurs, les formate comme il faut, configure puis
            crée le graph
        """

        while(not self.stop):    
            
            # waits until queue is full
            self.my_queue.get(True)
            self.transmit_is_ready = False
            
            # Graph creation
            graph.create_graph(
                self.analogSensors, self.listValueLists,
                self.timelist, self.datapath, self.graph_name)

            # Task finished, now ready
            self.transmit_is_ready = True



    def startThreads(self):
        """
            Sert à lancer les threads : les crée puis les lance
        """
        # Threads creation
        self.at = threading.Thread(None, self.threadAnalogData, None)
        self.gt = threading.Thread(None, self.threadGraph, None)

        # Threads start
        self.at.start()
        self.gt.start()

