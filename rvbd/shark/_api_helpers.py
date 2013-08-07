# Copyright (c) 2013 Riverbed Technology, Inc.
#
# This software is licensed under the terms and conditions of the 
# MIT License set forth at:
#   https://github.com/riverbed/flyscript/blob/master/LICENSE ("License").  
# This software is distributed "AS IS" as set forth in the License.



class SharkAPIVersions(object):
    CURRENT = "5.0"
    LEGACY = ["4.0"]

class APIGroup(object):
    '''Simple wrapper class for a group of related API functions'''
    def __init__(self, uri_prefix, shark):
        self.uri_prefix = uri_prefix
        self.shark = shark

class APITimestampFormat(object):
    '''Encapsulation of the various options supported for absolute
    timestamp encoding.'''
    NANOSECOND             = "ns number"
    NANOSECOND_STR         = "ns string"
    MICROSECOND            = "us number"
    MICROSECOND_STR        = "us string"
    MILLISECOND            = "ms number"
    MILLISECOND_STR        = "ms string"
    SECOND                 = "s number"
    SECOND_STR             = "s string"
    SECOND_NANOSECOND      = "s.ns number"
    SECOND_NANOSECOND_STR  = "s.ns string"
    SECOND_MICROSECOND     = "s.us number"
    SECOND_MICROSECOND_STR = "s.us string"
    SECOND_MILLISECOND     = "s.ms number"
    SECOND_MILLISECOND_STR = "s.ms string"

class API(object):
    version = NotImplementedError()
    common_version = NotImplementedError()
    def __init__(self, shark):
        self.shark = shark
        self.common = Common("/api/common/"+self.common_version, self.shark)
        self.auth = Auth("/api/shark/"+self.version, self.shark)
        self.settings = Settings("/api/shark/"+self.version, self.shark)
        self.interfaces = Interfaces("/api/shark/"+self.version, self.shark)
        self.jobs = Jobs("/api/shark/"+self.version, self.shark)
        self.clips = Clips("/api/shark/"+self.version, self.shark)
        self.fs = Files("/api/shark/"+self.version, self.shark)
        self.licenses = Licenses("/api/shark/"+self.version, self.shark)
        self.certificates = Certificates("/api/shark/"+self.version, self.shark)
        self.system = System("/api/shark/"+self.version, self.shark)
        self.view = Views("/api/shark/"+self.version, self.shark)
        self.stats = Stats("/api/shark/"+self.version, self.shark)
        self.info = Info('/api/shark/'+self.version+'/info', self.shark)
        self.users = Users('/api/shark/'+self.version, self.shark)
        self.groups = Users('/api/shark/'+self.version, self.shark)

        # For the misc handlers just make them methods of the api class itself
        m = Misc('/api/shark/'+self.version, self.shark)
        self.ping = m.ping
