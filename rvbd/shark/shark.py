# Copyright (c) 2013 Riverbed Technology, Inc.
#
# This software is licensed under the terms and conditions of the 
# MIT License set forth at:
#   https://github.com/riverbed/flyscript/blob/master/LICENSE ("License").  
# This software is distributed "AS IS" as set forth in the License.


"""
This module contains the Shark class, which is the main interface to
a Cascade Shark Appliance. It allows, among other things, retrieving
the state of the shark, modifying its settings and performing operations
like creating clips or starting/stopping capture jobs.
"""

from __future__ import absolute_import
import traceback

from rvbd.common.api_helpers import APIVersion
from rvbd.common.service import Service
from rvbd.shark._connection import SharkConnection
from rvbd.shark._exceptions import SharkException
from rvbd.shark._api_helpers import SharkAPIVersions
from rvbd.shark._api4 import API4_0
from rvbd.shark._api5 import API5_0
from rvbd.common.utils import ColumnProxy
from rvbd.shark._class_mapping import Classesv4, Classes, Classesv5


FILTERS_MAP = {}

API_TABLE = {
    "4.0" : API4_0,
    "5.0" : API5_0
    }

CLASS_TABLE = {
    '4.0': Classesv4,
    '5.0': Classesv5
    }


from rvbd.shark.filters import TimeFilter

__all__ = ['Shark']

class Shark(Service):
    """The Shark class is the main interface to interact with a Shark Appliance.
    Among other things, it makes it possible to manage views, jobs, files and
    trace clips, and to query and modify the appliance settings.
    """
    def __init__(self, host, port=None, auth=None,
                 force_version=None, force_ssl=None):
        """Establishes a connection to a Shark appliance.

        `host` is the name or IP address of the Shark to connect to

        `port` is the TCP port on which the Shark appliance listens.
                 if this parameter is not specified, the function will
                 try to automatically determine the port.

        `auth` defines the authentication method and credentials to use
                 to access the Shark.  It should be an instance of
                 rvbd.common.UserAuth or rvbd.common.OAuth.

        `force_version` is the API version to use when communicating.
                 if unspecified, this will use the latest version supported
                 by both this implementation and the Shark appliance.

        See the base [Service](common.html#service) class for more information
        about additional functionality supported.
        """

        if force_version is not None:
            if not force_version in API_TABLE:
                raise SharkException("API version %s unsupported" % force_version)
            versions = [APIVersion(force_version)]
        else:
            versions = [APIVersion(SharkAPIVersions.CURRENT)] + \
                       [APIVersion(v) for v in SharkAPIVersions.LEGACY]

        super(Shark, self).__init__("shark", host, port=port, auth=auth,
                                    force_ssl=force_ssl, versions=versions)
        
        self.api = API_TABLE[str(self.api_version)](self)
        self.classes = CLASS_TABLE[str(self.api_version)]()
        #these module may not be available
        try:
            self.settings = self.classes.Settings(self)
        except NotImplementedError:
            self.settings = Classes()

        self.views = {}
        self._interfaces = None
        self.xtfields = {}

        def _get_fields():
            self._fetch_extractor_fields()
            return self.xtfields.items()
        def _set_fields(f):
            self.columns = f
        self.columns = ColumnProxy(_get_fields, _set_fields)
        
        self._capture_jobs_cache = None
        self._traceclips_cache = None
        self._tracefiles_cache = None

    def __repr__(self):
        if self.port is not None:
            return '<Shark %s:%d>' % (self.host, self.port)
        else:
            return '<Shark %s>' % (self.host)

    def _get_connection_class(self):
        """Internal function to return the class
        used to instantiate a connection"""
        def conn_wrap(*args, **kwargs):
            if 'pool_size' not in kwargs:
                kwargs['pool_size'] = 4
            return SharkConnection(*args, **kwargs)
        return conn_wrap

    def _get_supported_versions(self):
        try:
            # First try the standard GL7 method
            versions = super(Shark, self)._get_supported_versions()

            if versions:
                return versions
        except:
            import traceback
            traceback.print_exc()
            pass

        # older sharks export the protocol info on /protocol_info, and
        # return a 401 unauthorized for any other unrecognized URLs
        res = self.conn.request('/protocol_info')
        if res.status != 200 \
               or res.getheader('content-type') != 'text/xml':
            # any other non-ok status probably means we are
            # not talking to a shark
            return None
        
        from xml.etree import ElementTree
        tree = ElementTree.fromstring(res.read())
        if tree.tag != 'ProtocolInfo':
            # probably some non-shark http server
            return None

        return [APIVersion(tree.get('Version'))]

    def logout(self):
        if self.conn:
            try:
                self.api.common.logout()
            except AttributeError:
                pass

            super(Shark, self).logout()

    def _detect_auth_methods(self):
        if self.api_version >= APIVersion("4.0"):
            # 4.0 shark supports the standard GL7 method
            return Service._detect_auth_methods(self)

        self._supports_auth_basic  = self.api_version >= APIVersion("3.0")
        self._supports_auth_cookie = self.api_version >= APIVersion("3.1")
        self._supports_auth_oauth  = False

    def get_open_views(self):
        """Get a list of View objects, one for each open view on
        the Shark appliance.
        """
        self._refresh_views()
        return self.views.values()

    def get_open_view_by_handle(self, handle):
        """Look up the view ``handle`` and return its View object"""
        if handle not in self.views:
            self._refresh_views()

        return self.views[handle]

    def _add_view(self, viewobj):
        """ add ``viewobj`` to the internal cache of view objects """
        # No handle if view hasn't yet been applied
        if not hasattr(viewobj, 'handle'):
            return
        self.views[viewobj.handle] = viewobj

    def _del_view(self, viewobj):
        """ remove ``viewobj`` from the internal cache of view objects """
        try:
            del self.views[viewobj.handle]
        except KeyError:
            pass

    def _refresh_views(self):
        oldviews = self.views
        self.views = {}

        try:
            handles = self.classes.View._get_all(self)
        except:
            # XXX make the except clause narrower
            traceback.print_exc()

            # We don't know if the server is down and we should delete all
            # view objects, or if it's simply momentarily unreachable and
            # we should keep the view objects -- so we take the conservative
            # route and keep them.
            return

        for handle in handles:
            # don't create a new object for the view if we already have one
            if handle in oldviews:
                self.views[handle] = oldviews[handle]
            else:
                try:
                    self.views[handle] = self.classes.View(self, handle)
                except:
                    # XXX make the except clause narrower
                    traceback.print_exc()

                    # XXX should put some sort of "orphaned view"
                    # object here so we know it exists but is unusable
                    pass

    def create_view_from_template(self, source, template,
                                  name=None, sync=True):
        """ Create a new view on this Shark using `template`.
        For 9.5.x and earlier, `template` should be an XML view
        document, for later releases, `template` should be a
        JSON view description.
        """
        view = self.classes.View._create_from_template(self, source, template,
                                                       name, sync)
        self._add_view(view)
        return view

    def create_view(self, src, columns, filters=None,
                    start_time=None, end_time=None,
                    name=None, charts=None, sync=True,
                    sampling_time_msec=None):
        """ Create a new view on this Shark.

        `src` identifies the source of packets to be analyzed.
        It may be any packet source object.

        `columns` specifies what information is extracted from
        packets and presented in this view.  It should be a list
        of `Key` and `Value` objects.

        `filters` is an optional list of filters that can be used
        to limit which packets from the packet source are processed
        by this view.

        """
       
        if start_time is not None or end_time is not None:
            if start_time is None or end_time is None:
                raise ValueError('must specify both start and end times')
            if filters is None:
                filters = []
            filters.append(TimeFilter(start_time, end_time))

        filterobjs = []
        if filters is not None:
            filterobjs.extend([filt.bind(self) for filt in filters])

        view = self.classes.View._create(self, src, columns, filterobjs, name=name,
                                         sync=sync, sampling_time_msec=sampling_time_msec)
        self._add_view(view)
        return view

    def create_job(self, interface, name,
             packet_retention_size_limit,
             packet_retention_packet_limit=None,
             packet_retention_time_limit=None,
             bpf_filter=None,
             snap_length=65525,
             indexing_size_limit=None,
             indexing_synced=False,
             indexing_time_limit=None,
             start_immediately=False,
             requested_start_time=None,
             requested_stop_time=None,
             stop_rule_size_limit=None,
             stop_rule_packet_limit=None,
             stop_rule_time_limit=None):
        """Create a Capture Job on this Shark, and return it as a
        a capture job object that can be used to work with the new job.

        `interface` is an interface object identifying the source of the packets
        that this job will capture. The method `get_interfaces()` returns
        interface objects for all interfaces on this shark.

        `name` is the name that the job will have after being created,
        and that will be used to identify the job for successive operations.

        `packet_retention_size_limit` is the maximum size on disk that the job
        will reach before old packets begin to be discarded.
        `packet_retention_size_limit` can be expressed as a number
        (in which case the unit will be bytes), or as a string.
        The format of the string can be Number and unit (e.g. "1.3GB"),
        or percentage of total disk spoace (e.g. "20%").

        `packet_retention_packet_limit`: the maximum number of packets that
        the job can contain before old packets begin to be discarded.

        `packet_retention_time_limit` a `datetime.timedelta` object
        specifying the maximum time interval that the job may contain before
        old packets begin to be discarded.

        `bpf_filter` is a filter, based on the Wireshark capture filter
        syntax, that selects which incoming packets should be saved
        in the job.

        `snap_length` is the portion of each packet that will be written on
        disk, in bytes. The default value of 65535 ensure that every packet is
        captured in its entirety.

        `indexing_size_limit` is the maximum size on disk that the index may
        reach before old index data may be discarded.
        It is specified in the same format as `keep_size`.

        If `indexing_synced` is True the job Microflow Index will be
        automatically pruned to cover the same time extension of the captured
        packets.

        `indexing_time_limit` is a `datetime.timedelta` object indicating
        how long index data should be retained.  This argument is only
        meaningful if `index_and_capture_synced` is False.

        If `start_immediately` is True, the Job is started after it has been
        created.

        `requested_start_time` and `requested_stop_time` are `datetime.datetime`
        objects that, if specified, determine the absolute time when the
        job will start/stop.

        If `stop_rule_size_limit` is specified, the job will stop storing
        new packets when the given size on disk is reached.  It is specified
        in the same format as `keep_size`.

        If `stop_rule_packet_limit` is specified, the job will stop storing new
        packets when the given number of packets is reached.

        If `stop_rule_time_limit` is specified, it should be a
        `datetime.timedelta` object, and the job will stop storing new
        packets when the given time has elapsed.
        """
        self._capture_jobs_cache = None
        return self.classes.Job.create(self,
                          interface, name, packet_retention_size_limit,
                          packet_retention_packet_limit,
                          packet_retention_time_limit,
                          bpf_filter, snap_length, indexing_size_limit,
                          indexing_synced, indexing_time_limit,
                          start_immediately,
                          requested_start_time, requested_stop_time,
                          stop_rule_size_limit, stop_rule_packet_limit,
                          stop_rule_time_limit)

    def create_clip(self, job, filters, description, locked=True):
        """Create a clip in the Shark appliance
        """
        self._traceclips_cache = None
        clip = self.classes.Clip.add(self, job, filters, description, locked)
        return clip

    def get_interfaces(self, force_refetch=False):
        """Return a list of Interface objects, corresponding to the
        capture interfaces available on the Shark.

        If ``force_refetch`` is True, the list of interfaces will be
        re-fetched from the Shark.  Otherwise, the list may be cached.
        """
        if force_refetch or self._interfaces is None:
            self._interfaces = self.classes.Interface.get_all(self)
        return self._interfaces

    def get_interface_by_name(self, ifname, force_refetch=False):
        """ Return an Interface object corresponding to the
        interface named ``ifname``.

        If ``force_refetch`` is True, the list of interfaces will be
        re-fetched from the Shark.  Otherwise, the list may be cached.
        """
        if force_refetch or self._interfaces is None:
            self._interfaces = self.classes.Interface.get_all(self)

        found = [ ifc for ifc in self._interfaces if ifc.name == ifname ]
        if len(found) == 0:
            raise KeyError()
        assert len(found) == 1
        return found[0]

    def get_capture_jobs(self, force_refetch=False):
        """Return a list of CaptureJob objects, corresponding to the
        capture jobs currently running on the Shark.

        If ``force_refetch`` is True, the list of jobs will be
        re-fetched from the Shark.  Otherwise, the list may be cached.
        """
        if self._capture_jobs_cache is None or force_refetch:
            self._capture_jobs_cache = self.classes.Job.get_all(self)
        return self._capture_jobs_cache

    def get_capture_job_by_name(self, jobname, force_refetch=False):
        """Return a CaptureJob object for the capture job ``jobname``

        If ``force_refetch`` is True, the list of jobs will be
        re-fetched from the Shark.  Otherwise, the list may be cached.
        """
        job = None
        if self._capture_jobs_cache is None or force_refetch:
            job = self.classes.Job.get(self, None, name=jobname)
        else:
            for j in self._capture_jobs_cache:
                if j.name == jobname:
                    job = j
                    break
        if job is None:
            raise ValueError('No Job called {0} is available on this Shark'.format(jobname))
        else:
            return job

    def get_clips(self, force_refetch=False):
        """Return a list of TraceClip objects, corresponding to the
        trace clips available on the Shark.

        If ``force_refetch`` is True, the list of clips will be
        re-fetched from the Shark.  Otherwise, the list may be cached.
        """
        if force_refetch or self._traceclips_cache is None:
            self._traceclips_cache = self.classes.Clip.get_all(self)
        return self._traceclips_cache

    def get_trace_clip_by_description(self, description, force_refetch=False):
        """Return a TraceClip object for the trace clip with the given
        description.

        If ``force_refetch`` is True, the list of jobs will be
        re-fetched from the Shark.  Otherwise, the list may be cached.

        **Note**: Clips don't have descriptions by default. A description can
        be added to a clip by right-clicking on it in Pilot.
        """
        if not force_refetch or self._traceclips_cache is None:
            #get_clips already set up the cache for us
            clips = self.get_clips(force_refetch)
        else:
            clips = self._traceclips_cache

        clips = [ c for c in clips
                  if c.description == description ]
            
        if len(clips) == 0:
            raise SharkException('cannot find clip %s' % description)

        return clips[0]

    def get_files(self, force_refetch=False):
        """Return a list of TraceFile, MergedFile or Multisegment objects,
        corresponding to the trace files available on the Shark.

        If ``force_refetch`` is True, the list of files will be
        re-fetched from the Shark.  Otherwise, the list may be cached.
        """
        if force_refetch or self._tracefiles_cache is None:
            self._tracefiles_cache = self.classes.File.get_all(self)
        return self._tracefiles_cache

    def get_file(self, path):
        """Given a path retrieve the `File` associated with it
        """
        return self.classes.File.get(self, path)

    def _fetch_extractor_fields(self, force=False):
        if not force and len(self.xtfields) > 0:
            return
        
        for f in self.classes.ExtractorField.get_all(self):
            self.xtfields[f.id] = f

    def get_extractor_fields(self):
        """ Return a list of all extractor fields available on this shark """
        self._fetch_extractor_fields()
        return sorted(self.xtfields.values())

    def find_extractor_field_by_name(self, fname):
        """ Return a specific extractor field given its name """
        self._fetch_extractor_fields()
        return self.xtfields[fname]

    def search_extractor_fields(self, string):
        """Search through the extractor fields to find the ones that
        match the given string in either the field name or the
        description."""
        self._fetch_extractor_fields()

        string = string.lower()
        return [ f for f in self.xtfields.values()
                 if string in f.name.lower() or string in f.desc.lower() ]

    def get_protocol_version(self):
        """Return the API protocol version used by this shark."""
        return str(self.api_version)

    def get_logininfo(self):
        """Return a dictionary with the information useful prior to
        logging in to the shark, including the protocol version,
        banner, and whether or not a login purpose should be
        requested from the user.
        """
        return self.api.common.get_auth_info()

    def get_serverinfo(self):
        '''Get the Shark appliance overall info.

        Return Value: a named tuple with the server parameters
        '''
        return self.api.system.get_info(self)

    def get_stats(self):
        '''Get the Shark appliance storage info
        '''
        res = dict()
        res['storage'] = self.api.stats.get_storage()
        res['memory'] = self.api.stats.get_memory()
        return res

    def restart(self):
        """Restart the Shark Appliance.
        This will issue a system reboot.
        """
        self.api.system.restart({'type':'SHARK'})

    def restart_probe(self):
        """Restart the Shark probe.
        This will restart the Pilot server only.
        """
        self.api.system.restart({'type':'PROBE'})

    def ping(self):
        '''Ping the probe.

        Return Value: True/False depending whether the server is
        up and running or not
        '''
        return self.api.common.ping(self)

    def create_dir(self, path):
        """
        Create a new directory. It will trigger an exception if the directory
        exist.
        Return Value: a reference to the new directory
        """
        return self.classes.Directory.create(self, path)

    def get_dir(self, path):
        """
        Get a directory. It will trigger an exception if the directory does not
        exist.
        Return Value: a reference to the directory
        """
        return self.classes.Directory(self, path)

    def exists(self, path):
        """
        Check if a path exists, works for files or directories.
        Return Value: true if the path exists, false otherwise
        """
        return self.classes.Directory.exists(self, path)

    def upload_trace_file(self, path, local_file):
        """
        Uploads a new trace file. 'path' is the complete destination path,
        'local_file' is the the local file to upload.
        Return Value: reference to the new trace file
        """
        return self.classes.TraceFile.upload(self, path, local_file)

    def create_multisegment_file(self, path, files=None):
        """
        Creates a multisegment file. 'path' is the new file full name and
        'files' is a File objects list
        Return Value: a reference to the new file
        """
        return self.classes.MultisegmentFile.create_multisegment_file(self, path, files)

    def create_merged_file(self, path, files=None):
        """
        Creates a merged file. 'path' is the new file full name and
        'files' is a File objects list
        Return Value: a reference to the new file
        """
        return self.classes.MergedFile.create_merged_file(self, path, files)
    
    def download_log(self, path=None, log_type='COMPLETE', case_id=None):
        """Download log archive to local machine into path
        If path is None a temporary file is created
        
        `log_type` can be:
            -'CURRENT'
            -'PROBE'
            -'PACKETRECORDER'
            -'COMPLETE' (default)
        
        `case_id` is an integer that represent the case id
        """
        config = {'dump_type': log_type}
        if case_id:
            config['case_id'] = int(case_id)
        return self.api.system.get_sysdump(path, config)
    
    @property
    def version(self):
        """Returns the Shark software version
        """
        return self.api.common.info().get('sw_version')

    @property
    def model(self):
        """Returns the Shark software model
        """
        return self.api.common.info().get('model')
