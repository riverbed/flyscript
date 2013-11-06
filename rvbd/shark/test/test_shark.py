# Copyright (c) 2013 Riverbed Technology, Inc.
#
# This software is licensed under the terms and conditions of the
# MIT License set forth at:
#   https://github.com/riverbed/flyscript/blob/master/LICENSE ("License").
# This software is distributed "AS IS" as set forth in the License.

from common import *

# this enables scenarios
#need pip install testscenarios
# we need scenarios to test over multiple shark
#(vShark and Shark and maybe Shak+Profiler and Shark+Steelhead)

import testscenarios


class SharkTests(SetUpTearDownMixin, testscenarios.TestWithScenarios):
    scenarios = config.get('4.0') + config.get('5.0')

    def test_info(self):
        """ Test server_info, stats, interfaces,
        logininfo and protocol/api versions
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
        self.assertTrue(len(i) >= 1)

        login = self.shark.get_logininfo()
        self.assertTrue('login_banner' in login)
        self.assertTrue('supported_methods' in login)

        self.assertEqual(self.shark.get_protocol_version(),
                         str(self.shark.api_version))

    def test_view_on_interface(self):
        """ Test creating a view on an interface """
        try:
            interface = self.shark.get_interface_by_name('mon0')
        except KeyError:
            interface = self.shark.get_interfaces()[0]
        columns, _ = setup_defaults()
        filters = None

        with self.shark.create_view(interface,
                                    columns,
                                    filters,
                                    name='test_view_interface',
                                    sync=True) as view:
            progress = view.get_progress()
            data = view.get_data()
            ti = view.get_timeinfo()

            #self.assertTrue(ti['start'] > 0)
            #self.assertTrue(len(data) >= 0)
            self.assertTrue(progress == 100)
            self.assertTrue(
                view.config['input_source']['path'].startswith('interfaces'))

    def test_view_on_job(self):
        """ Test creating a view on a capture job """
        job = setup_capture_job(self.shark)
        columns, filters = setup_defaults()

        with self.shark.create_view(
                job,
                columns,
                None,
                name='test_view_on_job') as view:
            data = view.get_data()
            self.assertTrue(
                view.config['input_source']['path'].startswith('jobs'))

        #testing bug 111168
        #http://bugzilla.nbttech.com/show_bug.cgi?id=111168

        with self.shark.create_view(job,
                                    columns,
                                    filters,
                                    name='bug_111168') as view:
            data = view.get_data()

            self.assertTrue(
                view.config['input_source']['path'].startswith('jobs'))

        with self.shark.create_view(job, columns,
                                    [TimeFilter.parse_range('last 2 hours')],
                                    name='bug_111168_2') as view:
            data = view.get_data()

            self.assertTrue(
                view.config['input_source']['path'].startswith('jobs'))
            self.assertEqual(len(view.config['input_source']['filters']), 1)
            filter = view.config['input_source']['filters'][0]
            self.assertEqual(
                filter.start+datetime.timedelta(hours=2),
                filter.end)

    def test_view_on_clip(self):
        """ Test creating a view on a trace clip """
        job = setup_capture_job(self.shark)
        clip = create_trace_clip(self.shark, job)
        columns, filters = setup_defaults()

        with self.shark.create_view(
                clip,
                columns,
                None,
                name='test_view_on_clip') as view:
            data = view.get_data()

            self.assertTrue(len(data) >= 0)
            self.assertTrue(
                view.config['input_source']['path'].startswith('clip'))

    def test_view_on_file(self):
        """ Test creating a view on a trace file """
        tracefile = create_tracefile(self.shark)
        columns, filters = setup_defaults()

        with self.shark.create_view(
                tracefile, columns,
                None,
                name='test_view_on_file') as view:
            data = view.get_data()
            try:
                self.assertTrue(len(data) > 0)
            except:
                # this may fail in low traffic machines
                pass
            self.assertTrue(
                view.config['input_source']['path'].startswith('fs'))

    def test_view_api(self):
        """ Test some basic properties of the view api
        """
        job = setup_capture_job(self.shark)
        clip = create_trace_clip(self.shark, job)
        columns, filters = setup_defaults()
        with self.shark.create_view(
                clip,
                columns,
                filters,
                name='test_view_on_api') as v:
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
                                    sync=False, name='test_async_view') as v:
            while v.get_progress() < 100:
                time.sleep(1)

    def test_create_clip(self):
        interface = self.shark.get_interfaces()[0]
        job = self.shark.create_job(interface, 'test_create_clip', '300M')
        filters = [TimeFilter(datetime.datetime.now() - datetime.timedelta(1),
                              datetime.datetime.now())]
        clip = self.shark.create_clip(job,  filters, description='test_clip')
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
        file1_ref = test_dir_ref.upload_trace_file(
            "2-router1-in.pcap",
            os.path.join(trace_files_dir, "2-router1-in.pcap"))
        file2_ref = test_dir_ref.upload_trace_file(
            "4-router2-in.pcap",
            os.path.join(trace_files_dir, "4-router2-in.pcap"))
        file3_ref = self.shark.upload_trace_file(
            "admin/files_test/6-router3-in.pcap",
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
        multisegment_ref = self.shark.create_multisegment_file(
            "admin/files_test/multisegment.pvt", linked_files_list)
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
        merged_ref = self.shark.create_merged_file(
            "admin/files_test/merged.pvt",
            linked_files_list2)
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
        try:
            interface = self.shark.get_interface_by_name('mon0')
        except:
            interface = self.shark.get_interfaces()[0]
        try:
            job = self.shark.get_capture_job_by_name(
                'test_shark_interface_job')
            job.delete()
        except ValueError:
            #everything is allright,
            #we can create the test_shark_interface_job job
            pass
        job = self.shark.create_job(
            interface,
            'test_shark_interface_job',
            '300M')
        filters = [TimeFilter.parse_range('last 10 minutes')]
        with self.shark.create_clip(
                job,
                filters,
                'test_shark_interface_clip') as clip:
            self.shark.get_capture_jobs()
            self.shark.get_clips()
            self.assertNotEqual(
                self.shark.get_capture_job_by_name(
                    'test_shark_interface_job'), None)
            self.assertNotEqual(
                self.shark.get_trace_clip_by_description(
                    'test_shark_interface_clip'), None)
            try:
                self.assertNotEqual(
                    self.shark.get_file('/admin/noon.cap'), None)
            except RvbdHTTPException as e:
                if e.status != 404:
                    raise
            self.assertNotEqual(self.shark.get_files(), None)
            self.assertNotEqual(self.shark.get_dir('/admin/'), None)

        job.delete()

    def test_create_job_parameters(self):
        try:
            interface = self.shark.get_interface_by_name('mon0')
        except KeyError:
            interface = self.shark.get_interfaces()[0]

        stats = self.shark.get_stats()
        packet_total_size = stats['storage']['packet_storage'].total
        index_total_size = stats['storage']\
            ['os_storage']['index_storage'].total
        try:
            job = self.shark.get_capture_job_by_name(
                'test_create_job_with_parameters')
            if job:
                job.delete()
        except (ValueError, RvbdHTTPException):
            pass
        job = self.shark.create_job(
            interface, 'test_create_job_with_parameters',
            '20%', indexing_size_limit='1.7GB',
            start_immediately=True)
        self.assertEqual(job.size_limit, packet_total_size * 20/100)
        self.assertTrue(job.data.config.indexing.size_limit < 1.7*1024**3)
        self.assertTrue(job.data.config.indexing.size_limit > 1.6*1024**3)
        self.assertEqual(job.interface.name, interface.name)
        self.assertEqual(job.get_state(), 'RUNNING')
        # TODO add some equality checks to these
        self.assertTrue(job.get_stats())
        self.assertTrue(job.get_index_info())
        self.assertTrue(job.packet_start_time <= job.packet_end_time)
        self.assertTrue(job.size_on_disk <= job.size_limit)

        job.delete()

        job = self.shark.create_job(
            interface, 'test_create_job_with_parameters',
            '20%', indexing_size_limit='10%',
            packet_retention_time_limit=datetime.timedelta(days=7),
            start_immediately=True)
        self.assertEqual(job.size_limit, packet_total_size * 20/100)
        self.assertTrue(
            job.data.config.indexing.size_limit < index_total_size * 11/100)
        self.assertTrue(
            job.data.config.indexing.size_limit > index_total_size * 9/100)
        job.delete()

        #test contextual manager
        with self.shark.create_job(interface,
                                   'test_create_job_with_parameters',
                                   '20%',
                                   indexing_size_limit='1.7GB',
                                   start_immediately=True) as job:
            pass

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
        interface = shark.get_interfaces()[0]
        job = self.shark.create_job(
            interface, 'test_loaded_decorator',
            '300MB')
        with shark.create_clip(job, [fltr], 'test_decorator_clip') as clip:
            #this will test the @loaded decorator
            clip.size

    def test_job_export(self):
        shark = self.shark
        interface = shark.get_interfaces()[0]
        # keep this low or you will download too much
        with self.shark.create_job(interface,
                                   'test_job_export', '300MB',
                                   indexing_size_limit='30MB',
                                   start_immediately=True) as job:
            time.sleep(20)
            for x in ['/tmp/test_job_export', '/tmp/trace.pcap']:
                try:
                    os.remove(x)
                except:
                    pass
            job.download('/tmp/test_job_export')
            job.download('/tmp/')
            f = job.download()
            f.close()
            for x in ['/tmp/test_job_export', '/tmp/trace.pcap']:
                self.assertTrue(os.path.exists(x))
                os.remove(x)
            #remove tempdir for f.name
            tempdir = os.path.split(f.name)[0]
            shutil.rmtree(tempdir)

    def test_clip_export(self):
        job = self.shark.get_capture_jobs()[0]
        fltr = TimeFilter.parse_range('last 5 minutes')
        clip = self.shark.create_clip(job, [fltr], 'test_clip')
        logger.info('created 5 min trace clip for export test')
        f = clip.download()
        f.close()
        self.assertTrue(os.path.exists(f.name))
        os.remove(f.name)

#    def test_log_download(self):
#        shark = self.shark
#        f = shark.download_log()
#        self.assertTrue(os.path.exists(f))
#        os.remove(f)

    def test_interface_name_change(self):
        #test on live interface
        s = self.shark
        inst = s.get_interfaces()[0]

        def change_name(inst):
            inst.name = "flyscript test"

        if s.api_version.major == 4:
            self.assertRaises(AttributeError, change_name, inst)
        else:
            change_name(inst)
            self.assertEqual(inst.name, "flyscript test")
            inst.save()


class SharkLiveViewTests(SetUpTearDownMixin, testscenarios.TestWithScenarios):
    scenarios = config.get('4.0') + config.get('5.0')

    #this fails on low traffic machines, disabling
    # def test_live_view(self):
    #     shark = self.shark
    #     job = setup_capture_job(self.shark)
    #     clip = create_trace_clip(self.shark, job)
    #     interface = shark.get_interfaces()[0]
    #     columns, filters = setup_defaults()
    #     with shark.create_view(
    #         clip, columns, None, name='test_live_view') as v:
    #         cursor = viewutils.Cursor(v.all_outputs()[0])
    #         data = cursor.get_data()
    #         time.sleep(3)
    #         data2 = cursor.get_data()
    #         self.assertFalse(data == data2)

    def test_live_view_api(self):
        #test on live interface
        s = self.shark
        columns, filters = setup_defaults()
        interface = s.get_interfaces()[0]
        view = s.create_view(
            interface, columns, None, name='test_live_view', sync=True)

        time.sleep(20)
        # 20 seconds delta
        start = view.get_timeinfo()['start']
        onesec = 1000000000
        end = start + 20*onesec

        data = view.get_data(start=start)
        table = [(x['p'], x['t'],
                  T.datetime_to_nanoseconds(x['t'])) for x in data]

        # XXX figure how to split these up into
        # separate tests without adding 20sec delay
        #     for each of them

        # this part needs to be redone since delta
        # is no longer accepted for aggregated calls

        # aggregate and compare against first row of data
        # print table
        # delta = table[0][2] - start + onesec
        # d = view.get_data(aggregated=True, delta=delta)
        # self.assertEqual(len(d), 1)
        # self.assertEqual(d[0]['p'], table[0][0])

        # # aggregate and compare against first two rows of data
        # # note extra onesec not needed here
        # delta = table[1][2] - start
        # d = view.get_data(aggregated=True, delta=delta)
        # self.assertEqual(len(d), 1)
        # self.assertEqual(d[0]['p'], table[0][0])

        if len(table) >= 2:
            # aggregate with start/end as last two samples
            #
            start = table[-2][2]
            end = table[-1][2]
            d = view.get_data(aggregated=True, start=start, end=end)
            self.assertEqual(len(d), 1)
            self.assertEqual(d[0]['p'], table[-2][0])

            # aggregate with start/end as first and last sample
            #  result is sum of samples without last one
            start = table[0][2]
            end = table[-1][2]
            d = view.get_data(aggregated=True, start=start, end=end)
            self.assertEqual(len(d), 1)
            self.assertEqual(d[0]['p'], sum(x[0] for x in table[:-1]))

        # # aggregate with start as second sample and delta to end of table
        # #
        # start = table[1][2]
        # delta = table[-1][2] - start
        # d = view.get_data(aggregated=True, start=start, delta=delta)
        # self.assertEqual(len(d), 1)
        # self.assertEqual(d[0]['p'], sum(x[0] for x in table[1:-1]))

        # # aggregate going backwards from last sample
        # #
        # end = table[-1][2]
        # delta = end - table[-3][2]
        # d = view.get_data(aggregated=True, end=end, delta=delta)
        # self.assertEqual(len(d), 1)
        # self.assertEqual(d[0]['p'], sum(x[0] for x in table[-3:-1]))

        view.close()
