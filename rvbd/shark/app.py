# Copyright (c) 2013 Riverbed Technology, Inc.
#
# This software is licensed under the terms and conditions of the 
# MIT License set forth at:
#   https://github.com/riverbed/flyscript/blob/master/LICENSE ("License").  
# This software is distributed "AS IS" as set forth in the License.

from rvbd.common.app import Application
import rvbd.shark


class SharkApp(Application):
    """Simple class to wrap common command line parsing"""
    def __init__(self, *args, **kwargs):
        super(SharkApp, self).__init__(*args, **kwargs)
        self.optparse.set_usage('%prog SHARK_HOSTNAME <options>')
        self.shark = None

    def parse_args(self):
        super(SharkApp, self).parse_args()
        
        self.shark = rvbd.shark.Shark(self.args[0], port=self.options.port,
                                      force_ssl=self.options.force_ssl,
                                      auth=self.auth,
                                      force_version=self.options.api_version)

    def validate_args(self):
        if len(self.args) < 1:
            self.optparse.error('missing SHARK_HOSTNAME')
