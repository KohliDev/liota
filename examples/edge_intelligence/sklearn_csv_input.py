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

import csv

from liota.entities.metrics.metric import Metric
from liota.edge_component.sklearn_edge_component import SKLearnEdgeComponent

line = 0
rows = None


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
    read_file("/home/vl/Desktop/sample.csv")
    sample = SKLearnEdgeComponent("/home/vl/Desktop/finalized_model.sav", action_actuator)
    sample_metric = Metric(
        name="File Metric",
        unit=None,
        interval=1,
        aggregation_size=1,
        sampling_function=read_csv_file
    )
    reg_sample_metric = sample.register(sample_metric)
    reg_sample_metric.start_collecting()
