# Copyright (c) 2013 Riverbed Technology, Inc.
#
# This software is licensed under the terms and conditions of the 
# MIT License set forth at:
#   https://github.com/riverbed/flyscript/blob/master/LICENSE ("License").  
# This software is distributed "AS IS" as set forth in the License.

from common import *
import testscenarios

class Dpi(SetUpTearDownMixin, testscenarios.TestWithScenarios):
    scenarios = config.get('hosts')

    def test_snmp(self):
        snmp = self.shark.settings.snmp
        snmp.get()
        snmp.save()

    def test_alerts(self):
        alerts = self.shark.settings.alerts
        alerts.get()
        alerts.save()

    def test_basic(self):
        basic = self.shark.settings.basic
        basic.get()
        basic.hostname = 'shark'
        basic.domain = 'local'
        basic.primary_dns = '127.0.0.1'
        basic.secondary_dns = '8.8.8.8'
        basic.ssh_enabled = True
        basic.fips_enabled = True
        basic.save()
        saved = basic.get()
        basic.hostname = 'flyscripttest'
        basic.domain = 'flyscripttestdomain'
        basic.primary_dns = '10.0.0.1'
        basic.secondary_dns = '10.0.0.2'
        basic.ssh_enabled = True
        basic.fips_enabled = False
        basic.timezone
        basic.ntp_config
        basic.save()
        self.assertNotEqual(saved, basic.get())
        basic.load(saved)
        basic.save()
        self.assertEqual(saved, basic.get())

    def test_auth(self):
        auth = self.shark.settings.auth
        auth.get()
        auth.local_settings.min_password_length = 0
        auth.local_settings.password_change_history = 0
        auth.auth_sequence = ['LOCAL']
        auth.save()
        saved = auth.get()
        auth.local_settings.min_password_lenght = 1
        self.assertNotEqual(saved, auth.get())
        auth.load(saved)
        auth.save()
        self.assertEqual(saved, auth.get())

    def test_audit(self):
        audit = self.shark.settings.audit
        audit.get()
        for category in audit.audit_categories:
            print category.min_remote_server_level
            print category.audit_type
            print category.min_syslog_level
            print category.description
            print category.name
        audit.audit_categories[0].name = 'test'
        audit.save()
        saved = audit.get()
        audit.audit_categories[0].name = 'AUTHENTICATION'
        self.assertNotEqual(saved, audit.get())
        audit.load(saved)
        audit.save()
        self.assertEqual(saved, audit.get())

    def test_licenses(self):
        licenses = self.shark.settings.licenses
        saved = licenses.get()
        licenses.remove(saved[0].key)
        licenses.save()
        print licenses.status()
        licenses.add(saved[0].key)
        licenses.save()
        self.assertEqual(saved, licenses.get())
        licenses.clear()
        licenses.save()
        licenses.add(saved[0].key)
        licenses.save()
        self.assertEqual(saved, licenses.get())
        
        
    def test_firewall(self):
        pass

    def test_certificates(self):
        pass

    def test_profiler_export(self):
        pass

    def test_cors_domain(self):
        pass




