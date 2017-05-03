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

from linux_metrics import cpu_stat, disk_stat, net_stat, mem_stat

from liota.edge_component.file_reader_package import FileReader
from liota.dccs.iotcc import IotControlCenter
from liota.entities.metrics.metric import Metric
import csv
from liota.edge_component.pfa_component import PFAComponent
from liota.entities.devices.simulated_device import SimulatedDevice
from liota.entities.edge_systems.dell5k_edge_system import Dell5KEdgeSystem
from liota.dcc_comms.websocket_dcc_comms import WebSocketDccComms
from liota.dccs.dcc import RegistrationFailure
from liota.lib.utilities.utility import get_default_network_interface, get_disk_name

# getting values from conf file
config = {}
execfile('sampleProp.conf', config)
line = 0
rows = None


# Getting edge_system's network interface and disk name

# There are situations where route may not actually return a default route in the
# main routing table, as the default route might be kept in another table.
# Such cases should be handled manually.
# network_interface = get_default_network_interface()
# If edge_system has multiple disks, only first disk will be returned.
# Such cases should be handled manually.
# disk_name = get_disk_name()



# some standard metrics for Linux systems
# agent classes for different IoT system
# agent classes for different data center components
# agent classes for different kinds of of devices, connected to the IoT System
# we are showing here how to create a representation for a Device in IoTCC but
# using the notion of RAM (because we have no connected devices yet)
# agent classes for different kinds of layer 4/5 connections from agent to DCC
# -------User defined functions for getting the next value for a metric --------
# usage of these shown below in main
# semantics are that on each call the function returns the next available value
# from the device or system associated to the metric.

def read_file(path):
    with open(path, 'r') as my_file:
        reader = csv.reader(my_file)
        global rows
        rows = list(reader)


def action_actuator(value):
    print value


def read_csv_file():
    global line
    line += 1
    if not line > len(rows):
        return int(rows[line][0])


# ---------------------------------------------------------------------------
# In this example, we demonstrate how System health and some simulated data
# can be directed to data center component IoTCC using Liota.
# The program illustrates the ease of use Liota brings to IoT application developers.

if __name__ == '__main__':
    read_file("/Users/vkohli/sample.csv")
    sample = PFAComponent("/Users/vkohli/sample.pfa", action_actuator)
    sample_metric = Metric(
        name="File Metric",
        unit=None,
        interval=10,
        aggregation_size=1,
        sampling_function=read_csv_file
    )
    reg_sample_metric = sample.register(sample_metric)
    reg_sample_metric.start_collecting()
