#!/usr/bin/env python

# Copyright (c) 2013 Riverbed Technology, Inc.
#
# This software is licensed under the terms and conditions of the 
# MIT License set forth at:
#   https://github.com/riverbed/flyscript/blob/master/LICENSE ("License").  
# This software is distributed "AS IS" as set forth in the License.


"""
This script shows a couple of advanced options that can be used when creating
Capture Jobs.
"""

import datetime

from rvbd.shark.app import SharkApp


class JobCreator(SharkApp):
    def main(self):
        # For the sake of simplicity, we pick the first available port on the Shark
        interface = self.shark.get_interfaces()[0]

        # This creates a job that captures only web traffic (port 80), and stores
        # on disk only the first 100 bytes of each packet.
        # Capture Job filters are based on the Wireshatk capture filter syntax, a
        # reference of which can be found here:
        #   http://wiki.wireshark.org/CaptureFilters
        name = "Test Job 1"
        job = self.shark.create_job(interface,
                                    name,
                                    "257MB",
                                    bpf_filter="port 80",
                                    snap_length=100)
        print 'Job named %s created successfully ...' % name,
        job.delete()
        print 'and deleted.'

        # This creates a job that has no Microflow Index.
        # Avoiding indexing the job can be beneficial if performance is very
        # important and drill-down efficiency can be sacrificed.
        name = "Test Job 2"
        job = self.shark.create_job(interface,
                                    name,
                                    "257MB")
        print 'Job named %s created successfully ...' % name,
        job.delete()
        print 'and deleted.'

        # This creates a job in which packets and index have different retention
        # times.  The index has a much smaller disk footprint compared to packets
        # (usually around 1%), and therefore can cover longer timespans.
        # In this case, packets storage is 500MB or 1 day (whichever is smaller),
        # while index storage is 20MB or one week.
        name = "Test Job 3"
        job = self.shark.create_job(interface,
                                    name,
                                    "257MB",
                                    packet_retention_time_limit=datetime.timedelta(days=1),
                                    indexing_size_limit="25MB",
                                    indexing_time_limit=datetime.timedelta(days=7))
        print 'Job named %s created successfully ...' % name,
        job.delete()
        print 'and deleted.'

        print 'Capture Jobs created (and deleted) successfully'


if __name__ == '__main__':
    JobCreator().run()
