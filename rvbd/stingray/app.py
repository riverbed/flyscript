# Copyright (c) 2013 Riverbed Technology, Inc.
#
# This software is licensed under the terms and conditions of the 
# MIT License set forth at:
#   https://github.com/riverbed/flyscript/blob/master/LICENSE ("License").  
# This software is distributed "AS IS" as set forth in the License.



from rvbd.common.app import Application
from rvbd.stingray.stingraytm import StingrayTrafficManager

class StingrayTrafficManagerApp(Application):
    '''Simple class to wrap common command line parsing'''
    def __init__(self, *args, **kwargs):
        super(StingrayTrafficManagerApp, self).__init__(*args, **kwargs)
        self.optparse.set_usage('%prog STINGRAY_HOSTNAME <options>')
        self.stingray = None
        
    def parse_args(self):
        super(StingrayTrafficManagerApp, self).parse_args()
        self.host = self.args[0]

    def setup(self):
        self.stingray = StingrayTrafficManager(self.host,
                                               port=self.options.port,
                                               force_ssl=self.options.force_ssl,
                                               auth=self.auth)
        
    def validate_args(self):
        if len(self.args) < 1:
            self.optparse.error('missing STINGRAY_HOSTNAME')
