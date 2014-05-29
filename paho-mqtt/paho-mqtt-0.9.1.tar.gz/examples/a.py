#!/usr/bin/env python
 
import sys
try:
    import paho.mqtt.client as mqtt
except ImportError:
    # This part is only required to run the example from within the examples
    # directory when the module itself is not installed.
    #
    # If you have the module installed, just use "import paho.mqtt.client"
    import os
    import inspect
    cmd_subfolder = os.path.realpath(os.path.abspath(os.path.join(os.path.split(inspect.getfile( inspect.currentframe() ))[0],"../src")))
    if cmd_subfolder not in sys.path:
        sys.path.insert(0, cmd_subfolder)
    import paho.mqtt.client as mqtt
import socket, sys, time
 
def on_connect(client, userdata, rc):
    client.subscribe("$SYS/#", 0)
 
def on_subscribe(client, userdata, mid, granted_qos):
    print("success: {}".format(server))
    client.disconnect()
 
if len(sys.argv) < 2:
    sys.stderr.write("Usage: {} <MQTT server> [<username> <password>]\n".format(sys.argv[0]))
    sys.exit(-1)
 
mqttc = mqtt.Client()
mqttc.on_connect = on_connect
mqttc.on_subscribe = on_subscribe
 
server = sys.argv[1]
 
if len(sys.argv) == 4:
    mqttc.username_pw_set(sys.argv[2], sys.argv[3])
 
try:
    mqttc.connect(server, 1883, 60)
except:
    sys.stderr.write("Connection error: {}\n".format(server))
    sys.exit(-1)
 
mqttc.loop_forever()
