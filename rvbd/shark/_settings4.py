# Copyright (c) 2013 Riverbed Technology, Inc.
#
# This software is licensed under the terms and conditions of the 
# MIT License set forth at:
#   https://github.com/riverbed/flyscript/blob/master/LICENSE ("License").  
# This software is distributed "AS IS" as set forth in the License.

import functools

def getted(f):
    @functools.wraps(f)
    def wrapper(self, *args, **kwds):
        if self._settings is None:
            raise LookupError('You have to get the configuration first via the get method')
        return f(self, *args, **kwds)
    return wrapper

class Settings4(object):
    '''Interface to various configuration settings on the shark appliance.'''

    class Basic:
        '''Wrapper class around basic system settings.'''
        def __init__(self, shark):
            self.shark = shark
            self._settings = None

        def get(self):
            if self._settings is None:
                self._settings = self.shark.api.settings.get_basic()

        @getted
        def save(self):
            self.shark.api.settings.update_basic(self._settings)

        @property
        @getted    
        def hostname(self):
            return self._settings.hostname

        @hostname.setter
        @getted        
        def update_hostname(self, hostname):
            self._settings.hostname = hostname

        @property
        @getted
        def domain(self):
            return self._settings.domain

        @domain.setter
        @getted
        def set_domain(self, domain):
            self._settings.domain = domain

        @property
        @getted
        def dns_servers(self):
            return (self._settings.primary_dns, self._settings.secondary_dns)

        @dns_servers.setter
        @getted
        def set_dns_servers(self, primary_dns="", secondary_dns=""):
            self._settings.primary_dns = primary_dns
            self._settings.secondary_dns = secondary_dns

        @property
        @getted
        def ssh_enabled(self):
            return self._settings.ssh_enabled

        @ssh_enabled.setter
        @getted
        def set_ssh_enabled(self, ssh_enabled):
            self._settings.ssh_enabled = ssh_enabled

        @property
        @getted
        def fips_enabled(self):
            return self._settings.fips_enabled

        @fips_enabled.setter
        @getted
        def set_fips_enabled(self, fips_enabled):
            self._settings.fips_enabled = fips_enabled

        @property
        @getted
        def timezone(self):
            return self._settings.timezone

        @timezone.setter
        @getted
        def set_timezone(self, timezone):
            self._settings.timezone = timezone

        @property
        @getted
        def ntp_servers(self):
            return self._settings.ntp_config.servers

        @ntp_servers.setter
        @getted
        def set_ntp_servers(self, servers):
            self._settings.ntp_config.servers = servers

    class Auth:
        """Wrapper class around authentication settings.

        It maintains a cache of the current settings and exposes
        specific get/set methods for the various elements of the
        authentication configuration.

        By default all settings are immediately applied for a given
        function, and most will invalidate the current login session.

        Thus if multiple setting operations need to be performed, the
        caller should set the object's update_immediately flag to
        False and then explicitly call update() to apply the changes.
        """

        def __init__(self, shark):
            self.shark = shark
            self._settings = None

        def get(self):
            if self._settings is None:
                self._settings = self.shark.api.settings.get_auth()

        @getted
        def save(self):
            self.shark.api.settings.update_auth(self._settings)

        @property
        @getted
        def local_settings(self):
            return self._settings.local_settings

        @local_settings.setter
        @getted
        def set_local_settings(self,
                               min_password_length = 0,
                               password_change_history = 0,
                               min_password_special_character = 0,
                               min_password_upper_letter = 0,
                               max_unsuccessful_login_attempts = 0,
                               min_password_lower_letter = 0,
                               max_password_lifetime_days = 0,
                               min_password_numeric_character = 0):

            self._settings.local_settings.min_password_length = min_password_length
            self._settings.local_settings.password_change_history = password_change_history
            self._settings.local_settings.min_password_special_character = min_password_special_character
            self._settings.local_settings.min_password_upper_letter = min_password_upper_letter
            self._settings.local_settings.max_unsuccessful_login_attempts = max_unsuccessful_login_attempts
            self._settings.local_settings.min_password_lower_letter = min_password_lower_letter
            self._settings.local_settings.max_password_lifetime_days = max_password_lifetime_days
            self._settings.local_settings.min_password_numeric_character = min_password_numeric_character


        @property
        @getted
        def radius_settings(self):
            return self._settings.radius_settings

        @radius_settings.setter
        @getted
        def set_radius_settings(self,
                                servers,
                                client_port="na",
                                encryption_protocol="PAP",
                                accounting_enabled=False):
            '''
            Update the radius authentication settings.

            servers: A list of dictionaries contiaining address, port,
            and sharedSecret elements

            client_port: XXX
            encryption_protocol: XXX
            accounting_enabled: XXX
            '''
            self._settings.radius_settings.servers = servers
            self._settings.radius_settings.client_port = client_port
            self._settings.radius_settings.encryption_protocol = encryption_protocol
            self._settings.radius_settings.accounting_enabled = accounting_enabled

        @property
        @getted
        def tacacs_settings(self):
            return self._settings.tacacs_settings

        @tacacs_settings.setter
        @getted
        def set_tacacs_settings(self,
                                servers,
                                accounting_terminator = "2>&1",
                                accounting_enabled = True,
                                accounting_value = "cace",
                                authorization_value = "cace",
                                client_port = "ttyp6",
                                authorization_response_attribute = "*",
                                authorization_attribute = "service",
                                accounting_attribute = "task_id"):
            '''
            Update the TACACS+ authentication settings.

            servers: A list of dictionaries contiaining address, port,
            and sharedSecret elements

            '''
            
            self._settings.tacacs_settings.servers = servers
            self._settings.tacacs_settings.accounting_terminator = accounting_terminator
            self._settings.tacacs_settings.accounting_enabled = accounting_enabled
            self._settings.tacacs_settings.accounting_value = accounting_value
            self._settings.tacacs_settings.authorization_value = authorization_value
            self._settings.tacacs_settings.client_port = client_port
            self._settings.tacacs_settings.authorization_response_attribute = authorization_response_attribute
            self._settings.tacacs_settings.authorization_attribute = authorization_attribute
            self._settings.tacacs_settings.accounting_attribute = accounting_attribute

        @property
        @getted
        def auth_sequence(self):
            return self._settings.auth_sequence

        @auth_sequence.setter
        @getted
        def set_auth_sequence(self, modes):
            self._settings.auth_sequence = modes

        @property
        @getted
        def remote_auth_settings(self):
            return self._settings.remote_auth_settings

        @remote_auth_settings.setter
        @getted
        def set_remote_auth_settings(self, fallback_on_unavailable_only, default_group=""):
            self._settings.remote_auth_settings.fallback_on_unavailable_only = fallback_on_unavailable_only
            self._settings.remote_auth_settings.default_group = default_group

        @property
        @getted
        def webui_settings(self):
            return self._settings.webui_settings

        @webui_settings.setter
        @getted
        def set_webui_settings(self, login_banner="", need_purpose=False, session_duration=60):
            self._settings.webui_settings.login_banner = login_banner
            self._settings.webui_settings.need_purpose = need_purpose
            self._settings.webui_settings.session_duration = session_duration

    class Audit:
        """Wrapper class around audit configuration.

        It maintains a cache of the current audit settings for each
        category as a map indexed by the category type. Various
        accessor methods can then update the settings.
        
        By default all settings are immediately applied for a given
        function.

        If multiple setting operations need to be performed, the
        caller should set the object's update_immediately flag to
        False and then explicitly call update() to apply the changes.
        """

        def __init__(self, shark):
            self.shark = shark
            self.categories = None
            self._settings = None

        def get(self):
            if self.categories is None:
                self.categories = {}
                self._settings = self.shark.api.settings.get_audit()
                for c in self._settings.audit_categories:
                    self.categories[c.audit_type] = c

        @getted
        def save(self, force=False):
            self.shark.api.settings.update_audit({'audit_categories' : self.categories.values()})

        @getted
        def category_settings(self, category):
            '''Return a reference to the current settings for the given category.'''
            return self.categories[category]

        @getted
        def update_category_settings(self, category, min_syslog_level, min_remote_server_level):
            '''Return a reference to the current settings for the given category.'''
            self.categories[category].min_syslog_level = min_syslog_level
            self.categories[category].min_remote_server_level = min_remote_server_level

        @getted
        def get_category_descriptions(self):
            '''Return a list of (category, description) pairs containing
            the description for each audit category.'''
            return [(c.audit_type, c.description) for c in self.categories.values()]

        @getted
        def syslog_levels(self):
            '''Return a list of (category, level) pairs containing the
            currently enabled syslog level for each audit category.'''
            return [(c.audit_type, c.min_syslog_level) for c in self.categories.values()]

        @getted
        def update_syslog_levels(self, levels):
            '''Given a list of (category, level) pairs, updates the min
            syslog levels for each of the given categories.'''
            for category, level in levels:
                self.categories[category].min_syslog_level = level

        @getted
        def update_all_syslog_levels(self, level):
            '''Update the syslog level for all categories to the given level'''
            for c in self.categories:
                c.min_syslog_level = level

        @getted
        def remote_server_levels(self):
            '''Return a list of (category, level) pairs containing the
            currently enabled remote_server level for each audit category.'''
            return [(c.audit_type, c.min_remote_server_level) for c in self.categories.values()]

        @getted
        def update_remote_server_levels(self, levels):
            '''Given a list of (category, level) pairs, updates the min
            remote_server levels for each of the given categories.'''
            for category, level in levels:
                self.categories[category].min_remote_server_level = level

        @getted
        def update_all_remote_server_levels(self, level):
            '''Update the remote_server level for all categories to the given level'''
            for c in self.categories:
                c.min_remote_server_level = level
                    
    class Licenses:
        '''Wrapper class around license configuration'''
        def __init__(self, shark):
            self.shark = shark

        def get(self):
            return [lic.key for lic in self.shark.api.licenses.get_all()]

        @getted
        def add(self, license_keys):
            self.shark.api.licenses.add_license(license_keys)

        @getted
        def remove(self, key):
            self.shark.api.licenses.delete_license(key)

        @getted
        def clear(self):
            for lic in self.get_all():
                self.shark.api.licenses.delete_license(lic)

        @getted
        def status(self):
            return self.shark.api.licenses.get_status()


    class Firewall:
        ''' Allows to get the current configuration of the firewall and 
        set a new one.'''

        def __init__(self, shark):
            self.shark = shark
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

           
    class Certificates:
        '''Wrapper class around the certificates configuration'''
        def __init__(self, shark):
            self.shark = shark
    
        def get(self):
            return self.shark.api.certificates.get_certificates_config()

    class ProfilerExport:
        """Wrapper class around authentication settings.

        It maintains a cache of the current settings and exposes
        specific get/set methods for the various elements of the
        authentication configuration.

        By default all settings are immediately applied for a given
        function, and most will invalidate the current login session.

        Thus if multiple setting operations need to be performed, the
        caller should set the object's update_immediately flag to
        False and then explicitly call update() to apply the changes.
        """

        def __init__(self, shark):
            self.shark = shark
            self._settings = None

        def get(self):
            self._settings = self.shark.api.settings.get_profiler_export()

        @getted    
        def save(self):
            self.shark.api.settings.update_profiler_export(self._settings)

        @getted    
        def enabled(self):
            """Return whether or not profiler export is enabled"""
            return self._settings.enabled

        @getted
        def enable(self):
            """Enable profiler export"""
            self._settings.enabled = True

        @getted    
        def disable(self):
            """Disable profiler export"""
            self._settings.enabled = False

        @getted    
        def get_profilers(self):
            """Return a list of (address, status) pairs for all enabled profilers."""
            return [(p.address, p.status) for p in self._settings.profilers]

        @getted    
        def add_profiler(self, address):
            if len(self._settings.profilers) == 2:
                raise ValueError("Only two profilers can be enabled")
            self._settings.profilers.append({'address' : address})

        @getted    
        def remove_profiler(self, address):
            for p in self._settings.profilers:
                if p['address'] == address:
                    self._settings.profilers.remove(p)
                    # Check if there is no Profiler set
                    if len(self._settings.profilers) == 0:
                        # If no profiler is available Profiler Export should be disabled 
                        self._settings.enabled = False
                    return
            raise ValueError("No profiler enabled with address %s" % address)

        @getted    
        def remove_all_profilers(self):
            self._settings.profilers = []
            self._settings.enabled = False

        @getted    
        def enabled_ports(self):
            """Return a list of all ports for which profiler export is enabled."""
            return [port.name for port in self._settings.adapter_ports if port.enabled]

        @getted    
        def disabled_ports(self):
            """Return a list of all ports for which profiler export is not enabled."""
            return [port.name for port in self._settings.adapter_ports if not port.enabled]

        @getted        
        def enable_port(self, name, bpf_filter=None, voip_enabled=None):
            """Enable the given port for profiler export, optionally
            setting the given BPF filter and whether or not voip
            metrics should be enabled."""

            for port in self._settings.adapter_ports:
                if port.name == name:
                    port.enabled = True
                    if bpf_filter is not None:
                        port.BPF_filter = bpf_filter
                    if voip_enabled is not None:
                        port.VoIP_enabled = voip_enabled
                    return

            raise ValueError("Invalid port " + port)

        @getted    
        def disable_port(self, name):
            for port in self._settings.adapter_ports:
                if port.name == name:
                    port.enabled = False
                    return
            raise ValueError("Invalid port " + port)

        @getted    
        def get_port_config(self, name):
            for port in self._settings.adapter_ports:
                if port.name == name:
                    return port
            raise ValueError("No such port %s" % port)

    @property
    @getted
    def cors_domains(self):
        '''Return the list of allowed domains for cross-origin
        resource access.'''
        return self.shark.api.settings.get_cors_domains()

    @cors_domains.setter
    @getted
    def update_cors_domains(self, domains):
        '''Update the list of allowed domains for cross-origin
        resource access.'''
        return self.shark.api.settings.update_cors_domains(domains)
    
    def __init__(self, shark):
        super(Settings4, self).__init__()
        self.shark = shark
        self.auth = self.Auth(shark)
        self.audit = self.Audit(shark)
        self.basic = self.Basic(shark)
        self.licenses = self.Licenses(shark)
        self.firewall = self.Firewall(shark)
        self.certificates = self.Certificates(shark)
        self.profiler_export = self.ProfilerExport(shark)

        # For the raw text handlers there's nothing that the
        # high-level API needs to add or hide
        self.get_raw = shark.api.settings.get_raw
        self.update_raw = shark.api.settings.update_raw
        self.reset_raw = shark.api.settings.reset_raw
        self.get_protocol_groups = shark.api.settings.get_protocol_groups
        self.update_protocol_groups = shark.api.settings.update_protocol_groups
        self.get_protocol_names = shark.api.settings.get_protocol_names
        self.update_protocol_names = shark.api.settings.update_protocol_names


        

