#!/usr/bin/env python

# Copyright (c) 2013 Riverbed Technology, Inc.
#
# This software is licensed under the terms and conditions of the 
# MIT License set forth at:
#   https://github.com/riverbed/flyscript/blob/master/LICENSE ("License").  
# This software is distributed "AS IS" as set forth in the License.


"""
This script can be used to export packets from Trace Files, Capture Jobs or 
Trace clips on a Shark Appliance. An optional IP address can be specified to 
restrict the exported packets to the ones of a single host. 

Note: in order to export a clip with this script, you need to make sure the
clip has been given a name
"""

from rvbd.shark.app import SharkApp
from rvbd.shark.filters import SharkFilter


class ExportApp(SharkApp):
    def add_options(self, parser):
        parser.add_option('--filename', dest="filename", default=None,
                            help='export a Trace File')
        parser.add_option('--jobname', dest="jobname", default=None,
                            help='export a Capture Job')
        parser.add_option('--clipname', dest="clipname", default=None,
                            help='export a Trace Clip')

    def main(self):
    
        # Do the export based on the specified object type
        if self.options.filename is not None:
            # find the file
            f = self.shark.get_file(self.options.filename)

            # extract the file name from the full path
            filename = str(f).split('/')[-1]

            # export the file
            f.download(filename)
        elif self.options.jobname is not None:
            # find the job
            job = self.shark.get_capture_job_by_name(self.options.jobname)

            job.download(job.id + '.pcap')
        elif self.options.clipname is not None:
            # find the clip
            clip = self.shark.get_trace_clip_by_description(self.options.clipname)

            # extract the clip
            clip.download(clip.id + '.pcap')
        else:
            print 'No options provided ... use "-h" to see available options.'

if __name__ == '__main__':
    ExportApp().run()
