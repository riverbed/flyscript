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
import copy
import time

def getted(f):
    @functools.wraps(f)
    def wrapper(self, *args, **kwds):
        if self.data is None:
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
    """
    def __init__(self, api):
        self.data = None
        self._api = api

    def _get(self, f,  force=False):
        """Gets the configuration calling the f function
        """
        if self.data is None or force is True:
            self.data = f()
        return copy.deepcopy(self.data)

    def get(self, force=False):
        """Gets the configuration from the server
        """
        return self._get(self._api.get, force)

    @getted
    def _save(self, f):
        """Saves the configuration using the function f"""
        f(self.data)
        self.get(force=True)

    @getted
    def save(self):
        """Save configuration to the server
        """
        self._save(self._api.update)

    @getted
    def cancel(self):
        """Cancel pending changes to the configuration
        and reloads the configuration from server
        """
        return self.get(force=True)

    @getted
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
                self.data = json.loads(f.read())
        elif isinstance(path_or_obj, dict):
            self.data = path_or_obj
        elif isinstance(path_or_obj, list):
            self.data = path_or_obj
        else:
            raise ValueError('path_or_obj muth be a filepath, a dict or a list')

        if save is True:
            self.save()

class NoBulk(object):
    """Mixin class to force get of new configuration in not bulk update capable
    settings

    This basically overrides the save method such that it doesn't perform a
    bulk update on the resource but fetches the new data from the server only
    """

    @getted
    def save(self):
        #this mymics settings behaviour
        #for all the resources that do not allow bulk update
        self.get(force=True)

class Basic(BasicSettingsFunctionality):
    """Wrapper class around basic system settings."""

    #definining get/save here in order to do not touch _api4.py
    def get(self, force=False):
        """Get configuration from the server
        """
        return self._get(self._api.get_basic)

    @getted
    def save(self):
        self._save(self._api.update_basic)


class Auth(BasicSettingsFunctionality):
    """Wrapper class around authentication settings."""

    def get(self, force=False):
        """Get configuration from the server
        """
        return self._get(self._api.get_auth)

    @getted
    def save(self):
        self._save(self._api.update_auth)
        

class Audit(BasicSettingsFunctionality):
    """Wrapper class around audit configuration."""

    def get(self, force=False):
        """Get configuration from the server
        """
        return self._get(self._api.get_audit)

    @getted
    def save(self):
        self._save(self._api.update_audit)

                    
class Licenses(NoBulk, BasicSettingsFunctionality):
    """Wrapper class around license configuration."""

    @getted
    def save(self):
        NoBulk.save(self)
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
        for lic in self.data:
            self._api.delete_license(lic['key'])

    @getted
    def status(self):
        return self._api.get_status()


class Firewall(BasicSettingsFunctionality):
    """Allows to get the current configuration of the firewall and 
    set a new one."""

    def get(self, force=False):
        """Get configuration from the server
        """
        return self._get(self._api.get_firewall_config)

    @getted
    def save(self):
        self._save(self._api.update_firewall_config)


class Certificates(NoBulk, BasicSettingsFunctionality):
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
        NoBulk.save(self)
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
        return self._get(self._api.get_profiler_export)

    @getted
    def save(self):
        self._save(self._api.update_profiler_export)


class CorsDomain(BasicSettingsFunctionality):

    def get(self, force=False):
        """Get configuration from the server
        """
        return self._get(self._api.get_cors_domains)

    @getted
    def save(self):
        self._save(self._api.update_cors_domains)


class Users(NoBulk, BasicSettingsFunctionality):

    @getted
    def add(self, username, password, groups=[], can_be_locked=False):
        """Adds a user to the Shark

        `username` is a string representing the username

        `groups` is the group the user should be added in.
        Administrators is the administrators group. Add user to that group
        to make the user with administator privileges.

        `can_be_locked` is a boolean representing if the user can be locked out
        from the system or not
        """
        self._api.add({'name': username,
                       'password': password,
                       'groups': groups,
                       'can_be_locked': can_be_locked
                       })
    @getted
    def delete(self, username):
        """Delete user from the system

        `username` is the username of the user to be deleted
        """
        self._api.delete(username)

    @getted
    def change_password(self, username, password):
        """Change password of an user
        """
        self._api.update(username, {'existing_password': '',
                                    'new_password': password})

class Groups(NoBulk, BasicSettingsFunctionality):

    @getted
    def add(self, name, description='', capabilities=[]):
        """Adds a new group to the system

        `name` is the name of the group

        `description` is the description of the group

        `capabilities` is a list of permissions the group has.
        They can be:

        CAPABILITY_ADMINISTRATOR,
        CAPABILITY_APPLY_VIEWS_ON_FILES,
        CAPABILITY_APPLY_VIEWS_ON_INTERFACES,
        CAPABILITY_SHARE_VIEWS,
        CAPABILITY_CREATE_FILES,
        CAPABILITY_IMPORT_FILES,
        CAPABILITY_EXPORT_FILES,
        CAPABILITY_CREATE_JOBS,
        CAPABILITY_SCHEDULE_WATCHES,
        CAPABILITY_ACCESS_PROBE_FILES
        """
        self._api.add({'name': name,
                       'description': description,
                       'capabilities': capabilities})

    @getted
    def delete(self, name):
        """Removes group from the groups in the Shark

        `name` is the name of the group
        """
        self._api.delete(name)

class Update(NoBulk, BasicSettingsFunctionality):

    def load_iso_from_url(self, url):
        self._api.load_iso_from_url({'url':url})

    def upload_iso(self, f):
        self._api.upload_iso(f)

    @getted
    def delete_iso(self):
        self._api.delete_iso({'state': 'NEUTRAL', 'reset': True})

    @getted
    def update(self):
        if self.data['init_id'] is not '': 
            res = self._api.update({'init_id':self.data.init_id, 'state':'RUNNING'})
        else:
            raise SystemError('Server does not have any iso image loaded for upload. Upload an iso first and save the configuration to proceed.')

        while res['state'] == 'RUNNING':
            time.sleep(5)
            res = self.get(force=True)

        if res['state'] != 'NEUTRAL':
            raise SystemError('Server returned error while update: {0}'.format(res['comment']))

        return res

class Storage(NoBulk, BasicSettingsFunctionality):

    def reinitialize(self, wait=True):
        """Reinitializes the packet storage

        If `wait` is True it will wait for the packet storage to be back again
        before returning

        WARNING: This operation will lose all packets in every job
        """
        self._api.reinitialize()

        res = self.get(force=True)

        while res['state'] == 'INITIALIZING':
            time.sleep(5)
            res = self.get(force=True)

        if res['state'] != 'OK':
            raise SystemError('Server returned error while reinitializing packet storage')

        return res

    def format(self, percentage_reserved_space=0):
        """Formats the packet storage

        `percentage_reserved_space` is the percentage of disk reserved starting from the
        outher boundaries of the disk.
        Since I/O operations at the farmost parts of the disk have higher latency this is
        often used to increase performances of the packet recorder.
        `percentage_reserved_space` can be any value from 0 (default) to 95.

        WARNING: This operation will lose all packets in every job
        """

        assert percentage_reserved_space >=0 and percentage_reserved_space < 96
        self._api.format({'reserved_space': percentage_reserved_space})

class NotImplementedSetting(object):
    def __init__(self, msg=''):
        self.msg = msg

    def get(self, force=True):
        raise NotImplementedError('This setting is not available for this version of Shark'+self.msg)

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
        self.users = Users(shark.api.users)
        self.groups = Groups(shark.api.groups)
        self.update = Update(shark.api.update)
        self.storage = Storage(shark.api.storage)

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

        #these have been implemented from API >= 5.0 
        self.alerts = NotImplementedSetting()
        self.snmp = NotImplementedSetting()
