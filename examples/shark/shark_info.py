#!/usr/bin/env python

# Copyright (c) 2013 Riverbed Technology, Inc.
#
# This software is licensed under the terms and conditions of the 
# MIT License set forth at:
#   https://github.com/riverbed/flyscript/blob/master/LICENSE ("License").  
# This software is distributed "AS IS" as set forth in the License.


"""
This script connects to a Shark appliance, collects a bounch of information
about it, and prints it the screen.
"""

from rvbd.shark.app import SharkApp
from rvbd.common.utils import bytes2human


class SharkInfo(SharkApp):

    def main(self):
        # Print the high level shark info
        print 'APPLIANCE INFO:'

        info = self.shark.get_serverinfo()
        print '\tAppliance Version: ' + info['version']
        print '\tAppliance Hostname: ' + info['hostname']
        print '\tUptime: ' + str(info['uptime'])
        print '\tWeb UI TCP Port: {0}'.format(info['webui_port'])

        stats = self.shark.get_stats()
        print '\tPacket Storage: {0} total, {1} free, status:{2}'.format(
            bytes2human(stats['storage']['packet_storage'].total),
            bytes2human(stats['storage']['packet_storage'].unused),
            stats['storage']['packet_storage'].status)
        print '\tIndex Storage: {0} total, {1} free, status:{2}'.format(
            bytes2human(stats['storage']['os_storage']['index_storage'].total),
            bytes2human(stats['storage']['os_storage']['index_storage'].unused),
            stats['storage']['os_storage'].status)
        print '\tOS File System: {0} total, {1} free, status:{2}'.format(
            bytes2human(stats['storage']['os_storage']['disk_storage'].total),
            bytes2human(stats['storage']['os_storage']['disk_storage'].unused),
            stats['storage']['os_storage'].status)
        print '\tmemory: {0} total, {1} free, status:{2}'.format(
            bytes2human(stats['memory'].total),
            bytes2human(stats['memory'].available),
            stats['memory'].status)

        # Print the list of interfaces
        print 'INTERFACES:'
        for i in self.shark.get_interfaces():
            print '\t{0} (OS name: {1})'.format(i, i.name)

        # Print the list of trace files
        print 'TRACE FILES:'
        for f in self.shark.get_files():
            print '\t{0} ({1} bytes, created: {2})'.format(f, f.size, f.created)

        # Print the list of capture jobs
        print 'JOBS:'
        jobs = self.shark.get_capture_jobs()
        for j in jobs:
            print '\t{0} (size: {1}, src interface: {2})'.format(j, j.size_limit, j.interface)

        # Print the list of trace clips
        print 'TRACE CLIPS:'
        for c in self.shark.get_clips():
            if c.description == "":
                print '\t{0} ({1} bytes)'.format(c, c.size)
            else:
                print '\t{0}, {1} ({2} bytes)'.format(c.description, c, c.size)

        # Print the list of open views
        print 'OPEN VIEWS:'
        for view in self.shark.get_open_views():
            print '\t{0}'.format(view.handle)
            for output in view.all_outputs():
                print '\t\t{0}'.format(output.id)


if __name__ == '__main__':
    SharkInfo().run()
