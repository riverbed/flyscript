#!/usr/bin/env python

# Copyright (c) 2013 Riverbed Technology, Inc.
#
# This software is licensed under the terms and conditions of the 
# MIT License set forth at:
#   https://github.com/riverbed/flyscript/blob/master/LICENSE ("License").  
# This software is distributed "AS IS" as set forth in the License.



import rvbd
import rvbd.profiler

from rvbd.common.service import UserAuth
from rvbd.profiler.filters import TimeFilter
from rvbd.profiler.report import TrafficSummaryReport

import pprint

# connection information
username = 'admin'
password = 'admin'
host = 'tm08-1.lab.nbttech.com'

auth = UserAuth(username, password)

p = rvbd.profiler.Profiler(host, auth=auth)
report = TrafficSummaryReport(p)

columns = [p.columns.key.host_ip,
           p.columns.value.avg_bytes,
           p.columns.value.network_rtt]
sort_column = p.columns.value.avg_bytes
timefilter = TimeFilter.parse_range("last 5 m")

report.run('hos', columns, timefilter=timefilter, sort_col=sort_column)
data = report.get_data()
legend = report.get_legend()
report.delete()

pprint.pprint(data[:10])


