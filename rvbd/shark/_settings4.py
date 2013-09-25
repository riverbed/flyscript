# Copyright (c) 2013 Riverbed Technology, Inc.
#
# This software is licensed under the terms and conditions of the 
# MIT License set forth at:
#   https://github.com/riverbed/flyscript/blob/master/LICENSE ("License").  
# This software is distributed "AS IS" as set forth in the License.

import functools

from rvbd.common.jsondict import JsonDict
import json

def getted(f):
    @functools.wraps(f)
    def wrapper(self, *args, **kwds):
        if self._settings is None:
            raise LookupError('You have to get the configuration first via the get method')
        return f(self, *args, **kwds)
    return wrapper

 
class BasicSettingsFunctionality(object):
    """This basic mixin is used as a base for all the settings related classes.
    It ensures that the following interface is implemented for all the settings:
     get()
     save()
     cancel()
     download()
     load()

    It defines a __getattr__ and __setattr__ such that attributes that start with _ are
    added as object attribute and all the remaining is added to the inner _settings
    JsonDict that stores the settings configuration and get synced with the server
    as soon as the user save() the configuration.
    """
    def __init__(self, api):
        self._settings = None
        self._api = api

    def __getattr__(self, name):
        if name in self._settings:
            return getattr(self._settings, name)
        else:
            raise AttributeError

    def __setattr__(self, name, value):
        """If name start with _ add as a normal attribute, add to _settings otherwise"""
        if name[0] == '_':
            super(BasicSettingsFunctionality, self).__setattr__(name, value)
        elif self._settings is None:
            raise RuntimeError('Get the settings from the server first with .get()')
        else:
            self._settings[name] = value
  
    def __dir__(self):
        """Retrieve posible attributes from object and _settings keys (since it's a
        JsonDict object)
        """
        return sorted(set(dir(type(self))+dir(self._settings)))


    def get(self, force=False):
        """Get configuration from the server
        """
        if self._settings is None and force is False:
            self._settings = JsonDict(self._api.get())
        #with this we return a copy of _settings
        return JsonDict(self._settings)

    @getted
    def save(self):
        """Save configuration to the server
        """
        self._api.update(self._settings)
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

    def load(self, path_or_dict, save=True):
        """Load the configuration from a path or dict

        `path_or_dict` is or a string representing a path or a dict representing the
        configuration

        `save` is a flag to automatically save to the server after load,
        default to True
        """
        if isinstance(path_or_dict, basestring):
            with open(path_or_dict, 'r') as f:
                self._settings = json.loads(f.read())
        elif isinstance(path_or_dict, dict):
            self._settings = JsonDict(path_or_dict)
        else:
            raise ValueError('path_or_dict muth be a filepath or a dict')

        if save is True:
            self.save()

class Basic(BasicSettingsFunctionality):
    """Wrapper class around basic system settings."""

    #definining get/save here in order to do not touch _api4.py
    def get(self, force=False):
        """Get configuration from the server
        """
        if self._settings is None and force is False:
            self._settings = JsonDict(self._api.get_basic())
        return JsonDict(self._settings)


    @getted
    def save(self):
        self._api.update_basic(self._settings)
        self.get(force=True)


class Auth(BasicSettingsFunctionality):
    """Wrapper class around authentication settings."""

    def get(self, force=False):
        """Get configuration from the server
        """
        if self._settings is None and force is False:
            self._settings = JsonDict(self._api.get_auth())
        return JsonDict(self._settings)

    @getted
    def save(self):
        self._api.update_auth(self._settings)
        self.get(force=True)
        

class Audit(BasicSettingsFunctionality):
    """Wrapper class around audit configuration."""

    def get(self, force=False):
        """Get configuration from the server
        """
        if self._settings is None and force is False:
            self._settings = JsonDict(self._api.get_audit())
        return JsonDict(self._settings)


    @getted
    def save(self):
        self._api.update_audit(self._settings)
        self.get(force=True)


                    
class Licenses(BasicSettingsFunctionality):
    """Wrapper class around license configuration."""

    def get(self, force=False):
        """Get configuration from the server
        """
        if self._settings is None and force is False:
            self._settings = self._api.get_all()
        return list(self._settings)

    @getted
    def save(self):
        #this mymics other settings behaviour
        #even tho Licenses is not a bulk update
        self.get(force=True)
    
    @getted
    def add(self, license_keys):
        #the add wants a list of keys while the
        #delete wants a single key
        self._api.add_license([license_keys])
        
    @getted
    def remove(self, key):
        self._api.delete_license(key)
        
    @getted
    def clear(self):
        for lic in self._settings:
            self._api.delete_license(lic.key)

    @getted
    def status(self):
        return self._api.get_status()


class Firewall(BasicSettingsFunctionality):
        """Allows to get the current configuration of the firewall and 
        set a new one."""

        def __init__(self, shark):
            self._shark = shark
            self._firewall_config = None
            self._settings = None

        @property
        @getted
        def firewall_settings(self):
            return self._firewall_config
 
        def get(self):
            config_dict = self.shark.api.settings.get_firewall_config()
            self._settings = config_dict
            self._firewall_config = self.FirewallConfig(config_dict["firewall_enabled"],
                                                        config_dict["default_policy"],
                                                        config_dict["rules"])

        @getted
        def save(self, force=False):
            config_dict = {"firewall_enabled": self._firewall_config.enabled,
                           "default_policy" :self._firewall_config.default_policy,
                           "rules" :self._firewall_config.rules
                           }
            self.shark.api.settings.update_firewall_config(config_dict)

        @firewall_settings.setter
        @getted
        def set_firewall_settings(self, firewall_config):
            '''
            Update the firewall configuration

            firewall_config: the new configuration to set
            '''
            self._firewall_config = firewall_config
        #TODO: test
        class FirewallConfig:
            '''
            Wrapper class around the firewall configuration
            '''
            def __init__(self,
                         enabled=False,
                         default_policy="DROP",
                         rules=None):
                '''
                Creates a new configuration

                enabled: true if the firewall is enabled, false otherwise
                default_policy: default policy for the firewall input chain
                rules: set of firewall rules
                '''
                self.enabled = enabled
                self.default_policy = default_policy
                self.rules = rules or []


            def add_rule(self,
                         action,
                         protocol=None,
                         description=None,
                         dest_port=None,
                         source=None):
                '''
                Add a new rule with the fields specified in the call. The new rule is appended 
                to the current firewall configuration

                action: action  to  take  when  a  packet  matches  the  rule 
                        Allowed values are ACCEPT, DROP, LOG_ACCEPT, LOG_DROP 
                        This is a mandatory attribute and it does  not have a 
                        default value

                protocol: rule protocol. Allowed values are ALL, TCP, UDP, ALL,
                          ICMP.

                description: a brief description for the rule. 

                dest_port: rule destination port 

                source: rule IPV4 source address. It can contain a netmasks specified as CIDR
                        format or as IPV4 address.",
                '''
                rule = {"action" :action,
                        "protocol":protocol,
                        "description":description,
                        "dest_port": dest_port,
                        "source": source
                        }
                #clean from None values
                rule = dict((k, v) for k, v in rule.iteritems() if v is not None)
                self.rules.append(rule)

            def remove_rule(self,
                            index):
                '''
                index: index of the rule to remove
                '''
                del self.rules[index]

           
class Certificates(BasicSettingsFunctionality):
    '''Wrapper class around the certificates configuration'''

    def get(self, force=False):
        """Get configuration from the server
        """
        if self._settings is None and force is False:
            self._settings = JsonDict(self._api.get_certificates_config())
        return JsonDict(self._settings)

    
class ProfilerExport(BasicSettingsFunctionality):
    """Wrapper class around authentication settings. """

    def get(self, force=False):
        """Get configuration from the server
        """
        if self._settings is None and force is False:
            self._settings = JsonDict(self._api.get_profiler_export())
        return JsonDict(self._settings)

    @getted
    def save(self):
        self._api.update_profiler_export(self._settings)
        self.get(force=True)


class CorsDomain(BasicSettingsFunctionality):

    def get(self, force=False):
        """Get configuration from the server
        """
        if self._settings is None and force is False:
            self._settings = JsonDict(self._api.get_cors_domains())
        return JsonDict(self._settings)
    
    @getted
    def save(self):
        self._api.update_cors_domains(self._settings)
        self.get(force=True)


class Settings4(object):
    '''Interface to various configuration settings on the shark appliance.'''

    def __init__(self, shark):
        super(Settings4, self).__init__()
        self.shark = shark
        self.auth = Auth(shark.api.settings)
        self.audit = Audit(shark.api.settings)
        self.basic = Basic(shark.api.settings)
        self.licenses = Licenses(shark.api.licenses)
        self.firewall = Firewall(shark.api.settings)
        self.certificates = Certificates(shark.api.certificates)
        self.profiler_export = ProfilerExport(shark.api.settings)

        # For the raw text handlers there's nothing that the
        # high-level API needs to add or hide
        self.get_raw = shark.api.settings.get_raw
        self.update_raw = shark.api.settings.update_raw
        self.reset_raw = shark.api.settings.reset_raw

        #these are now DPI in Shark API 5.0
        self.get_protocol_groups = shark.api.settings.get_protocol_groups
        self.update_protocol_groups = shark.api.settings.update_protocol_groups
        self.get_protocol_names = shark.api.settings.get_protocol_names
        self.update_protocol_names = shark.api.settings.update_protocol_names
