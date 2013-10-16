# Copyright (c) 2013 Riverbed Technology, Inc.
#
# This software is licensed under the terms and conditions of the 
# MIT License set forth at:
#   https://github.com/riverbed/flyscript/blob/master/LICENSE ("License").  
# This software is distributed "AS IS" as set forth in the License.

from _api_helpers import APIGroup, APITimestampFormat
from _api4 import API4_0
import urllib

class API5Group(APIGroup):
    base_headers = {}

    def request(self, urlpath, method, data=None, timestamp_format=APITimestampFormat.NANOSECOND, params=None, custom_headers=None):
        """Issue the given API request using either JSON or XML
        (dictated by the as_json parameter)."""
        self.add_base_header('X-RBT-High-Precision-Timestamp-Format', timestamp_format)
        
        # XXXWP Changing the method so that the caller can specify some extra headers
        headers =  dict(self.base_headers)
        if isinstance(custom_headers, dict):
            headers.update(custom_headers)

        # we are dealing with a url so let's sanitize it.
        # this may break code but at least prevents flyscript to send insane urls to the server
        # define insane: url that contains spaces
        urlpath = urllib.quote(urlpath)

        return self.shark.conn.json_request(self.uri_prefix + urlpath, method=method,
                                                  data=data, params=params, extra_headers=headers)
        
    def add_base_header(self, key, value=""):
        if isinstance(key, basestring):
            self.base_headers[key] = value

    def remove_base_header(self, key):
        if isinstance(key, basestring):
            self.base_headers.pop(key, None)


class PortDefinitions(API5Group):
    def get(self):
        """Get the configuration from the server"""
        return self.request('/port_names', 'GET')

    def update(self, data):
        """Updates the configuration to the server"""
        return self.request('/port_names', 'PUT', data)


class PortGroups(API5Group):
    def get(self):
        """Get the configuration from the server"""
        return self.request('/port_groups', 'GET')

    def update(self, data):
        """Updates the configuration to the server"""
        return self.request('/port_groups', 'PUT', data)

class L4Mappings(API5Group):
    def get(self):
        """Get the configuration from the server"""
        return self.request('/layer4_mappings', 'GET')

    def update(self, data):
        """Updates the configuration to the server"""
        return self.request('/layer4_mappings', 'PUT', data)

class CustomApplications(API5Group):
    def get(self):
        """Get the configuration from the server"""
        return self.request('/custom_applications', 'GET')

    def update(self, data):
        """Updates the configuration to the server"""
        return self.request('/custom_applications', 'PUT', data)

class SrtPorts(API5Group):
    def get(self):
        """Get the configuration from the server"""
        return self.request('/srt_ports', 'GET')

    def update(self, data):
        """Updates the configuration to the server"""
        return self.request('/srt_ports', 'PUT', data)

class Snmp(API5Group):
    def get(self):
        """Get the configuration for the Snmp from the server"""
        return self.request('/snmp', 'GET')

    def update(self, data):
        """Updates the configuration to the server"""
        return self.request('/snmp', 'PUT', data)

class Alerts(API5Group):
    def get(self):
        """Gets the configuration for the alerts from the server"""
        return self.request('/notification', 'GET')

    def update(self, data):
        """Updates the configuration to the server"""
        return self.request('/notification', 'PUT', data)

    def send_test_snmp(self, data):
        """Tries the SNMP configuration"""
        return self.request('/notification/send_test_trap.json', 'POST', data)

    def send_test_smtp(self, data):
        """Tries the SMTP configuration"""
        return self.request('/notification/send_test_mail.json', 'POST', data)


class API5_0(API4_0):
    version = '5.0'
    common_version = '1.0'

    def __init__(self, shark):
        super(API5_0, self).__init__(shark)
        self.port_definitions = PortDefinitions('/api/shark/'+self.version+'/definitions', shark)
        self.port_groups = PortGroups('/api/shark/'+self.version+'/definitions', shark)
        self.l4_mappings = L4Mappings('/api/shark/'+self.version+'/definitions', shark)
        self.custom_applications = CustomApplications('/api/shark/'+self.version+'/definitions', shark)
        self.srt_ports = SrtPorts('/api/shark/'+self.version+'/definitions', shark)
        self.snmp = Snmp('/api/shark/'+self.version+'/settings', shark)
        self.alerts = Alerts('/api/shark/'+self.version+'/settings', shark)

__all__ = ['API5_0']
