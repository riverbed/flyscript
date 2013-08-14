#!/usr/bin/env python

# Copyright (c) 2013 Riverbed Technology, Inc.
#
# This software is licensed under the terms and conditions of the 
# MIT License set forth at:
#   https://github.com/riverbed/flyscript/blob/master/LICENSE ("License").  
# This software is distributed "AS IS" as set forth in the License.


"""
This script can be used to start, stop, delete or clear a Capture Job on a
Shark Appliance.

Use the -l option to list the appliance jobs.
"""
import sys

from rvbd.shark.app import SharkApp


class ControlJob(SharkApp):
    def add_options(self, parser):
        parser.add_option('-l', action="store_true", dest="list", default=False,
                          help='print a list of available capture jobs')
        parser.add_option('-d', dest="delete", help='delete a job')
        parser.add_option('-s', dest="start", help='start a job')
        parser.add_option('-e', dest="stop", help='stop a job')
        parser.add_option('-c', dest="clear",
                          help='clear a job. This can only be done when the job is stopped.')

    def main(self):
        done = 0

        if self.options.list:
            for j in self.shark.get_capture_jobs():
                print j
            done += 1

        if self.options.delete is not None:
            job = self.shark.get_capture_job_by_name(self.options.delete)
            ans = raw_input('Are you sure you want to delete Job %s [yes/no]: ' % self.options.delete)
            if ans.lower() != 'yes':
                print 'Okay, aborting.'
                sys.exit()
            job.delete()
            print 'Job %s deleted.' % self.options.delete
            done += 1

        if self.options.start is not None:
            job = self.shark.get_capture_job_by_name(self.options.start)
            job.start()
            print 'Job %s started.' % self.options.start
            done += 1

        if self.options.stop is not None:
            job = self.shark.get_capture_job_by_name(self.options.stop)
            job.stop()
            print 'Job %s stopped.' % self.options.stop
            done += 1

        if self.options.clear is not None:
            job = self.shark.get_capture_job_by_name(self.options.clear)
            job.clear()
            done += 1

        if done == 0:
            self.optparse.error('nothing to do!')


if __name__ == '__main__':
    ControlJob().run()
