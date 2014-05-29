#!/usr/bin/python

# Copyright (c) 2014 Roger Light <roger@atchoo.org>
#
# All rights reserved. This program and the accompanying materials
# are made available under the terms of the Eclipse Distribution License v1.0
# which accompanies this distribution. 
#
# The Eclipse Distribution License is available at 
#   http://www.eclipse.org/org/documents/edl-v10.php.
#
# Contributors:
#    Roger Light - initial implementation

# This shows an example of using the publish.multiple helper function.

import sys
try:
    import paho.mqtt.publish as publish
except ImportError:
    # This part is only required to run the example from within the examples
    # directory when the module itself is not installed.
    #
    # If you have the module installed, just use "import paho.mqtt.publish"
    import os
    import inspect
    cmd_subfolder = os.path.realpath(os.path.abspath(os.path.join(os.path.split(inspect.getfile( inspect.currentframe() ))[0],"../src")))
    if cmd_subfolder not in sys.path:
        sys.path.insert(0, cmd_subfolder)
    import paho.mqtt.publish as publish
    import paho.mqtt.client

msgs = [{'topic':"paho/test/1", 'payload':"1", 'retain':True, 'qos':2},
        {'topic':"paho/test/2", 'payload':"2", 'retain':True, 'qos':2},
        {'topic':"paho/test/3", 'payload':"3", 'retain':True, 'qos':2},
        {'topic':"paho/test/4", 'payload':"4", 'retain':True, 'qos':2},
        {'topic':"paho/test/5", 'payload':"5", 'retain':True, 'qos':2},
        {'topic':"paho/test/6", 'payload':"6", 'retain':True, 'qos':2},
        {'topic':"paho/test/7", 'payload':"7", 'retain':True, 'qos':2},
        {'topic':"paho/test/8", 'payload':"8", 'retain':True, 'qos':2},
        {'topic':"paho/test/9", 'payload':"9", 'retain':True, 'qos':2},
        {'topic':"paho/test/10", 'payload':"10", 'retain':True, 'qos':2},
        ]

publish.multiple(msgs, hostname="localhost", protocol=paho.mqtt.client.MQTTv31)
