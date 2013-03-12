# Copyright (c) 2013 Riverbed Technology, Inc.
#
# This software is licensed under the terms and conditions of the 
# MIT License set forth at:
#   https://github.com/riverbed/flyscript/blob/master/LICENSE ("License").  
# This software is distributed "AS IS" as set forth in the License.



from __future__ import absolute_import

import datetime
try:
    from rvbd.common.datetime import datetimeng
    datetimeng_available = True
except:
    datetimeng_available = False
    
from rvbd.common import timeutils


class TimeFilter(object):
    def __init__(self, start, end, gmtoffset=0):
        self.start = timeutils.force_to_utc(start)
        self.end = timeutils.force_to_utc(end)

        # XXX this was a legacy from v3 TimeFilters, get rid of it
        assert gmtoffset == 0


    def to_dict(self):
        return {
            'type': 'TIME',
            'value': str(timeutils.datetime_to_nanoseconds(self.start)) + 
            ', ' + str(timeutils.datetime_to_nanoseconds(self.end))
            }
    
class SharkFilter(object):
    def __init__(self, string):
        self.string = string

    def to_dict(self):
        return {
            'type': 'SHARK',
            'value': self.string
            }

class BpfFilter(object):
    def __init__(self, string):
        self.string = string

    def to_dict(self):
        return {
            'type': 'BPF',
            'value': self.string
            }
