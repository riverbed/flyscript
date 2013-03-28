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
from rvbd.common.utils import Formatter

def main(app):
    headers = ['ID', 'Description', 'Type']
    data = [(f.id, f.description, f.type) for f in app.shark.get_extractor_fields()]
    Formatter.print_table(data, headers)


if __name__ == '__main__':
    SharkApp(main).run()
