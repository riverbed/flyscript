# Copyright (c) 2013 Riverbed Technology, Inc.
#
# This software is licensed under the terms and conditions of the
# MIT License set forth at:
#   https://github.com/riverbed/flyscript/blob/master/LICENSE ("License").
# This software is distributed "AS IS" as set forth in the License.

from common import *
import testscenarios
from functools import partial


class EqualityTest(object):
    def _equality_test(self, saved, settings):
        settings.save()
        self.assertNotEqual(saved, settings.get())
        settings.load(saved)
        settings.save()
        self.assertEqual(saved, settings.get())


class Settings(EqualityTest, SetUpTearDownMixin, testscenarios.TestWithScenarios):
    scenarios = config.get('4.0') + config.get('5.0')

    def test_basic(self):
        basic = self.shark.settings.basic
        basic.get()
        basic.data['hostname'] = 'shark'
        basic.data['domain'] = 'local'
        basic.data['primary_dns'] = '127.0.0.1'
        basic.data['secondary_dns'] = '8.8.8.8'
        basic.data['ssh_enabled'] = True
        basic.data['fips_enabled'] = True
        basic.save()
        saved = basic.get()
        basic.data['hostname'] = 'flyscripttest'
        basic.data['domain'] = 'flyscripttestdomain'
        basic.data['primary_dns'] = '10.0.0.1'
        basic.data['secondary_dns'] = '10.0.0.2'
        basic.data['ssh_enabled'] = True
        basic.data['fips_enabled'] = False
        basic.data['timezone']
        basic.data['ntp_config']
        self._equality_test(saved, basic)

    def test_auth(self):
        auth = self.shark.settings.auth
        auth.get()
        auth.data['local_settings']['min_password_length'] = 0
        auth.data['local_settings']['password_change_history'] = 0
        auth.auth_sequence = ['LOCAL']
        auth.save()
        saved = auth.get()
        auth.data['local_settings']['min_password_length'] = 1
        self._equality_test(saved, auth)

    def test_users(self):
        users = self.shark.settings.users
        saved = users.get()
        try:
            users.delete('flyscripttestuser')
        except:
            #all good we came from a failure of this test from
            #the past
            pass

        users.add('flyscripttestuser', 'test', ['Administrators'])
        users.save()

        #check that user is in the system
        flag = False
        for user in users.data:
            if user['name'] == 'flyscripttestuser':
                flag = True
                break
        self.assertEqual(flag, True)

        users.change_password('flyscripttestuser', 'test1234')
        users.delete('flyscripttestuser')
        users.save()

    def test_groups(self):
        groups = self.shark.settings.groups
        saved = groups.get()

        try:
            groups.delete('flyscriptgroup')
        except:
            #all good we came from a failure of this test from
            #the past
            pass

        groups.add('flyscriptgroup', 'test', ['CAPABILITY_ADMINISTRATOR'])
        groups.save()

        #check that user is in the system
        flag = False
        for group in groups.data:
            if group['name'] == 'flyscriptgroup':
                flag = True
                break
        self.assertEqual(flag, True)

        groups.delete('flyscriptgroup')
        groups.save()

    def test_audit(self):
        audit = self.shark.settings.audit
        audit.get()
        for category in audit.data['audit_categories']:
            print category['min_remote_server_level']
            print category['audit_type']
            print category['min_syslog_level']
            print category['description']
            print category['name']
        audit.data['audit_categories'][0]['name'] = 'test'
        audit.save()
        saved = audit.get()
        audit.data['audit_categories'][0]['name'] = 'AUTHENTICATION'
        self._equality_test(saved, audit)

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
        firewall = self.shark.settings.firewall
        saved = firewall.get()
        firewall.data['firewall_enabled'] = False
        for rule in firewall.data['rules']:
            print rule
        #action can be ACCEPT, DROP, LOG_ACCEPT, LOG_DROP
        #protocol can be ALL, TCP, UDP, ICMP
        firewall.data['rules'].append({
                'action': 'ACCEPT',
                'protocol': 'TCP',
                'description': 'flyscript test',
                'dest_port': 12345})
        firewall.data['rules'].append({
                'action': 'DROP',
                'protocol': 'UDP',
                'description': 'flyscript test',
                'dest_port': 12345})
        firewall.data['rules'].append({
                'action': 'LOG_DROP',
                'protocol': 'TCP',
                'description': 'flyscript test',
                'dest_port': 12367})
        self._equality_test(saved, firewall)

    def test_certificates(self):
        certificates = self.shark.settings.certificates
        default_profiler_pem = '''-----BEGIN CERTIFICATE-----
MIIBsTCCARqgAwIBAgIJAOqvgxZRcO+ZMA0GCSqGSIb3DQEBBAUAMA8xDTALBgNV
BAMTBE1henUwHhcNMDYxMDAyMTY0MzQxWhcNMTYwOTI5MTY0MzQxWjAPMQ0wCwYD
VQQDEwRNYXp1MIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQC0e+f4pJY2eSm1
8U579OKJIyxc/sdKXlLOw0zK6SoNu7XNHmNoObNhQV+3PoSbZNyqW3GuZ54EEKUw
G54kDzHu9cZMGEWvNO6syjZZlfBORpklQoNEsNxAkbhTr9DXfloFKiLouDl8E7jB
hMkbKxnpNcfcl+NEuQ8av2QQWp3jfQIDAQABoxUwEzARBglghkgBhvhCAQEEBAMC
BkAwDQYJKoZIhvcNAQEEBQADgYEATnoqJSym+wATLxgb2Ujdy4CY0gawUXHjidaE
ehyejGdw6VhXpf4lP9Q8JfVERjCoroVkiXenVQe/zer7Qf2hiDB/5s02/+8uiEeq
MJpzsSdEYZUSgpyAcws5PDyr2GVFMI3dfPnl28hVavIkR8r05BPDxKbb8Ic6HWpT
CTDPH3w=
-----END CERTIFICATE-----'''
# generated with:
# openssl req -newkey rsa:2048 -new -nodes -x509 -days 3650 \
# -keyout key.pem -out cert.pem
        pem_cert = '''-----BEGIN PRIVATE KEY-----
MIIEvwIBADANBgkqhkiG9w0BAQEFAASCBKkwggSlAgEAAoIBAQDKzwB0jOUITvdn
x5gHYYeRGvSktYtioWyGTnInZmCfmhhlv1G9tIc5BLdXvy3K5I76437HlVRfahkH
yPpxFukv7e2GPb8I8iAAw8ne/EvrSeE/eQZQs1tLFvAyQxxZvS2sEPSEiaAzhSLN
49MYkKOa0cdnQFtoIk2jxLjuXpOs2VFQwmgRbCNUANZg75gD6B2lQDbKAyTEpG4r
4S0AEH/ybuyhCbErFfjgIzlg1gt6DU6Gx19l8XjZYJKXbidC9dxSGvvbKppV3e+A
7ISxK6/qnSBwlBN3V/6dSAYy6iV+3KekuByheSX+ixIjF85PvY8LhY0q0Xj6oCBe
3iPf28/pAgMBAAECggEBAKAGtlVA13e214EL/OnWCyJ0IpXUqicpOHjBbVGpdpR5
AsdGLzmBOTHEhua182wk7K0K1P6m1exzy0xZSUPy0A0BsGo8ToDAjIAN/Tv11/HQ
Weu7k0AaRe76Ko1+ZuBoZaFfv5DVB5Ofedb77ZV0i6Od47mVDoschiazEzkDZ4L6
j5KebQtGqye7ch5cKq3WUR+k2/VNv+N1X1pQGtmsMtP1QPj5xYgealtdsoXA/9gU
GeLSMLCQ4rEjjDV/Fr6Ee6dS3i3kETpRN7G+ufjtO9Xm+/2m50xukKDAuU2hvs+C
H2EE12Q9HcCkc0GQmnUBO8fLPvlIGlo6SiJC3DA2oAECgYEA5oGabRmJROHEdVOm
UadyyTQKx/ANObhCZxDeI2c1cabP6daEzpuJCqMdyUvEvdgBRtf3LbZFbXXc/AQI
MopbmyNY+ytvg4PganBU7FpvwPmVkBY9n9stf+/Q3FLknwifQicBygKuFs8MNPl1
ynDYQFSlRJvqBUCdoobmVkXZKK0CgYEA4T0vlgJnCP0iRVwbSh0WSRYCwv/GIUzA
vxtpHGZxzktsNtbmyxsYZ0yBkSyTLTEn+w32HgdtN2sWS1zY574rtY9R0ShuvLCN
bjz++4xmwuLqpMP8mvW4m8ASmVQqN1OzV7F+R/YjIPBvZimdH7lfXO1WHH8HCbwg
F//TDu7T/60CgYAXFG8D8YSfEwP6w29pyZxirQVPU6ffWaW8cCHt5Y2iXZN/1Gzj
ywsDt6Vp3F5Mq+4ky8cCGrgE58JCsZyogtX9SKLGM2ks/+1eevTl3YBHEDZ7gN6W
vPlnT/nXta0Sh2h61TEGqxIHUp/kRf4XUQk2F8OchQf/kqK1/U/e34uI2QKBgQCg
aCPIkGNymlvay5K/wGFLoXpMBz3CH1gxgcLkr+yiv0IM+BUbVmuVvX2UtwsFpzlS
6Ql7L0zPp9sTxsbOm7ejMLNS4pmilZXTiWsKGF5ispnqx4zRiudzPGHCgpciGeDi
Ngy6EQfJgJHFTyOQIUNR+dBWsPyBKVIt5UoZG2stbQKBgQCKD1rkIcCs1fVJAOAC
BKQLLx7oi+75LUQNNPXdnV+CWLdxZcZGiEP9tIOT6F6cjoSR5F5rj+GpxsKwLRuC
SHYxmV55aV6BvLl8qPHbkAVkctpcVprGZv3KUa6z4rQAOtkrI/HChSFMqPwVdvfK
Vmpm+ktH79qTy/+/RbpBCBeUPg==
-----END PRIVATE KEY-----
-----BEGIN CERTIFICATE-----
MIIDczCCAlugAwIBAgIJALKq8pCt1HYEMA0GCSqGSIb3DQEBBQUAMFAxCzAJBgNV
BAYTAlVTMQswCQYDVQQIDAJDQTEWMBQGA1UEBwwNU2FuIEZyYW5jaXNjbzEcMBoG
A1UECgwTUml2ZXJiZWQgVGVjaG5vbG9neTAeFw0xMzA5MjYwMDIxMTVaFw0yMzA5
MjQwMDIxMTVaMFAxCzAJBgNVBAYTAlVTMQswCQYDVQQIDAJDQTEWMBQGA1UEBwwN
U2FuIEZyYW5jaXNjbzEcMBoGA1UECgwTUml2ZXJiZWQgVGVjaG5vbG9neTCCASIw
DQYJKoZIhvcNAQEBBQADggEPADCCAQoCggEBAMrPAHSM5QhO92fHmAdhh5Ea9KS1
i2KhbIZOcidmYJ+aGGW/Ub20hzkEt1e/LcrkjvrjfseVVF9qGQfI+nEW6S/t7YY9
vwjyIADDyd78S+tJ4T95BlCzW0sW8DJDHFm9LawQ9ISJoDOFIs3j0xiQo5rRx2dA
W2giTaPEuO5ek6zZUVDCaBFsI1QA1mDvmAPoHaVANsoDJMSkbivhLQAQf/Ju7KEJ
sSsV+OAjOWDWC3oNTobHX2XxeNlgkpduJ0L13FIa+9sqmlXd74DshLErr+qdIHCU
E3dX/p1IBjLqJX7cp6S4HKF5Jf6LEiMXzk+9jwuFjSrRePqgIF7eI9/bz+kCAwEA
AaNQME4wHQYDVR0OBBYEFG8e7kWhLY6jfzR3oyHXMZqqx15+MB8GA1UdIwQYMBaA
FG8e7kWhLY6jfzR3oyHXMZqqx15+MAwGA1UdEwQFMAMBAf8wDQYJKoZIhvcNAQEF
BQADggEBAGkX+VFRkzlJI3Xre/LwZp2XRN7+WcaRdUQK9JbXyIKDwfaUbRS8hhmc
MYFpCXKIe0Cov1Yk3wdp7UQswLexrMXdJjMj/vrd9OGdNYdsh5qr2Awzf/BOjfOW
EylWdyX4+Dmriaek71MM4sJpBRVeRURx1UFcNexYF1qmmvb2iKNW/1qza1cMde4i
NBv+qvPK/Ic74bIa9tMlaJw6R6D5Te19g4fBoB3eUVOlk7LH86Yo5iK2TfOmas5L
OV6q8ntDR9dSbhsfUwCgQhJhCXxMKMB0Fvnh/IhFS1KJTo0aN4soJUnShv0di3/N
UvxFJ1fRfr/EH0By7SF/K4COFhhve6M=
-----END CERTIFICATE-----
'''
        saved = certificates.get()
        certificates.set_certificate_for_web(pem_cert)
        certificates.set_certificate_for_profiler_export(pem_cert)
        certificates.use_profiler_export_certificate_for_web()
        certificates.use_web_interface_certificate_for_profiler_export()
        certificates.generate_new_certificate_for_web()
        certificates.generate_new_certificate_for_profiler_export(
            country='IT',
            email="test@test.com",
            locality='Italy',
            organization='Flyscript',
            state="CT",
            days=70)
        certificates.generate_new_certificate_for_profiler_export()
        certificates.remove_profiler_trusted_certificate('default_profiler')
        certificates.add_profiler_trusted_certificate('default_profiler',
                                                      default_profiler_pem)
        certificates.save()

    def test_cors_domain(self):
        cors = self.shark.settings.cors_domain
        saved = cors.get()
        cors.data.append('http://example_domain1.com')
        cors.data.append('http://example_domain2.com')
        cors.save()
        self._equality_test(saved, cors)

    def test_update(self):
        update = self.shark.settings.update
        saved = update.get()

        try:
            update.delete_iso()
        except:
            pass

        #Do not perfom these two because
        #they are really time and bandwidth hungry
        #update.upload_iso(open('./Downloads/update.iso'))
        # update.load_iso_from_url(
        #('http://releng.nbttech.com/cascade_west/'
        #'catamaran/shark/latest/update.iso'))

        # update.save()

        # update.delete_iso()

        #To perform update
        #update.update()

    #disabling this because it requires all jobs to be turned off
    #and will loose all the packets in jobs

    # def test_storage(self):
    #     storage = self.shark.settings.storage
    #     saved = storage.get()

    #     storage.reinitialize()

    #     #format will lose all packets
    #     storage.format()


class Settings5Specific(EqualityTest, SetUpTearDownMixin, testscenarios.TestWithScenarios):
    scenarios = config.get('5.0')

    def test_4_and_5_compatibility(self):
        self.assertRaises(NotImplementedError, self.shark.settings.get_protocol_groups)
        self.assertRaises(NotImplementedError, self.shark.settings.update_protocol_groups)
        self.assertRaises(NotImplementedError, self.shark.settings.get_protocol_names)
        self.assertRaises(NotImplementedError, self.shark.settings.update_protocol_names)

    def test_alerts(self):
        #this test will fail first time in a new shark. why?
        #because the rest api does not allow to set an empty
        #SMTP server even if SMTP alerts are not enabled
        #and the basic configuration of a newly created shark
        #has an empyt SMTP configuration. So when i try to
        #restore the configuration the REST api complains
        alerts = self.shark.settings.alerts
        saved = alerts.get()
        alerts.data['mail']['smtp_server_port'] = 25
        alerts.data['mail']['to_address'] = 'test@test.com'
        alerts.data['mail']['from_address'] = 'fromtest@test.com'
        alerts.data['mail']['smtp_server_address'] = 'smtp.test.com'
        #enable SMTP notifications
        alerts.data['notifier']['enabled'] = True
        #enable SNMP notifications
        alerts.data['notifier']['trap_notification_enabled'] = True
        alerts.data['trap']['receivers'].append({
            'community': 'public',
            'version': 'V2C',
            'address': 'trap.test.com'})
        if saved['mail']['smtp_server_address'] == '':
            saved['mail']['smtp_server_address'] = 'test@riverbed.com'
        self._equality_test(saved, alerts)

        #test snmp
        alerts.test_snmp({
            "address": "trap.riverbed.com",
            "community": "public",
            "version": "V2C"})
        #test smtp
        alerts.test_smtp(
            'notexistentsmtp.riverbed.com',
            'nonexistent@riverbed.com',
            'flyscript_test@riverbed.com')

    def test_profiler_export(self):
        profiler_export = self.shark.settings.profiler_export
        saved = profiler_export.get()
        #remove profiler if exists
        for p in profiler_export.data['profilers']:
            if p.get('address') == 'test.com':
                profiler_export.data['profilers'].remove(p)
        #add profiler
        profiler_export.data['profilers'].append({
            'address': 'test.com'
            })
        # dpi sync
        profiler_export.sync_dpi_with_profiler('test.com')
        profiler_export.save()
        #dpi unsync
        profiler_export.unsync_dpi_with_profiler('test.com')
        profiler_export.save()
        #voip_enabled and dpi_enabled for all ports
        for port in profiler_export.data['adapter_ports']:
            port['voip_enabled'] = True
            port['dpi_enabled'] = True
        profiler_export.save()
        #test checks
        self._equality_test(saved, profiler_export)

    def test_snmp(self):
        snmp = self.shark.settings.snmp
        saved = snmp.get()
        snmp.data.description = "flyscript test"
        snmp.data.enabled = True
        snmp.data.community = "public"
        snmp.data.contact = 'flyscript@test.com'
        snmp.data.version = 'V2C'
        snmp.data.location = 'first floor flyscript'
        self._equality_test(saved, snmp)


class Settings4Specific(EqualityTest, SetUpTearDownMixin, testscenarios.TestWithScenarios):
    scenarios = config.get('4.0')

    def test_alerts(self):
        """They are not supported for 4.0"""
        def will_raise_ex():
            alerts = self.shark.settings.alerts
            alerts.get()

        self.assertRaises(NotImplementedError, will_raise_ex)

    def test_snmp(self):
        """They are not supported for 4.0"""
        def will_raise_ex():
            x = self.shark.settings.snmp
            x.get()

        self.assertRaises(NotImplementedError, will_raise_ex)

    def test_profiler_export(self):
        profiler_export = self.shark.settings.profiler_export
        saved = profiler_export.get()
        #remove profiler if exists
        for p in profiler_export.data['profilers']:
            if p.get('address') == 'test.com':
                profiler_export.data['profilers'].remove(p)
        #add profiler
        profiler_export.data['profilers'].append({
            'address': 'test.com'})
        profiler_export.save()
        #voip_enabled and dpi_enabled for all ports
        for port in profiler_export.data['adapter_ports']:
            port['voip_enabled'] = True
        profiler_export.save()
        #test checks
        self._equality_test(saved, profiler_export)
