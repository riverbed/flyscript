#!/usr/bin/env python

# Copyright (c) 2013 Riverbed Technology, Inc.
#
# This software is licensed under the terms and conditions of the 
# MIT License set forth at:
#   https://github.com/riverbed/flyscript/blob/master/LICENSE ("License").  
# This software is distributed "AS IS" as set forth in the License.


"""
This script shows how to create a Capture Job in the simplest possible way:
only the required job parameters are set, while all the optional parameters
keep their default value.
"""

from rvbd.shark.app import SharkApp
from rvbd.common.utils import bytes2human


class CreateJob(SharkApp):
    def add_options(self, parser):
        parser.add_option('-j', '--jobname', default=None, help='job name')
        parser.add_option('--capture-port', help='capture port')
        parser.add_option('-s', '--size', help='size', default=None)

    def main(self):
        # Make the user pick a name for the job
        name = self.options.jobname
        if name is None:
            name = raw_input('Job name? ')

        # Make the user pick the capture port
        try:
            ifc = self.shark.get_interface_by_name(self.options.capture_port)
        except KeyError:
            print 'Capture Ports:'
            interfaces = self.shark.get_interfaces()
            for i, ifc in enumerate(interfaces):
                print '\t{0}. {1}'.format(i+1, ifc)

            while 1:
                idx = raw_input('Port number(1-{0})? '.format(len(interfaces)))
                try:
                    ifc = interfaces[int(idx)-1]
                    break
                except IndexError:
                    print 'Bad index try again'

        # Make the user pick the job size
        size = self.options.size
        if size is None:
            stats = self.shark.get_stats()
            storage = stats['storage']['packet_storage']
            print 'Storage size is {0}, {1} available'.format(bytes2human(storage.total),
                                                              bytes2human(storage.unused))
            size = raw_input('Job size, greater than 256MB (e.g. 1.1GB, 512M, 20%)? ')

        job = self.shark.create_job(ifc, name, size)
        print 'Capture Job successfully created with the following properties:'
        print ''
        print 'ID: %s' % job.id
        print 'Current State: %s' % job.get_state()
        print 'Name: %s' % job.name
        print 'Interface: %s' % job.interface
        print 'Source Path: %s' % job.source_path
        print 'Size limit: %s' % job.size_limit
        print 'Current size on disk: %s' % job.size_on_disk
        print ''


if __name__ == '__main__':
    CreateJob().run()
