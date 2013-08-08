# Copyright (c) 2013 Riverbed Technology, Inc.
#
# This software is licensed under the terms and conditions of the 
# MIT License set forth at:
#   https://github.com/riverbed/flyscript/blob/master/LICENSE ("License").  
# This software is distributed "AS IS" as set forth in the License.


"""
This module contains the Profiler class, which is the main interface to
a Cascade Profiler Appliance. It allows, among other things, retrieving
the state of the Profiler, modifying its settings and performing operations
like creating running reports.
"""

import types
from rvbd.common.utils import DictObject, ColumnProxy
from rvbd.common.api_helpers import APIVersion
import rvbd.common.service
import json

API_VERSIONS = ["1.0"]

# Notes:
#   common api not supported


class StingrayTrafficManager(rvbd.common.service.Service):
    """The StingrayTrafficManager class is the main interface to interact with a Stingray
    Traffic Manager Appliance.  Primarily this provides an interface to configuration."""
    
    def __init__(self, host, port=None, auth=None, force_ssl=None):
        """Establishes a connection to a Stingray Traffic Manager appliance.

        `host` is the name or IP address of the TM to connect to

        `port` is the TCP port on which the TM appliance listens.
                 if this parameter is not specified, the function will
                 try to automatically determine the port.

        `auth` defines the authentication method and credentials to use
                 to access the TM.  It should be an instance of
                 rvbd.common.UserAuth or rvbd.common.OAuth.

        `force_version` is the API version to use when communicating.
                 if unspecified, this will use the latest version supported
                 by both this implementation and the TM appliance.

        `force_ssl` when set to True will only allow SSL based connections.
            If False, only allow non-SSL connections.  If set to None (the default)
            try SSL first, then try non-SSL.
        
        See the base [Service](common.html#service) class for more information
        about additional functionality supported.
        """
        if port is None:
            port = [9070]

        super(StingrayTrafficManager, self).__init__("tm", host, port,
                                                     auth=auth, force_ssl=force_ssl,
                                                     versions=[APIVersion("1.0")])
            
    def create_trafficscript_rule(self, vserver, trafficscript):
        rule = 'ARX_' + vserver

        extra_headers = {'Content-Type': 'application/octet-stream'}
        self.conn.upload("/api/tm/1.0/config/active/rules/%s" % rule,
                         data=trafficscript,
                         method="PUT",
                         extra_headers=extra_headers)

        need_to_add = True
        jp = self.conn.json_request("/api/tm/1.0/config/active/vservers/%s" % vserver)
        for r in jp['properties']['basic']['response_rules']:
            if r == rule:
                need_to_add = False
                break
            elif r == '/' + rule:
                need_to_add = False
                loc = jp['properties']['basic']['response_rules'].index(r)
                jp['properties']['basic']['response_rules'][loc] = rule
                break

        if need_to_add:
            jp['properties']['basic']['response_rules'].append(rule)

        self.conn.json_request("/api/tm/1.0/config/active/vservers/%s" % vserver,
                               method="PUT",
                               data=jp)
    
    def change_rule(self, vserver, rule, enable=True, request=True, response=True):
        jp = self.conn.json_request("/api/tm/1.0/config/active/vservers/%s" % vserver)
        #print json.dumps(jp, indent=2)

        def process(jp, rule, t):
            change2 = False
            newrules = []
            for r in jp['properties']['basic'][t+'_rules']:
                if enable:
                    if r == '/' + rule:
                        newrules.append(rule)
                        change2 = True
                    else:
                        newrules.append(r)
                else:
                    if r ==  rule:
                        newrules.append('/' + rule)
                        change2 = True
                    else:
                        newrules.append(r)
                    
            if change2:
                jp['properties']['basic'][t+'_rules'] = newrules
                return True
            return False
        
        change = False
        if request: change = process(jp, rule, 'request')
        if response: change = process(jp, rule, 'response') or change

        #print json.dumps(jp, indent=2)
        self.conn.json_request("/api/tm/1.0/config/active/vservers/%s" % vserver, method="PUT", data=jp)

        
            
