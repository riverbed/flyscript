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
