# Copyright (c) 2013 Riverbed Technology, Inc.
#
# This software is licensed under the terms and conditions of the 
# MIT License set forth at:
#   https://github.com/riverbed/flyscript/blob/master/LICENSE ("License").  
# This software is distributed "AS IS" as set forth in the License.


'''
This module contains the Connection class, which is the underlying object
for communicating with a Shark server.
'''

from __future__ import absolute_import

import logging
import xml.etree.ElementTree as ET

from rvbd.common.connection import Connection
from rvbd.shark._exceptions import SharkException

__all__ = [ 'Connection' ]

logger = logging.getLogger(__name__)

class SharkConnection(Connection):
    '''This class is the main interface to a Shark appliance.

    Upon instantiation it connects to the appliance and authenticates with
    the given credentials'''
    def __init__(self, host, port=None, force_ssl=True, pool_size=1,
                 reauthenticate_handler=None, test_resource=None):
        if port is None:
            port = [443, 61898, 80]
        Connection.__init__(self, host, port, force_ssl, pool_size=pool_size,
                            reauthenticate_handler=reauthenticate_handler,
                            test_resource=test_resource)

    def xml_request(self, urlpath, method='GET', body='', params=None,
                    extra_headers=None, check_result=True):
        tree = Connection.xml_request(self, urlpath, method, body, params,
                                      extra_headers)
       
        # XXX/demmer this needs work to handle the new API
        if check_result and tree.tag == 'TraceStats':
            result = tree.get('Result')
            if result != 'Success':
                try:
                    cause = tree.get('Cause')
                except:
                    cause = 'unknown cause'
                raise SharkException(cause)

        return tree

    def xml_request_iter(self, urlpath, method='GET', body='',
                         check_result=True, params=None):
        ''' Like xml_request(), but returns an xml iterparse object
        for incremental parsing'''
        res = self.request(urlpath, method, body, params=params)
        t = res.getheader('Content-type')
        if t != 'text/xml':
            raise SharkException('unxepected content type %s' % t)

        parser = ET.iterparse(res, events=("start", "end"))
        if check_result:
            parser = iter(parser)
            event, element = parser.next()
            if event != 'start' or element.tag != 'TraceStats':
                raise SharkException('did not get expected <TraceStats> tag')
            if element.get('Result') != 'Success':
                try:
                    cause = element.get('Cause')
                except:
                    cause = 'unknown cause'
                raise SharkException(cause)

        return parser
