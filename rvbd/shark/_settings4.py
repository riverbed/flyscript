# Copyright (c) 2013 Riverbed Technology, Inc.
#
# This software is licensed under the terms and conditions of the 
# MIT License set forth at:
#   https://github.com/riverbed/flyscript/blob/master/LICENSE ("License").  
# This software is distributed "AS IS" as set forth in the License.



class Settings4(object):
    '''Interface to various configuration settings on the shark appliance.'''

    class Basic:
        '''Wrapper class around basic system settings.'''
        def __init__(self, shark):
            self.shark = shark
            self._settings = None

        def _get(self):
            if self._settings is None:
                self._settings = self.shark.api.settings.get_basic()
            
        def _update(self):
            self.shark.api.settings.update_basic(self._settings)
            
        def hostname(self):
            self._get()
            return self._settings.hostname
        
        def update_hostname(self, hostname):
            self._get()
            self._settings.hostname = hostname
            self._update()
        
        def domain(self):
            self._get()
            return self._settings.domain
        
        def set_domain(self, domain):
            self._get()
            self._settings.domain = domain
            self._update()

        def dns_servers(self):
            self._get()
            return (self._settings.primary_dns, self._settings.secondary_dns)
        
        def set_dns_servers(self, primary_dns="", secondary_dns=""):
            self._get()
            self._settings.primary_dns = primary_dns
            self._settings.secondary_dns = secondary_dns
            self._update()

        def ssh_enabled(self):
            self._get()
            return self._settings.ssh_enabled
        
        def set_ssh_enabled(self, ssh_enabled):
            self._get()
            self._settings.ssh_enabled = ssh_enabled
            self._update()

        def fips_enabled(self):
            self._get()
            return self._settings.fips_enabled
        
        def set_fips_enabled(self, fips_enabled):
            self._get()
            self._settings.fips_enabled = fips_enabled
            self._update()

        def timezone(self):
            self._get()
            return self._settings.timezone
        
        def set_timezone(self, timezone):
            self._get()
            self._settings.timezone = timezone
            self._update()

        def ntp_servers(self):
            self._get()
            return self._settings.ntp_config.servers

        def set_ntp_servers(self, servers):
            self._get()
            self._settings.ntp_config.servers = servers
            self._update()

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
            self.update_immediately = True

        def _get(self):
            if self._settings is None:
                self._settings = self.shark.api.settings.get_auth()

        def update(self):
            '''Force apply any setting changes'''
            self._update(force=True)
            
        def _update(self, force=False):
            if force or self.update_immediately:
                self.shark.api.settings.update_auth(self._settings)
            
        def local_settings(self):
            self._get()
            return self._settings.local_settings

        def set_local_settings(self,
                               min_password_length = 0,
                               password_change_history = 0,
                               min_password_special_character = 0,
                               min_password_upper_letter = 0,
                               max_unsuccessful_login_attempts = 0,
                               min_password_lower_letter = 0,
                               max_password_lifetime_days = 0,
                               min_password_numeric_character = 0):
            self._get()
            self._settings.local_settings.min_password_length = min_password_length
            self._settings.local_settings.password_change_history = password_change_history
            self._settings.local_settings.min_password_special_character = min_password_special_character
            self._settings.local_settings.min_password_upper_letter = min_password_upper_letter
            self._settings.local_settings.max_unsuccessful_login_attempts = max_unsuccessful_login_attempts
            self._settings.local_settings.min_password_lower_letter = min_password_lower_letter
            self._settings.local_settings.max_password_lifetime_days = max_password_lifetime_days
            self._settings.local_settings.min_password_numeric_character = min_password_numeric_character
            self._update()


        def radius_settings(self):
            self._get()
            return self._settings.radius_settings

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
            self._get()
            self._settings.radius_settings.servers = servers
            self._settings.radius_settings.client_port = client_port
            self._settings.radius_settings.encryption_protocol = encryption_protocol
            self._settings.radius_settings.accounting_enabled = accounting_enabled
            self._update()

        def tacacs_settings(self):
            self._get()
            return self._settings.tacacs_settings

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
            
            self._get()
            self._settings.tacacs_settings.servers = servers
            self._settings.tacacs_settings.accounting_terminator = accounting_terminator
            self._settings.tacacs_settings.accounting_enabled = accounting_enabled
            self._settings.tacacs_settings.accounting_value = accounting_value
            self._settings.tacacs_settings.authorization_value = authorization_value
            self._settings.tacacs_settings.client_port = client_port
            self._settings.tacacs_settings.authorization_response_attribute = authorization_response_attribute
            self._settings.tacacs_settings.authorization_attribute = authorization_attribute
            self._settings.tacacs_settings.accounting_attribute = accounting_attribute
            self._update()

        def auth_sequence(self):
            self._get()
            return self._settings.auth_sequence

        def set_auth_sequence(self, modes):
            self._get()
            self._settings.auth_sequence = modes
            self._update()

        def remote_auth_settings(self):
            self._get()
            return self._settings.remote_auth_settings

        def set_remote_auth_settings(self, fallback_on_unavailable_only, default_group=""):
            self._get()
            self._settings.remote_auth_settings.fallback_on_unavailable_only = fallback_on_unavailable_only
            self._settings.remote_auth_settings.default_group = default_group
            self._update()

        def webui_settings(self):
            self._get()
            return self._settings.webui_settings

        def set_webui_settings(self, login_banner="", need_purpose=False, session_duration=60):
            self._get()
            self._settings.webui_settings.login_banner = login_banner
            self._settings.webui_settings.need_purpose = need_purpose
            self._settings.webui_settings.session_duration = session_duration
            self._update()

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
            self.update_immediately = True

        def _get(self):
            if self.categories is None:
                self.categories = {}
                settings = self.shark.api.settings.get_audit()
                for c in settings.audit_categories:
                    self.categories[c.audit_type] = c
                
        def update(self):
            '''Force apply any setting changes'''
            self._update(force=True)
            
        def _update(self, force=False):
            if force or self.update_immediately:
                self.shark.api.settings.update_audit({'audit_categories' : self.categories.values()})

        def get_category_settings(self, category):
            '''Return a reference to the current settings for the given category.'''
            self._get()
            return self.categories[category]

        def update_category_settings(self, category, min_syslog_level, min_remote_server_level):
            '''Return a reference to the current settings for the given category.'''
            self._get()
            self.categories[category].min_syslog_level = min_syslog_level
            self.categories[category].min_remote_server_level = min_remote_server_level
            self._update()

        def get_category_descriptions(self):
            '''Return a list of (category, description) pairs containing
            the description for each audit category.'''
            self._get()
            return [(c.audit_type, c.description) for c in self.categories.values()]

        def get_syslog_levels(self):
            '''Return a list of (category, level) pairs containing the
            currently enabled syslog level for each audit category.'''
            self._get()
            return [(c.audit_type, c.min_syslog_level) for c in self.categories.values()]

        def update_syslog_levels(self, levels):
            '''Given a list of (category, level) pairs, updates the min
            syslog levels for each of the given categories.'''
            self._get()
            for category, level in levels:
                self.categories[category].min_syslog_level = level
            self._update()

        def update_all_syslog_levels(self, level):
            '''Update the syslog level for all categories to the given level'''
            self._get()
            for c in self.categories:
                c.min_syslog_level = level
            self._update()
                    
        def get_remote_server_levels(self):
            '''Return a list of (category, level) pairs containing the
            currently enabled remote_server level for each audit category.'''
            self._get()
            return [(c.audit_type, c.min_remote_server_level) for c in self.categories.values()]

        def update_remote_server_levels(self, levels):
            '''Given a list of (category, level) pairs, updates the min
            remote_server levels for each of the given categories.'''
            self._get()
            for category, level in levels:
                self.categories[category].min_remote_server_level = level
            self._update()

        def update_all_remote_server_levels(self, level):
            '''Update the remote_server level for all categories to the given level'''
            self._get()
            for c in self.categories:
                c.min_remote_server_level = level
            self._update()
                    
    class Licenses:
        '''Wrapper class around license configuration'''
        def __init__(self, shark):
            self.shark = shark

        def get_all(self):
            return [lic.key for lic in self.shark.api.licenses.get_all()]

        def add(self, license_keys):
            self.shark.api.licenses.add_license(license_keys)

        def remove(self, key):
            self.shark.api.licenses.delete_license(key)
    
        def clear(self):
            for lic in self.get_all():
                self.shark.api.licenses.delete_license(lic)

        def status(self):
            return self.shark.api.licenses.get_status()


    class Firewall:
        ''' Allows to get the current configuration of the firewall and 
        set a new one.'''

        def __init__(self, shark):
            self.shark = shark
            self._firewall_config = None
            self.update_immediately = True

        def firewall_settings(self):
            self._get(force=True)
            return self._firewall_config
 
        def _get(self, force=False):
            if force or self._firewall_config is None:
                config_dict = self.shark.api.settings.get_firewall_config()
                self._firewall_config = self.FirewallConfig(config_dict["firewall_enabled"],
                                                       config_dict["default_policy"],
                                                       config_dict["rules"])

        def update(self):
            '''Force apply any setting changes'''
            self._update(force=True)

        def _update(self, force=False):
            if force or self.update_immediately:
                config_dict = {"firewall_enabled": self._firewall_config.enabled,
                               "default_policy" :self._firewall_config.default_policy,
                               "rules" :self._firewall_config.rules
                               }
                self.shark.api.settings.update_firewall_config(config_dict)
                self._get(force=True)

        def set_firewall_settings(self, firewall_config):
            '''
            Update the firewall configuration

            firewall_config: the new configuration to set
            '''
            self._get()
            self._firewall_config = firewall_config
            self._update()


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
    
        def get_certificates_config(self):
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
            self.update_immediately = True

        def _get(self, force=False):
            if force or self._settings is None:
                self._settings = self.shark.api.settings.get_profiler_export()

        def update(self):
            '''Force apply any setting changes'''
            self._update(force=True)
            
        def _update(self, force=False):
            if force or self.update_immediately:
                self.shark.api.settings.update_profiler_export(self._settings)

        def enabled(self):
            """Return whether or not profiler export is enabled"""
            self._get()
            return self._settings.enabled
        
        def enable(self):
            """Enable profiler export"""
            self._get()
            self._settings.enabled = True
            self._update()
            
        def disable(self):
            """Disable profiler export"""
            self._get()
            self._settings.enabled = False
            self._update()
            
        def get_profilers(self):
            """Return a list of (address, status) pairs for all enabled profilers."""
            self._get()
            return [(p.address, p.status) for p in self._settings.profilers]

        def add_profiler(self, address):
            self._get()
            if len(self._settings.profilers) == 2:
                raise ValueError("Only two profilers can be enabled")
            self._settings.profilers.append({'address' : address})
            self._update()
            self._get(force=True)
        
        def remove_profiler(self, address):
            self._get()
            for p in self._settings.profilers:
                if p.address == address:
                    self._settings.profilers.remove(p)
                    # Check if there is no Profiler set
                    if len(self._settings.profilers) == 0:
                        # If no profiler is available Profiler Export should be disabled 
                        self._settings.enabled = False
                    self._update()
                    return
            raise ValueError("No profiler enabled with address %s" % address)

        def remove_all_profilers(self):
            self._get()
            self._settings.profilers = []
            self._settings.enabled = False
            self._update()

        def enabled_ports(self):
            """Return a list of all ports for which profiler export is enabled."""
            self._get()
            return [port.name for port in self._settings.adapter_ports if port.enabled]

        def disabled_ports(self):
            """Return a list of all ports for which profiler export is not enabled."""
            self._get()
            return [port.name for port in self._settings.adapter_ports if not port.enabled]

        def enable_port(self, name, bpf_filter=None, voip_enabled=None):
            """Enable the given port for profiler export, optionally
            setting the given BPF filter and whether or not voip
            metrics should be enabled."""
            self._get()
            for port in self._settings.adapter_ports:
                if port.name == name:
                    port.enabled = True
                    if bpf_filter is not None:
                        port.BPF_filter = bpf_filter
                    if voip_enabled is not None:
                        port.VoIP_enabled = voip_enabled
                    self._update()
                    return

            raise ValueError("Invalid port " + port)
            
        def disable_port(self, name):
            self._get()
            for port in self._settings.adapter_ports:
                if port.name == name:
                    port.enabled = False
                    self._update()
                    return
            raise ValueError("Invalid port " + port)

        def get_port_config(self, name):
            self._get()
            for port in self._settings.adapter_ports:
                if port.name == name:
                    return port
            raise ValueError("No such port %s" % port)
            
    def get_cors_domains(self):
        '''Return the list of allowed domains for cross-origin
        resource access.'''
        return self.shark.api.settings.get_cors_domains()

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


        

