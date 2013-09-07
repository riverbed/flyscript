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

    def test_job_dpi(self):
        job = setup_capture_job(self.shark)
        columns, filters = setup_defaults()
        job.dpi_enabled = True
        job.save()

        job2 = self.shark.get_capture_job_by_name(job.name)
        self.assertEqual(job.dpi_enabled, True)


    def test_port_definitions(self):
        pd = self.shark.settings.port_definitions
        settings = pd.get()
        self.assertNotEqual(pd._settings, None)

        try:
            pd.remove('flyscript', 65345)
        except ValueError:
            #it's all good, we don't have the rule in the server
            pass

        pd.add('flyscript', 65345, 'tcp', True)
        pd.save()

        pd.remove('flyscript', 65345)
        pd.save()

        self.assertEqual(settings, pd.get())

    def test_group_definitions(self):
        gd = self.shark.settings.port_definitions
        settings = gd.get()

        try:
            gd.remove('flyscript')
        except ValueError:
            #it's all good, no rule on server
            pass

        gd.add('flyscript', '1,2,3-80', priority=2)
        gd.save()

        gd.remove('flyscript')
        gd.save()

        self.assertEqual(settings, gd.get())
