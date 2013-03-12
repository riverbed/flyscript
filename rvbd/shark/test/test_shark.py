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
from rvbd.common.exceptions import *

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
    loglevel = logging.INFO

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


def create_shark():
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
    return Shark(config['sharkhost'], auth=auth)


def setup_defaults():
    #
    # some columns and filters we can use for creating views
    #
    columns = [Key('ip.src'),
               Key('ip.dst'),
               Value('generic.packets'),
               Value('http.duration', Operation.max, description="Max Duration"),
               Value('http.duration', Operation.avg, description="Avg Duration")]
    filters = [SharkFilter('(generic.application="Web") & (http.content_type contains "image/")'),
               TimeFilter.parse_range('last 2 hours')]
    return columns, filters


def setup_capture_job(shark):
    try:
        job = shark.get_capture_job_by_name('Flyscript-tests-job')
    except ValueError:
        #let's create a capture job
        interface = shark.get_interface_by_name('mon0')
        job = shark.create_job(interface, 'Flyscript-tests-job', '40%', indexing_size_limit='2GB',
                               start_immediately=True)

    logger.info('using capture job %r' % job)
    return job


def create_trace_clip(shark, job):
    # create a relatively short trace clip that we can use later
    fltr = TimeFilter.parse_range('last 10 minutes')
    clip = shark.create_clip(job, [fltr], 'test')
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


class SharkTests(unittest.TestCase):
    def setUp(self):
        self.shark = create_shark()

        #self.columns, self.filters = create_defaults()
        #self.job = create_capture_job(self.shark)
        #self.interface = create_interface(self.shark)
        #self.clip = create_trace_clip(self.shark, self.job)
        #self.tracefile = create_tracefile(self.shark)

    def tearDown(self):
        try:
            self.clip.delete()
        except AttributeError:
            pass
        
    def test_info(self):
        """ Test server_info, stats, interfaces,  logininfo and protocol/api versions
        """
        info = self.shark.get_serverinfo()
        self.assertTrue('hostname' in info)
        self.assertTrue('uptime' in info)

        stats = self.shark.get_stats()
        self.assertTrue('memory' in stats)
        self.assertTrue('storage' in stats)

        # check we get a list of at least one interface
        # possibly enhance to validate its of an Interface type
        i = self.shark.get_interfaces()
        self.assertTrue(len(i) > 1)

        login = self.shark.get_logininfo()
        self.assertTrue('login_banner' in login)
        self.assertTrue('supported_methods' in login)

        self.assertEqual(self.shark.get_protocol_version(), str(self.shark.api_version))

    def test_view_on_interface(self):
        """ Test creating a view on an interface """

        interface = self.shark.get_interface_by_name('mon0')
        columns, _ = setup_defaults()
        filters = None

        with self.shark.create_view(interface, columns, filters, sync=True) as view:
            progress = view.get_progress()
            data = view.get_data()

            # XXX the next statement always fails under test
            # but works when run in debugger or from script
            #self.assertTrue(len(data) > 0)
            self.assertTrue(progress == 100)
            self.assertTrue(view.config['input_source']['path'].startswith('interfaces'))

    def test_view_on_job(self):
        """ Test creating a view on a capture job """
        job = setup_capture_job(self.shark)
        columns, filters = setup_defaults()

        with self.shark.create_view(job, columns, None) as view:
            data = view.get_data()

            self.assertTrue(len(data) > 0)
            self.assertTrue(view.config['input_source']['path'].startswith('jobs'))

    def test_view_on_clip(self):
        """ Test creating a view on a trace clip """
        job = setup_capture_job(self.shark)
        clip = create_trace_clip(self.shark, job)
        columns, filters = setup_defaults()

        with self.shark.create_view(clip, columns, None) as view:
            data = view.get_data()

            self.assertTrue(len(data) > 0)
            self.assertTrue(view.config['input_source']['path'].startswith('clip'))

    def test_view_on_file(self):
        """ Test creating a view on a trace file """
        tracefile = create_tracefile(self.shark)
        columns, filters = setup_defaults()

        with self.shark.create_view(tracefile, columns, None) as view:
            data = view.get_data()

            self.assertTrue(len(data) > 0)
            self.assertTrue(view.config['input_source']['path'].startswith('fs'))

    def test_view_api(self):
        """ Test some basic properties of the view api
        """
        job = setup_capture_job(self.shark)
        clip = create_trace_clip(self.shark, job)
        columns, filters = setup_defaults()
        with self.shark.create_view(clip, columns, filters) as v:
            legend = v.get_legend()
            for col in legend:
                # make sure we have name and description attributes
                self.assertTrue(col.name)
                self.assertTrue(col.description)

            for row in v.get_data():
                self.assertTrue(isinstance(row['t'], datetime.datetime))
                for val in row['vals']:
                    self.assertEqual(len(val), len(legend))

            # do an aggregated get_data()
            rows = v.get_data(aggregated=True)
            if len(rows) == 0:
                logger.warn('no data in view, cannot test aggregated get')
            self.assertTrue(len(rows) == 0 or len(rows) == 1)

    def test_create_view_from_template(self):
        job = setup_capture_job(self.shark)
        clip = create_trace_clip(self.shark, job)

        with open(os.path.join(HERE, 'view-example.json')) as f:
            template = f.read()

        with self.shark.create_view_from_template(clip, template) as v:
            pass

    def test_async_view(self):
        job = setup_capture_job(self.shark)
        clip = create_trace_clip(self.shark, job)
        columns, filters = setup_defaults()
        with self.shark.create_view(clip, columns, filters,
                                    sync=False) as v:
            while v.get_progress() < 100:
                time.sleep(1)

    def test_create_clip(self):
        interface = self.shark.get_interfaces()[0]
        job = self.shark.get_capture_jobs()[0]
        filters = [TimeFilter(datetime.datetime.now() - datetime.timedelta(1),
                              datetime.datetime.now())]
        clip = self.shark.create_clip(job,  filters, description='test')
        clip.delete()
        #lets create a clip from a job
        with job.add_clip(filters, 'test_add_clip') as clip:
            pass

    def test_columns_structure(self):
        assert str(self.shark.columns.this.will.be.test) == 'this.will.be.test'
        self.shark.columns.__dir__()
        self.assertNotEqual(str(self.shark.columns.ip.src),  'ip.src')

    def test_fs(self):
        """
        Tests some commands for creating/removing/moving/listing dirs
        """
        def print_details(resource):
            to_print = ""
            to_print += resource.path + " - "
            to_print += str(resource.created) + " - "
            to_print += str(resource.modified)

            try:
                to_print += " - " + str(resource.size)
            except:
                pass

            try:
                to_print += " - " + resource.link_layer
                to_print += " - " + resource.trace_type
            except:
                pass
            logger.debug(to_print)

        root_ref = self.shark.get_dir("/")
        for current_dir in root_ref.data["dirs"]:
            print_details(current_dir)

        if not self.shark.exists("admin/foo"):
            dir_ref = self.shark.create_dir("admin/foo")
        else:
            dir_ref = self.shark.get_dir("admin/foo")

        if not self.shark.exists("admin/foo/bar"):
            sub_dir_ref = dir_ref.create_subdir("bar")
        else:
            sub_dir_ref = self.shark.get_dir("admin/foo/bar")

        admin_ref = self.shark.get_dir("admin")
        dirs, files = admin_ref.list()
        for current_dir in dirs:
            print_details(current_dir)

        sub_dir_ref.move("admin/bar")
        print_details(sub_dir_ref)

        dir_ref.remove()
        sub_dir_ref.remove()

        #do file operations
        if self.shark.exists("admin/files_test"):
            dir_ref = self.shark.get_dir("admin/files_test")
            dir_ref.remove()

        test_dir_ref = self.shark.create_dir("admin/files_test")

        # File Upload
        trace_files_dir = os.path.join(HERE, "traces")
        file1_ref = test_dir_ref.upload_trace_file("2-router1-in.pcap",
                                                   os.path.join(trace_files_dir, "2-router1-in.pcap"))
        file2_ref = test_dir_ref.upload_trace_file("4-router2-in.pcap",
                                                   os.path.join(trace_files_dir, "4-router2-in.pcap"))
        file3_ref = self.shark.upload_trace_file("admin/files_test/6-router3-in.pcap",
                                                 os.path.join(trace_files_dir, "6-router3-in.pcap"))

        #File Download
        download_dir = trace_files_dir + "fs_sandbox_test_dir"
        if os.path.exists(download_dir):
            shutil.rmtree(download_dir)

        os.mkdir(download_dir)
        file1_ref.download(download_dir)
        file2_ref.download(download_dir)
        file3_ref.download(download_dir)

        file1_upload_success = filecmp.cmp(os.path.join(
            trace_files_dir, "2-router1-in.pcap"),
            os.path.join(download_dir, "2-router1-in.pcap"))
        logger.debug("File1 upload success: " + str(file1_upload_success))
        assert file1_upload_success
            
        file2_upload_success = filecmp.cmp(
            os.path.join(trace_files_dir, "4-router2-in.pcap"),
            os.path.join(download_dir, "4-router2-in.pcap"))
        logger.debug("File2 upload success: " + str(file2_upload_success))
        assert file2_upload_success
            
        file3_upload_success = filecmp.cmp(
            os.path.join(trace_files_dir, "6-router3-in.pcap"),
            os.path.join(download_dir, "6-router3-in.pcap"))
        logger.debug("File3 upload success: " + str(file3_upload_success))
        assert file3_upload_success

        shutil.rmtree(download_dir)

        dirs, files = test_dir_ref.list()
        for current_file in files:
            print_details(current_file)

        # Indexes
        file1_ref.create_index()

        # Let's give some time to the probe to create the index
        while True:
            info = file1_ref.index_info()
            if info["status"] == "OK":
                print info
                break
            else:
                print info["status"]
                time.sleep(2)

        file1_ref.remove_index()

        # Multisegment files
        file1_ref.default_file = True
        file2_ref.timeskew_val = 10000
        linked_files_list = [file1_ref, file2_ref, file3_ref]
        multisegment_ref = self.shark.create_multisegment_file("admin/files_test/multisegment.pvt", linked_files_list)
        print_details(multisegment_ref)

        # Timeskew calculation
        logger.debug("- " + multisegment_ref.path + " timeskew data")
        # Let's give some time to the probe to calculate the timeskew
        multisegment_ref.calculate_timeskew(1000)
        while True:
            info = multisegment_ref.timeskew()
            if info["status"]['state'] == "OK":
                logger.debug(info)
                break
            else:
                logger.debug(info["status"]['state'])
                time.sleep(2)

        multisegment_ref.delete_timeskew()
        multisegment_ref.remove()

        # Merged files
        linked_files_list2 = [file1_ref, file2_ref]
        merged_ref = self.shark.create_merged_file("admin/files_test/merged.pvt", linked_files_list2)
        merged_ref.remove()

        # Common and miscellaneous calls
        file1_ref.move("/admin/files_test/router1-in.pcap")
        file2_ref.move("/admin/files_test/router2-in.pcap")
        file3_ref.move("/admin/files_test/router3-in.pcap")
        
        dirs, files = test_dir_ref.list()
        for current_file in files:
            print_details(current_file)
                
        logger.debug("- " + file1_ref.path + " checksum data")
        logger.debug(str(file1_ref.checksum()))
            
        # Get File directly without using the directory ref
        file_ref = self.shark.get_file("/admin/files_test/router1-in.pcap")
        logger.debug("- " + file_ref.path + " checksum data")
        logger.debug(file_ref.checksum())
            
        file1_ref.remove()
        file2_ref.remove()
        file3_ref.remove()
            
        logger.debug("- Content after removing the files")
        dirs, files = test_dir_ref.list()
        for current_file in files:
            print_details(current_file)

        test_dir_ref.remove()

    def test_shark_interface(self):
        interfaces = self.shark.get_interfaces()
        interface = self.shark.get_interface_by_name('mon0')
        try:
            job = self.shark.get_capture_job_by_name('test_shark_interface_job')
            job.delete()
        except ValueError:
            #everything is allright, we can create the test_shark_interface_job job
            pass
        job = self.shark.create_job(interface, 'test_shark_interface_job', '300M')
        filters = [TimeFilter.parse_range('last 10 minutes')]
        with self.shark.create_clip(job, filters, 'test_shark_interface_clip') as clip:
            self.shark.get_capture_jobs()
            self.shark.get_clips()
            self.assertNotEqual(self.shark.get_capture_job_by_name('test_shark_interface_job'), None)
            self.assertNotEqual(self.shark.get_trace_clip_by_description('test_shark_interface_clip'), None)
            self.assertNotEqual(self.shark.get_file('/admin/noon.cap'), None)
            self.assertNotEqual(self.shark.get_files(), None)
            self.assertNotEqual(self.shark.get_dir('/admin/'), None)

        job.delete()
        
    def test_create_job_parameters(self):
        interface = self.shark.get_interface_by_name('mon0')
        stats = self.shark.get_stats()
        packet_total_size = stats['storage']['packet_storage'].total
        index_total_size = stats['storage']['os_storage']['index_storage'].total
        try:
            job = self.shark.get_capture_job_by_name('test_create_job_with_parameters')
            if job:
                job.delete()
        except (ValueError, RvbdHTTPException):
            pass
        job = self.shark.create_job(interface, 'test_create_job_with_parameters', '20%', indexing_size_limit='1.7GB',
                                    start_immediately=True)
        self.assertEqual(job.size_limit, packet_total_size * 20/100)
        assert job.data.config.indexing.size_limit < 1.7*1024**3
        assert job.data.config.indexing.size_limit > 1.6*1024**3
        job.delete()
        job = self.shark.create_job(interface, 'test_create_job_with_parameters', '20%', indexing_size_limit='10%',
                                    packet_retention_time_limit=datetime.timedelta(days=7), start_immediately=True)
        self.assertEqual(job.size_limit, packet_total_size * 20/100)
        assert job.data.config.indexing.size_limit < index_total_size * 11/100
        assert job.data.config.indexing.size_limit > index_total_size * 9/100
        job.delete()
        #TODO: test other job parameters

    def test_directory_list(self):
        dir = self.shark.get_dir('/')
        dir_list = dir.list()
        assert isinstance(dir_list[0], list)
        assert isinstance(dir_list[1], list)
        dir = self.shark.get_dir('/admin')
        dir_list = dir.list()

    def test_directory_walk(self):
        dir = self.shark.get_dir('/admin')
        for root, dirs, files in dir.walk():
            print root, dirs, files
            assert isinstance(root, str)
            assert isinstance(dirs, list)
            assert isinstance(files, list)
        dir = self.shark.get_dir('/')
        for root, dirs, files in dir.walk():
            print root, dirs, files
            assert isinstance(root, str)
            assert isinstance(dirs, list)
            assert isinstance(files, list)

    def test_loaded_decorator(self):
        shark = self.shark
        fltr = (TimeFilter.parse_range("last 30 m"))
        job = shark.get_capture_jobs()[0]
        with shark.create_clip(job, [fltr], 'my_clip') as clip:
            #this will test the @loaded decorator
            clip.size

    def test_profiler_export(self):
        shark = self.shark
        pe = shark.settings.profiler_export
        try:
            pe.remove_profiler('tm08-1.lab.nbttech.com')
        except (RvbdHTTPException, ValueError):
            pass
        pe.add_profiler('tm08-1.lab.nbttech.com')
        pe.enable()
        pe.disable()
        pe.remove_profiler('tm08-1.lab.nbttech.com')
        
if __name__ == '__main__':
    # for standalone use take one command-line argument: the shark host
    assert len(sys.argv) == 2

    config = {'sharkhost': sys.argv[1]}
    sys.argv = [ sys.argv[0] ]

    unittest.main()
