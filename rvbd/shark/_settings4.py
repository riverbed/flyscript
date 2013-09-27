# Copyright (c) 2013 Riverbed Technology, Inc.
#
# This software is licensed under the terms and conditions of the 
# MIT License set forth at:
#   https://github.com/riverbed/flyscript/blob/master/LICENSE ("License").  
# This software is distributed "AS IS" as set forth in the License.

import functools
import warnings

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
        try:
            return getattr(self._settings, name)
        except AttributeError:
            return object.__getattribute__(self, name)

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

    def load(self, path_or_obj, save=True):
        """Load the configuration from a path or dict

        `path_or_obj` is or a string representing a path or a dict/list representing the
        configuration

        `save` is a flag to automatically save to the server after load,
        default to True
        """
        if isinstance(path_or_obj, basestring):
            with open(path_or_obj, 'r') as f:
                self._settings = json.loads(f.read())
        elif isinstance(path_or_obj, dict):
            self._settings = JsonDict(path_or_obj)
        elif isinstance(path_or_obj, list):
            self._settings = list(path_or_obj)
        else:
            raise ValueError('path_or_obj muth be a filepath, a dict or a list')

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
        warnings.warn('Reboot of shark is needed to apply the new configuration')
    
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

    def get(self, force=False):
        """Get configuration from the server
        """
        if self._settings is None and force is False:
            self._settings = JsonDict(self._api.get_firewall_config())
        return JsonDict(self._settings)
        
    @getted
    def save(self):
        self._api.update_firewall_config(self._settings)
        self.get(force=True)


class Certificates(BasicSettingsFunctionality):
    '''Wrapper class around the certificates configuration'''

    def _gen_cert_configuration(self, *args, **kwargs):
        return {
                'issued_to':{
                    'country': kwargs.get('country') or 'US',
                    'email': kwargs.get('email') or '',
                    'locality': kwargs.get('locality') or 'San Francisco',
                    'organization': kwargs.get('organization') or 'Riverbed Technology',
                    'organization_unit': kwargs.get('organization_unit') or '',
                    'state': kwargs.get('state') or 'CA'
                    },
                'validity':{
                    'days': kwargs.get('days') or 365
                    }
                }

    @getted
    def save(self):
        #this mymics other settings behaviour
        #even tho Licenses is not a bulk update
        self.get(force=True)
        warnings.warn('Reboot of shark is needed to apply the new configuration')
    
    @getted
    def use_profiler_export_certificate_for_web(self):
        """Copies profiler export certificate and use it for webui"""
        self._api.copy_profiler_export_certificate()
      
    @getted
    def set_certificate_for_web(self, cert):
        """Given a certificate in PEM format, uploads to the server and
        sets as webui certificate.

        The PEM certificate must contain both private key and CA-signed public certificate"""
        self._api.update_web_certificate({'pem':cert})

    @getted
    def generate_new_certificate_for_web(self, country=None, email=None, locality=None,
                                         organization=None, organization_unit=None,
                                         state=None, days=None):
        """Generates a new certificate for the webui"""
        kwargs = locals()
        kwargs.pop('self')
        self._api.generate_web_certificate(self._gen_cert_configuration(**kwargs))

    @getted
    def set_certificate_for_profiler_export(self, cert):
        """Give a certificate in PEM format, uploads to the server and sets
        as profiler export certificate

        The PEM certificate must contain both private key and CA-signed public certificate"""
        self._api.update_profiler_export_certificate({'pem': cert})

    @getted
    def generate_new_certificate_for_profiler_export(self, country=None, email=None,
                                                     locality=None,organization=None,
                                                     organization_unit=None, state=None,
                                                     days=None):
        """Generates a new certificate for profiler export"""
        kwargs = locals()
        kwargs.pop('self')
        self._api.generate_profiler_export_certificate(self._gen_cert_configuration(**kwargs))

    @getted
    def use_web_interface_certificate_for_profiler_export(self):
        """Copies webui certificate and use it for profiler export"""
        self._api.copy_web_certificate()

    @getted
    def add_profiler_trusted_certificate(self, name, cert):
        """Adds the given PEM certificate to the list of trusted certificates
        under the given name"""
        self._api.add_trusted_profiler_certificate({
                'id': name,
                'pem': cert
                })

    @getted
    def remove_profiler_trusted_certificate(self, name):
        """Removes the name of a PEM certificate that is trusted, removes from the list of
        trusted certificates"""
        self._api.delete_trusted_profiler_certificate(name)
    

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
            self._settings = list(self._api.get_cors_domains())
        return list(self._settings)
    
    @getted
    def save(self):
        self._api.update_cors_domains(self._settings)
        self.get(force=True)


class Settings4(object):
    """Interface to various configuration settings on the shark appliance."""

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
        self.cors_domain = CorsDomain(shark.api.settings)

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
