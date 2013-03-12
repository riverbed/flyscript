# Copyright (c) 2013 Riverbed Technology, Inc.
#
# This software is licensed under the terms and conditions of the 
# MIT License set forth at:
#   https://github.com/riverbed/flyscript/blob/master/LICENSE ("License").  
# This software is distributed "AS IS" as set forth in the License.


import string
import rvbd.shark

from rvbd.shark._filter import *
import rvbd.common.time
from rvbd.pilot.exceptions import *
from rvbd.shark._source import *
import sys
import time

class ArgParser(object):
    '''This calss offers support for parsing the parameters that Pilot puts on
    the command line when invoking a python script.
    '''
    def __init__(self, param_string):
        '''Parse the command line parameters that Pilot passes to the script
        when invoking it from the user interface.

        ``param_string`` a list of strings containing the arguments received 
        from pilot. The list contains the following entries:        
        - script name 
        - probe address and port (e.g. 192.168.0.1:61898)
        - probe username 
        - probe password 
        - source (file or interface) name
        - source type
        - handle of the view from which the scipt was executed 
        - ID if the output from which the scipt was executed. The output 
          identifies the selected chart  
        - user selection filter        
        '''        
        self._args = param_string
        self._addr, self._port = self._args[1].split(':')
        self._port = int(self._port)
        self._shark = None
        self._username = self._args[2]
        self._pass = self._args[3]
        self._srctype = self._args[5]
        
    def get_shark_addr(self):
        '''returns the address of the Shark where the data selected in Pilot
        comes from.'''
        return self._addr
    
    def get_shark_port(self):
        '''returns the port of the Shark where the data selected in Pilot
        comes from.'''
        return self._port

    def get_username(self):
        '''returns the name of the user that applied the selected view.'''
        return self._username

    def get_pass(self):
        '''returns the password of the user that applied the selected view.'''
        return self._pass

    def connect_to_shark(self):
        '''Connect to the Shark specified in the command line

        Returns the correspondent ``rvbd.shark.Shark`` object.'''
        if self._shark == None:
            self._shark = rvbd.shark.Shark(self.get_shark_addr(), 
                                    port=self.get_shark_port(), 
                                    username=self.get_username(), 
                                    password=self.get_pass(),
                                    force_ssl=True)
        
        return self._shark
    
    def get_source(self):
        '''Get the packet rvbd.shark._source class identifying the packet 
        source for the selected view in Pilot.'''
        if self._shark == None:
            raise PilotException("you need to call connect_to_shark() before get_source()")
                      
        if self._srctype == "pcapfile":
            files = self._shark.get_files()
            
            for file in files:
                if file.path == self._args[4]:
                    return file
    
            raise PilotException("file %s not found on %s" % (self._args[4], self._args[1]))
        elif self._srctype == "adapter" or self._srctype == "tc_adapter" or self._srctype == "airpcap_pilot":
            interfaces = self._shark.get_interfaces()
            
            for interface in interfaces:
                if interface.name == self._args[4]:
                    return interface
    
            raise PilotException("interface %s not found on %s" % (self._args[4], self._args[1]))        
        elif self._srctype == "vtrace":
            clip = TraceClip(self._shark.conn, self._args[4])
            return clip
        elif self._srctype == "savtrace":
            jobs = self._shark.get_capture_jobs()
            
            for job in jobs:
                if job.handle == self._args[4]:
                    return job
                
            raise PilotException("job %s not found on %s" % (self._args[4], self._args[1]))        
        else:
            raise PilotException("source type %s not supported" % self._srctype)          
        
    def get_filters(self):
        '''return the parsed list of filters associated with this selection.'''
        res = []
        
#        res = re.findall(r'\w+|;\w+', self._args[6])
        flts = self._args[8].split(';')
        for flt in flts:
            components = flt.split('|')
            
            if components[0] == "GenericFrameFilter":
                res.append(GenericFrameFilter("RejectInvalidFrames", "true"))
            elif components[0] == "decrypt":
                res.append(DecryptFilter())
            elif components[0] == "TimeFilter":
                start, end = rvbd.common.time.parse_range(components[1])
                res.append(TimeFilter(start, end))
                #res.append(tr.filter_strings())
            elif components[0] == "cube":
                fstr = flt[5:]
                
                res.append(CubeFilter(fstr))
            elif components[0] == "ws":
                res.append(WiresharkDisplayFilter(components[1]))
            else:
                raise PilotException("unrecognized filter type")
            
        return res
