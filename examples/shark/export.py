#!/usr/bin/env python

# Copyright (c) 2013 Riverbed Technology, Inc.
#
# This software is licensed under the terms and conditions of the 
# MIT License set forth at:
#   https://github.com/riverbed/flyscript/blob/master/LICENSE ("License").  
# This software is distributed "AS IS" as set forth in the License.



'''
This script can be used to export packets from Trace Files, Capture Jobs or 
Trace clips on a Shark Appliance. An optional IP address can be specified to 
restrict the exported packets to the ones of a single host. 

Note: in order to export a clip with this script, you need to make sure the
clip has been given a name
'''

from rvbd.shark.app import SharkApp
from rvbd.shark.filters import SharkFilter


class ExportApp(SharkApp):
    def add_options(self, parser):
        parser.add_argument('--filename', dest="filename", default=None,
                            help='export a Trace File')
        parser.add_argument('--jobname', dest="jobname", default=None,
                            help='export a Capture Job')
        parser.add_argument('--clipname', dest="clipname", default=None,
                            help='export a Trace Clip')
        parser.add_argument('--filter', default=None, help='filter host')

    def main(self):
        # If the user specified a host, create the correspondent filter
        if self.options.filter is not None:
            flts = [SharkFilter('ip::ip.str="{0}"'.format(args.filter))]
        else:
            flts = None

        # Do the export based on the specified object type
        if self.options.filename is not None:
            # find the file
            file = self.shark.get_file(args.filename)

            # extract the file name from the full path
            filename = str(file).split('/')[-1]

            # export the file
            file.export(filename + '.pcap', filters=flts)
        elif self.options.jobname is not None:
            # find the job
            job = self.shark.get_capture_job_by_name(self.options.jobname)

            # extract the job
            job.export(job.description + '.pcap', filters=flts)
        elif self.options.clipname is not None:
            # find the clip
            clip = self.shark.get_trace_clip_by_description(self.options.clipname)

            # extract the clip
            clip.export(clip.description + '.pcap', filters=flts)

