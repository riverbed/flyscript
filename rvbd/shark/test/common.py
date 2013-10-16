# Copyright (c) 2013 Riverbed Technology, Inc.
#
# This software is licensed under the terms and conditions of the 
# MIT License set forth at:
#   https://github.com/riverbed/flyscript/blob/master/LICENSE ("License").  
# This software is distributed "AS IS" as set forth in the License.

import rvbd.shark
from rvbd.shark import Shark
from rvbd.shark.types import Operation, Value, Key
from rvbd.shark.filters import SharkFilter, TimeFilter
from rvbd.common.service import UserAuth
from rvbd.common.exceptions import RvbdException, RvbdHTTPException
from rvbd.shark import viewutils

import rvbd.common.timeutils as T

import os
import sys
import time
import shutil
import filecmp
import logging
import unittest
import datetime

http_loglevel = 0
debug_msg_body = 0
scenario_only = False

try:
    from testconfig import config
except ImportError:
    if __name__ != '__main__':
        raise
    config = {}

# XXX we try to use unittest.SkipTest() in setUp() below but it
# isn't supported by python 2.6.  this simulates the same thing...
if 'sharkhost' not in config:
    __test__ = False


logger = logging.getLogger(__name__)
try:
    loglevel = config['loglevel']
except KeyError:
    loglevel = logging.DEBUG

logging.basicConfig(format="%(asctime)s [%(levelname)-5.5s] %(msg)s",
                    level=loglevel)
    
import rvbd.common.connection
try:
    rvbd.common.connection.Connection.HTTPLIB_DEBUGLEVEL = config['http_loglevel']
except KeyError:
    pass

try:
    rvbd.common.connection.Connection.DEBUG_MSG_BODY = config['debug_http_body']
except KeyError:
    pass
    

HERE = os.path.abspath(os.path.dirname(__file__))
trace_files_dir = os.path.join(HERE, "traces")


def create_shark(host):
    # Get our host and user credentials from testconfig
    # and create a persistent Shark object for all tests
    if 'sharkhost' not in config:
        raise unittest.SkipTest('no shark hostname provided')

    try:
        username = config['username']
    except KeyError:
        username = 'admin'
    try:
        password = config['password']
    except KeyError:
        password = 'admin'

    auth = UserAuth(username, password)
    
    try:
        port = config['sharkport']
    except KeyError:
        port = None
 
    if port:
        sk = Shark(host, port=port, auth=auth)
    else:
        sk = Shark(host, auth=auth)
    return sk


def setup_defaults():
    #
    # some columns and filters we can use for creating views
    #
    columns = [Key('ip.src'),
               Key('ip.dst'),
               Value('generic.packets'),
                Value('http.duration', Operation.max, description="Max Duration"),
                Value('http.duration', Operation.avg, description="Avg Duration")]
    # we don't 
    # have generic.application in 5.0 anymore
    filters = [SharkFilter('(tcp.src_port=80) | (tcp.dst_port=80)'),
               TimeFilter.parse_range('last 2 hours')]
    return columns, filters


def setup_capture_job(shark):
    def create_job():
        interface = shark.get_interfaces()[0]
        if shark.model == 'vShark':
            job = shark.create_job(interface, 'Flyscript-tests-job', '10%', indexing_size_limit='2GB',
                               start_immediately=True)
        else:
            job = shark.create_job(interface, 'Flyscript-tests-job', '400MB', indexing_size_limit='300MB',
                               start_immediately=True) 
            time.sleep(5)
            job.stop()
        return job

    try:
        job = shark.get_capture_job_by_name('Flyscript-tests-job')
    except ValueError:
        #let's create a capture job
        job = create_job()

    if job.size_on_disk == 0:
        #job has no packets, probably
        #the packet storage has been formatted
        #and lost all the packages
        job.delete()
        job = create_job()

    logger.info('using capture job %r' % job)
    return job


def create_trace_clip(shark, job):
    # create a relatively short trace clip that we can use later
    fltr = TimeFilter.parse_range('last 10 minutes')
    clip = shark.create_clip(job, [fltr], 'test_clip')
    logger.info('created test trace clip')
    return clip


def create_tracefile(shark):
    try:
        tracefile = shark.get_file('/admin/test.pcap')
    except rvbd.shark.RvbdHTTPException as e:
        if e.error_text.find('does not exist') == -1:
            raise

        dir = shark.get_dir(shark.auth.username)
        local_file = os.path.join(trace_files_dir, "2-router1-in.pcap")
        tracefile = dir.upload_trace_file("test.pcap", local_file)
        logger.info('uploaded test trace file')
    return tracefile


def cleanup_shark(shark):
    """Does proper cleanup of the shark appliance from views, jobs and clips

    In each case, only items named with a prefix of 'test_' are removed.
    """
    # XXX investigate implementing this at end of all tests instead of
    #     after every test

    for v in shark.api.view.get_all():
        config = shark.api.view.get_config(v['id'])
        if 'info' in config and config['info']['title'].startswith('test_'):
            shark.api.view.close(v.id)

    for j in shark.api.jobs.get_all():
        if j['config']['name'].startswith('test_'):
            shark.api.jobs.delete(j.id)

    for c in shark.api.clips.get_all():
        if c['config']['description'].startswith('test_'):
            shark.api.clips.delete(c.id)


class SetUpTearDownMixin(object):
    """Used to store the setUp and tearDown function used by
    the test classes"""
    def setUp(self):
        try:
            host = self.host
        except:
            host = config['sharkhost']
            if scenario_only:
                unittest.skip('Running only tests with scenario')
        self.shark = create_shark(host)
                
    def tearDown(self):
        cleanup_shark(self.shark)

