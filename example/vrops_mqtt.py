# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------------#
#  Copyright © 2015-2016 VMware, Inc. All Rights Reserved.                    #
#                                                                             #
#  Licensed under the BSD 2-Clause License (the “License”); you may not use   #
#  this file except in compliance with the License.                           #
#                                                                             #
#  The BSD 2-Clause License                                                   #
#                                                                             #
#  Redistribution and use in source and binary forms, with or without         #
#  modification, are permitted provided that the following conditions are met:#
#                                                                             #
#  - Redistributions of source code must retain the above copyright notice,   #
#      this list of conditions and the following disclaimer.                  #
#                                                                             #
#  - Redistributions in binary form must reproduce the above copyright        #
#      notice, this list of conditions and the following disclaimer in the    #
#      documentation and/or other materials provided with the distribution.   #
#                                                                             #
#  THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"#
#  AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE  #
#  IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE #
#  ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE  #
#  LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR        #
#  CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF       #
#  SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS   #
#  INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN    #
#  CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)    #
#  ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF     #
#  THE POSSIBILITY OF SUCH DAMAGE.                                            #
# ----------------------------------------------------------------------------#

from liota.transports.mqtt import Mqtt
from liota.boards.gateway_dk300 import Dk300
from liota.dcc.vrops import Vrops
from liota.transports.web_socket import WebSocket
from liota.things.device import Device
import Queue

# getting values from conf file
config = {}
execfile('sampleProp.conf', config)
# queue defined to store the values
# from the subscribed MQTT Channel
glass_panel_queue = Queue.Queue()
solar_lights_queue = Queue.Queue()

# Add message callbacks that will trigger on a specific subscription match.
# Values collected from the callback function are stored in the respective queue
# Callback function for glass panel
def callback_glass_panel(client, userdata, message):
    glass_panel_queue.put(float(message.payload))

# Callback function for solar lights
def callback_solar_lights(client, userdata, message):
    solar_lights_queue.put(float(message.payload))

#---------------------------------------------------------------------------
# In this example, we demonstrate how an event stream of data from MQTT channel
# can be directed to vrops data center component using Liota by setting
# sampling_interval_sec parameter to zero. Additionally, we are showcasing that
#  with help of lambda function how we can pass parameters to commmon user defined method
# Common User Defined Method (UDM) returning the value from respective queue
def get_value(queue):
    return queue.get(block=True)

if __name__ == '__main__':
    # create a mqtt_conn object by passing the port number and the server address
    # we will be enhancing this in future to support username/password as well as QoS option
    # currently we support QoS=1
    mqtt_conn = Mqtt(config['MqttServer'], config['MqttPort'])
    # subscribe to the base mqtt channel example "SmartBuilding/#"
    mqtt_conn.subscribe(config['MqttChannel'])
    # add a message callback to the client of mqtt_conn object
    # glass panel call back method added to the mqtt client to listen
    # on specific sub-channel example "SmartBuilding/GlassPanel"
    mqtt_conn.client.message_callback_add(config['MqttSubChannel1'], callback_glass_panel)
    # solar lights call back method added to the mqtt client
    # to listen on specific sub-channel example "SmartBuilding/SolarLights"
    mqtt_conn.client.message_callback_add(config['MqttSubChannel2'], callback_solar_lights)
    # create a data center object, vROps in this case, using websocket as a transport layer
    # this object encapsulates the formats and protocols neccessary for the agent to interact with the dcc
    # UID/PASS login for now.
    vrops = Vrops(config['vROpsUID'], config['vROpsPass'], WebSocket(url=config['WebSocketUrl']))
    # create a gateway object encapsulating the particulars of a gateway/board
    # argument is the name of this gateway
    gateway = Dk300(config['Gateway1Name'])
    # resister the gateway with the vrops instance
    # this call creates a representation (a Resource) in vrops for this gateway with the name given
    vrops_gateway = vrops.register(gateway)

    # Here we are showing how to create a device object Glass Panel & Solar device as well registering it in vrops
    # Since there are no attached devices we are simulating by posting dummy messages on the required MQTT channel
    # as separate from the gateway. The agent makes possible many different data models
    # arguments:
    #        device name
    #        Read or Write
    #        another Resource in vrops of which the should be the child of a parent-child relationship among Resources
    # Glass panel device registered
    glass_panel_device = Device(config['Device1Name'], 'Read', gateway)
    vrops_glass_device = vrops.register(glass_panel_device)
    if vrops_glass_device.registered:
        # over here we have shown the usage of lamda function in python
        # using it parameters can be passed to the UDM function and even
        # the same UDM can be used in a generic way to accept values from multiple metrics
        # glass_panel queue passed as parameter to UDM get_value()
        glass_metric = vrops.create_metric(vrops_glass_device, "Glass Panel", unit=None, sampling_interval_sec=0,
                                            aggregation_size=1, sampling_function=lambda :get_value(glass_panel_queue))
        glass_metric.start_collecting()
    else:
        print "vROPS resource not registered successfully"

    # Solar light device registered
    solar_lights_device = Device(config['Device2Name'], 'Read', gateway)
    vrops_solar_device = vrops.register(solar_lights_device)
    if vrops_solar_device.registered:
        # solar_lights queue passed as parameter to UDM get_value()
        solar_metric = vrops.create_metric(vrops_solar_device, "Solar Lights", unit=None, sampling_interval_sec=0,
                                            aggregation_size=1, sampling_function=lambda :get_value(solar_lights_queue))
        solar_metric.start_collecting()
    else:
        print "vROPS resource not registered successfully"
