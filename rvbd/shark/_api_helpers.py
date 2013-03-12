# Copyright (c) 2013 Riverbed Technology, Inc.
#
# This software is licensed under the terms and conditions of the 
# MIT License set forth at:
#   https://github.com/riverbed/flyscript/blob/master/LICENSE ("License").  
# This software is distributed "AS IS" as set forth in the License.



class SharkAPIVersions:

    CURRENT = "4.0"
    LEGACY = ["3.2", "3.1", "3.0"]

class APIGroup:
    '''Simple wrapper class for a group of related API functions'''
    def __init__(self, uri_prefix, shark):
        self.uri_prefix = uri_prefix
        self.shark = shark

class APITimestampFormat:
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

