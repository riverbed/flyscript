#!/usr/bin/env python

# Copyright (c) 2013 Riverbed Technology, Inc.
#
# This software is licensed under the terms and conditions of the 
# MIT License set forth at:
#   https://github.com/riverbed/flyscript/blob/master/LICENSE ("License").  
# This software is distributed "AS IS" as set forth in the License.



from rvbd.shark.app import SharkApp

class UploadPcap(SharkApp):
    def add_option(self, parser):
        parser.set_usage('%prog SHARK FILE DEST')

    def validate_args(self):
        if len(self.args) != 3:
            self.optparse.error('wrong number of arguments')
            
    def main(self):
        self.shark.upload_trace_file(self.args[2], self.args[1])


if __name__ == "__main__":
    app = UploadPcap()
    app.run()
    
