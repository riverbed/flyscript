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
        print snmp.version
