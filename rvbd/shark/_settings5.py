# Copyright (c) 2013 Riverbed Technology, Inc.
#
# This software is licensed under the terms and conditions of the 
# MIT License set forth at:
#   https://github.com/riverbed/flyscript/blob/master/LICENSE ("License").  
# This software is distributed "AS IS" as set forth in the License.

import json
from _settings4 import Settings4, getted
from rvbd.common.jsondict import JsonDict

#there is no functional need to put this class nested into Settings5 class
#leaving it as module object to simplify reuse and modularizzation
class SettingsLookup(object):
    """This mixin makes object able to lookup on its inner _settings
    structure. this enables easier lookup of settings using the dot notation.

    Note that this object defines __getattr__ and not __getattribute__ it means that
    if the object has any property/method it will be called first and this
    lookup method will never be executed
    """
    def __getattr__(self, name):
        if name in self._settings:
            return getattr(self._settings, name)
        else:
            raise AttributeError

    def __dir__(self):
        """Retrieve posible attributes from object and _settings keys (since it's a
        JsonDict object)
        """
        return sorted(set(dir(type(self))+dir(self._settings)))

class BasicSettingsFunctionality(object):
    """This basic mixin assumes the api.get() and api.update() available
    for the given resource.

    This is mainly used to give any setting object the get and save functionality and
    reuse code
    """
    def __init__(self, api):
        self._settings = None
        self.api = api

    def get(self, force=False):
        """Get configuration from the server
        """
        if self._settings is None and force is False:
            self._settings = JsonDict(self.api.get())
        return self._settings

    @getted
    def save(self):
        """Save configuration to the server
        """
        self.api.update(self._settings)
        self.get(force=True)

    @getted
    def cancel(self):
        """Cancel pending changes to the configuration
        and reloads the configuration from server
        """
        return self.get(force=True)

    def download(self, path):
        """Download configuration to path
        path must be a complete, including a filename
        """
        data = self.get()
        with open(path, 'w') as f:
            f.write(json.dumps(data))

    def load(self, path, save=True):
        """Load the configuration from a path

        `path` is the file path

        `save` is a flag to automatically save to the server after load,
        default to True
        """
        with open(path, 'r') as f:
            self._settings = json.loads(f.read())

        if save is True:
            self.save()


class DPIResource(BasicSettingsFunctionality):
    def _get_by_name(self, name):
        for obj in self._settings:
            if obj.get('name') == name:
                return obj
        return None

    def _get_by_priority(self, priority):
        obj = self._settings[priority]
        if obj.get('priority') != priority:
            return None
        else:
            return obj
  
    def _port_string_to_port_list(self, port_string, protocol='TCP'):
        if port_string is not None:
            ports = [{'port_range':range.strip(), 'protocol':protocol} for range in port_string.split(',')]
        else:
            ports = []
        return ports

    def _refresh_priorities(self):
        for i, obj in enumerate(self._settings):
                obj['priority'] = i


class PortDefinitions(DPIResource):
    def __init__(self, api, srt_ports_api):
        super(PortDefinitions, self).__init__(api)
        self.srt_ports_api = srt_ports_api
        self._srt_settings = None

    def get(self, force=False):
        if self._srt_settings is None or force:
            self._srt_settings = self.srt_ports_api.get()
        return super(PortDefinitions, self).get(force)

    @getted
    def save(self):
        super(PortDefinitions, self).save()
        self.srt_ports_api.update(self._srt_settings)
        

    def _lookup_port(self, port):
        for port_obj in self._settings:
            if port_obj['port'] == port:
                return port_obj
        return None

    @getted
    def add(self, name, port, protocol, srt):
        """Add a port definition

        `name` is a name for the port

        `port` is the port number

        `protocol` is the protocol the name is associated to can be 'tcp' or 'udp'

        `srt` is a boolean that indicates either True or False to the port
        to be enabled as srt port
        """
        assert port > 0 and port < 65536
        assert srt == True or srt == False
        if protocol is not 'tcp' and protocol is not 'udp':
            raise ValueError('Procotol must be tcp or udp')

        port_obj = self._lookup_port(port)

        if port_obj is not None:
            if port_obj.get(protocol) is not None:
                raise ValueError('There is already a setting for port number {0}'.format(port))
            else:
                port_obj[protocol] = name
        else:
            self._settings.append({protocol:name, 'port':port})

        if srt and protocol == 'tcp':
            if port not in self._srt_settings:
                self._srt_settings.append(port)


    @getted
    def remove(self, name, port):
        """Remove port identified by name and port number from the Port Definitions

        `name` is the name of the port

        `port` is the port number
        """
        assert port > 0 and port < 65536

        port_obj = self._lookup_port(port)

        if port_obj is None:
            raise ValueError('Port number {0} has no configuration in the current shark'.format(port))

        if port_obj.get('tcp') == name:
            del port_obj['tcp']
            if port in self._srt_settings:
                self._srt_settings.remove(port)

        if port_obj.get('udp') == name:
            del port_obj['udp']

        if port_obj.get('tcp') is None and port_obj.get('udp') is None:
            self._settings.remove(port_obj)


class GroupDefinitions(DPIResource):
    @getted
    def add(self, name, tcp_ports=None, udp_ports=None, priority=None):
        #sort the list first by priority
        self._settings.sort(key=lambda k:k['priority'])
        
        obj = self._get_by_name(name)
        
        if obj is not None:
            raise ValueError('A port group with the same name already exists')

        priority = priority or len(self._settings)

        tcp = self._port_string_to_port_list(tcp_ports, 'TCP')

        udp = self._port_string_to_port_list(udp_ports, 'UDP')
    
        self._settings.insert(priority, {'name': name,
                                         'priority': priority,
                                         'ports': tcp+udp
                                         })

        self._refresh_priorities()

        
    @getted
    def remove(self, name=None, priority=None):
        """Remove a port group by name or by priority

        It accepts one of name or priority. If name and priority are issued
        it will remove the rule named `name` only if it maches `priority`

        `name` is the name of the port group

        `priority` is the priority of the port group
        """
        if name is None and priority is None:
            raise ValueError('name and priority cannot be both None')

        if name is not None:
            obj = self._get_by_name(name)

        if priority is not None:
            obj = self._get_by_priority(priority)

        if name is not None and priority is not None:
            if obj.get('name') != name:
                raise ValueError('Port group with priority {0} has a different name than {1}'.format(priority, name))

        if obj is not None:
            self._settings.remove(obj)
        else:
            if name is not None and priority is None:
                raise ValueError('Impossible to find port group with name {0}'.format(name))
            if name is  None and priority is not None:
                raise ValueError('Impossible to find port group with priority {0}'.format(priority))
            if name is not None and priority is not None:
                raise ValueError('Impossible to find port group with name {0} and priority {1}'.format(name, priority))

class L4Mapping(GroupDefinitions):
    @getted
    def add(self, name, hosts, tcp_ports=None, udp_ports=None, priority=None):
        """Add a l4 mapping rule

        `name` is the name of the rule

        `hosts` is a comma separated list of hosts with optional subnet mask

        `tcp_ports` is a comma separated list of ports or port range

        `udp_ports` is a comma separated list of ports or port range
        """
        assert tcp_ports is not None and udp_ports is not None

        priority = priority or len(self._settings)

        obj = self._get_by_name(name)

        if obj is not None:
            raise ValueError('a l4 mapping with name {0} already exists'.format(name))

        tcp = self._port_string_to_port_list(tcp_ports, 'TCP')
        udp = self._port_string_to_port_list(udp_ports, 'UDP')

        self._settings.insert(priority, {'name': name,
                                         'hosts': [x.strip() for x in hosts.split(',')],
                                         'priority': priority,
                                         'ports': tcp+udp
                                         })

        self._refresh_priorities()

    @getted
    def remove(self, name=None, priority=None):
        """Remove a l4 mapping rule

        It accepts one of name or priority. If name and priority are issued
        it will remove the rule named `name` only if it maches `priority`

        `name` is the name of the l4 mapping

        `priority` is the priority of the l4 mapping
        """
        super(L4Mapping, self).remove(name, priority)


class CustomApplications(DPIResource):
    @getted
    def add(self, name, uri):
        """Add a custom application rule
        
        `name` is the name of the rule

        `uri` is a string representing a uri
        """

        obj = self._get_by_name(name)

        if obj is not None:
            raise ValueError('a l4 mapping with name {0} already exists'.format(name))

        self._settings.append({'name': name, 'uri': uri})

    @getted
    def remove(self, name):
        """Remove a custom application rule

        `name` is the name of the rule
        """
        obj = self._get_by_name(name)
        if obj is not None:
            self._settings.remove(obj)
        else:
            raise ValueError('The rule with name {0} does not exist'.format(name))


class ProfilerExport(Settings4.ProfilerExport):
    def _lookup_profiler(self, address):
        for p in self.data.profilers:
            if p.address == address:
                return address
        raise ValueError('No profiler with addredss {0} has been found in the configuration'.format(address))

    @getted
    def enable_dpi(self, address):
        p = self._lookup_profiler(address)
        p['dpi_enabled'] = True
    
    @getted
    def disable_dpi(self, address):
        p = self._lookup_profiler(address)
        p['dpi_enabled'] = False

class Snmp(BasicSettingsFunctionality, SettingsLookup):
    """Snmp settings configuration"""
    pass

class Alerts(BasicSettingsFunctionality, SettingsLookup):
    """Alerts settings configuration"""
    pass 

class Settings5(Settings4):
    '''Interface to various configuration settings on the shark appliance. Version 5.0 API'''    

    def __init__(self, shark):
        super(Settings5, self).__init__(shark)
        self.port_definitions = PortDefinitions(shark.api.port_definitions, shark.api.srt_ports)
        self.group_definitions = GroupDefinitions(shark.api.port_groups)
        self.l4_mapping = L4Mapping(shark.api.l4_mappings)
        self.custom_applications = CustomApplications(shark.api.custom_applications)
        self.profiler_export = ProfilerExport(shark)
        self.snmp = Snmp(shark.api.snmp)
        self.alerts = Alerts(shark.api.alerts)
