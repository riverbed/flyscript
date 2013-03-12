# Copyright (c) 2013 Riverbed Technology, Inc.
#
# This software is licensed under the terms and conditions of the 
# MIT License set forth at:
#   https://github.com/riverbed/flyscript/blob/master/LICENSE ("License").  
# This software is distributed "AS IS" as set forth in the License.


import unittest
import rvbd.shark.filters as filters


class FilterTests(unittest.TestCase):
    def test_timefilter(self):
        filters.TimeFilter.parse_range('last 5 minutes')
