#!/usr/bin/env python

# Copyright (c) 2013 Riverbed Technology, Inc.
#
# This software is licensed under the terms and conditions of the 
# MIT License set forth at:
#   https://github.com/riverbed/flyscript/blob/master/LICENSE ("License").  
# This software is distributed "AS IS" as set forth in the License.



'''
List all the key and column fields that the given shark appliance supports.
For full field details, use the -v flag.
'''

from rvbd.shark.app import SharkApp

def main(app):
    for f in app.shark.get_extractor_fields():
        print '{0}\t{1}\t{2}'.format(f.id, f.description, f.type)

SharkApp(main).run()
