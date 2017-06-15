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

from liota.core.package_manager import LiotaPackage
import pint

ureg = pint.UnitRegistry()

dependencies = ["graphite_rpi", "examples/dht22_device"]


def get_thermistor_temperature(dht22_device):
    return round(dht22_device.get_temperature(), 2)


def get_humidity(dht22_device):
    return round(dht22_device.get_humidity(), 2)


class PackageClass(LiotaPackage):
    def run(self, registry):
        from liota.entities.metrics.metric import Metric

        # Acquire resources from registry
        graphite = registry.get("graphite")
        dht22_device = registry.get("dht22_device")
        graphite_dht22_device = graphite.register(dht22_device)

        # Create metrics
        self.metrics = []
        metric_temper = "model.dht22_device.temperature"
        thermistor_temper = Metric(
            name=metric_temper,
            unit=ureg.degC,
            interval=5,
            sampling_function=lambda: get_thermistor_temperature(dht22_device)
        )
        reg_thermistor_temper = graphite.register(thermistor_temper)
        graphite.create_relationship(graphite_dht22_device, reg_thermistor_temper)
        reg_thermistor_temper.start_collecting()
        self.metrics.append(reg_thermistor_temper)

        metric_humidity = "model.dht22_device.humidity"
        humidity_device = Metric(
            name=metric_humidity,
            unit=None,
            interval=8,
            sampling_function=lambda: get_humidity(dht22_device)
        )
        reg_humidity_device = graphite.register(humidity_device)
        graphite.create_relationship(graphite_dht22_device, reg_humidity_device)
        reg_humidity_device.start_collecting()
        self.metrics.append(reg_humidity_device)

    def clean_up(self):
        for metric in self.metrics:
            metric.stop_collecting()
