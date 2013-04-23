#!/usr/bin/env python

# Copyright (c) 2013 Riverbed Technology, Inc.
#
# This software is licensed under the terms and conditions of the 
# MIT License set forth at:
#   https://github.com/riverbed/flyscript/blob/master/LICENSE ("License").  
# This software is distributed "AS IS" as set forth in the License.

from rvbd.profiler.app import ProfilerApp
from rvbd.profiler.report import WANSummaryReport, WANTimeSeriesReport
from rvbd.profiler.filters import TimeFilter

import sys
import optparse

# suppress warnings from pandas 0.11
import warnings
warnings.simplefilter(action="ignore", category=FutureWarning)


class WANReportApp(ProfilerApp):

    def add_options(self, parser):
        group = optparse.OptionGroup(parser, "Device List Options")
        group.add_option('--device-address', dest='device_address', default=None,
                         help='IP address for WAN device')
        group.add_option('--device-name', dest='device_name', default=None,
                         help='Text of device name to search for (simple search only,'
                              ' no regular expressions')
        group.add_option('--lan-address', dest='lan_address', default=None,
                         help='LAN interface address')
        group.add_option('--wan-address', dest='wan_address', default=None,
                         help='WAN interface address')

        group.add_option('--summary', dest='summary', default=False, action='store_true',
                         help='Generate Summary report of WAN address')
        group.add_option('--time-series', dest='time_series', default=False, action='store_true',
                         help='Generate Time Series report of WAN address')

        group.add_option('--timefilter', dest='timefilter', default='last 1 hour', 
                         help='Time range to analyze (defaults to "last 1 hour")')

        parser.add_option_group(group)

    def validate_args(self):
        """ Ensure either wan-address or wan-device-name chosen
        """
        super(WANReportApp, self).validate_args()

        if (not self.options.device_address and 
                not self.options.device_name and
                not (self.options.lan_address and self.options.wan_address)):
            self.optparse.error('Either device-address, device-name or '
                                'both lan-address and wan-address required')
        elif not self.options.summary and not self.options.time_series:
            self.optparse.error('Either summary or time_series option required')

    def main(self):
        self.ip_address = None
        self.lan_address = None
        self.wan_address = None
        self.timefilter = TimeFilter.parse_range(self.options.timefilter)

        if self.options.wan_address and self.options.lan_address:
            self.ip_address = self.options.wan_address.split(':')[0]
            self.lan_address = self.options.lan_address
            self.wan_address = self.options.wan_address
        elif self.options.device_name:
            name = self.options.device_name
            devices = self.profiler.api.devices.get_all()
            for d in devices:
                if name.lower() in d['name'].lower():
                    self.ip_address = d['ipaddr']
                    break
            else:
                print 'Device %s cannot be found in Profiler device list' % name
                print 'Try specifying the name differently or use an IP address'
                sys.exit(1)

        if self.options.summary:
            self.columns = ['device',
                            'avg_bytes',
                            'total_bytes']
            self.groupby = 'dev'
            ReportClass = WANSummaryReport

        elif self.options.time_series:
            self.columns = ['time',
                            'avg_bytes',
                            'total_bytes']
            self.groupby = None
            ReportClass = WANTimeSeriesReport

        with ReportClass(self.profiler) as report:
            if not self.lan_address:
                # query for the interfaces
                self.lan_address, self.wan_address = report.get_interfaces(self.ip_address)

            print self.lan_address
            print self.wan_address

            # inbound
            report.run(self.lan_address, self.wan_address, 'inbound', columns=self.columns,
                       groupby=self.groupby, timefilter=self.timefilter, resolution='auto')
            inbound = report.get_data(as_list=False)

            print 'inbound'
            print inbound

            # outbound
            report.run(self.lan_address, self.wan_address, 'outbound', columns=self.columns,
                       groupby=self.groupby, timefilter=self.timefilter, resolution='auto')
            outbound = report.get_data(as_list=False)

            print 'outbound'
            print outbound

            total = inbound + outbound
            print total


if __name__ == '__main__':
    WANReportApp().run()
