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

import Adafruit_DHT
import logging

from liota.entities.devices.device import Device
from liota.lib.utilities.utility import systemUUID

log = logging.getLogger(__name__)

class DH22Device(Device):

    def __init__(self, name, pin_no, sensor_param, entity_type="DH22"):

        super(DH22Device, self).__init__(
            name=name,
            entity_type=entity_type,
            entity_id=systemUUID().get_uuid(name)
        )

        self.sensor_param = sensor_param
        self.pin_no = pin_no

        sensor_args = {'11': Adafruit_DHT.DHT11,
                       '22': Adafruit_DHT.DHT22,
                       '2302': Adafruit_DHT.AM2302}
        if self.sensor_param in sensor_args:
            self.sensor = sensor_args[self.sensor_param]
            self.pin = self.pin_no
        else:
            log.info("Please specify the correct Pin Number and Sensor Args")

    def get_temperature(self):
        return Adafruit_DHT.read_retry(self.sensor, self.pin)[1]

    def get_humidity(self):
        return Adafruit_DHT.read_retry(self.sensor, self.pin)[0]


