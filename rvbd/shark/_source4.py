# Copyright (c) 2013 Riverbed Technology, Inc.
#
# This software is licensed under the terms and conditions of the 
# MIT License set forth at:
#   https://github.com/riverbed/flyscript/blob/master/LICENSE ("License").  
# This software is distributed "AS IS" as set forth in the License.



from __future__ import absolute_import

from rvbd.shark import _interfaces
from rvbd.shark._interfaces import loaded
from rvbd.shark._exceptions import SharkException
from rvbd.common import utils, timeutils


class Interface4(_interfaces._InputSource):
    """A physical interface packet source, that can be used for live packet
    capture. Interface objects are normally not instantianted directly, but
    are instead obtained by calling
    :py:func:`rvbd.shark.shark.Shark.get_interfaces` or
    :py:func:`rvbd.shark.shark.Shark.get_interface_by_name`."""
    def __init__(self, shark, data):
        super(Interface4, self).__init__(shark, data, shark.api.interfaces)
        self.id = self.data.id

    def __repr__(self):
        return '<{0} {1} {2}>'.format(self.__class__.__name__, self.data.name, self.data.type)

    def __str__(self):
        return '{0}'.format(self.data.name)
    
    @property
    def name(self):
        """The interface device name."""
        return self.data.name
    
    @property
    def description(self):
        """The interface description."""
        return self.data.description

    def is_live(self):
        """Can be used to determine if a source object is live or offline.
        The result is always True for an Interface4."""
        return True

    @property
    def source_path(self):
        return 'interfaces/{0}'.format(self.id)

    @property
    def source_options(self):
        return {}

    @classmethod
    def get_all(cls, shark):
        interfaces = shark.api.interfaces.get_all()
        return [ cls(shark, data) for data in interfaces ]

    def update(self):
        """Update current object with the values from the server
        """
        data = self._api.get_details(self.id)
        super(Interface4, self).update(data)
    

class Clip4(_interfaces.Clip):
    """A trace clip packet source.
    These objects are returned by `Shark.get_clips`."""
    def __init__(self, shark, data):
        super(Clip4, self).__init__(shark, data, shark.api.clips)
        self.id = self.data.id

    def __str__(self):
        return 'clips/'+self.id

    def _ensure_loaded(self):
        if self.data is None or len(self.data) == 1:
            self._load()
    
    def _load(self):
        self.data = self._api.get_details(self.id)

    @property
    def source_path(self):
        """Return the path of a Clip used for the internal shark representation
        """
        return 'clips/{0}'.format(self.id)

    @property
    def source_options(self):
        return {}

    @property
    @loaded
    def description(self):
        """Returns the description of the clip
        """
        return self.data.config.description

    @property
    @loaded
    def size(self):
        """Returns the size of the clip
        """
        return self.data.status.estimated_size

    def delete(self):
        """Erase the clip from shark
        """
        self._api.delete(self.id)
        self.id = None

    @classmethod
    def get_all(cls, shark):
        """Get the complete list of trace files on given a Shark.

        ``shark`` is an ``rvbd.shark.shark.Shark`` object

        Returns a list of ``TraceFile`` objects
        """
        return [cls(shark, data) for data in shark.api.clips.get_all()]

    @classmethod
    def add(cls, shark, job, filters, description, locked=True):
        """Create a new clip given a Shark connection and a job handle.

        `shark` is a Shark object

        `description` will be associated with the new clip.
        (The description is shown near the clip in grey in Pilot)

        `job` is the capture job to use

        `filters` is the list of filters to associate to the clip.
        In order for the clip to be valid, there must be at list one
        time filter in this list

        Returns a trace clip object for the new clip.
        """
        config = {
            'job_id': job.id,
            'filters': [filt.bind(shark) for filt in filters],
            'description': description,
            }
        ret = shark.api.clips.add(config)
        clip = cls(shark, ret)
        if locked:
            clip.locked(True)
        return clip

    @loaded
    def locked(self, state=None):
        """Set or retrieve locked state of a clip
        """
        pass

    def download(self, path=None):
        """Download the Clip packets to a file.
        If path is None packets will be exported to a temporary file.
        A file object that contains the packets is returned.
        """
        return open(self._api.get_packets(self.id, path), 'rb')

class Job4(_interfaces.Job):
    """A capture job packet source. These objects are normally not
    instantiated directly, but are instead obtained by calling
    `Shark.get_capture_jobs` or `Shark.get_capture_job_by_name`.
    """

    def __init__(self, shark, data):
        super(Job4, self).__init__(shark, data, shark.api.jobs)
        self.id = self.data.id
        self.index_enabled = True 
        self.data = data

    def _ensure_loaded(self):
        if self.data is None or len(self.data) == 1:
            self._load()
    
    def _load(self):
        self.data = self._api.get_details(self.id)

    @loaded
    def __repr__(self):
        return '<{0} {1} on {2}>'.format(
            self.__class__.__name__,
            self.data.config.name,
            self.data.config.interface_description)

    @loaded
    def __str__(self):
        return '{0}'.format(self.data.config.name)

    @property
    def source_path(self):
        return 'jobs/{0}'.format(self.id)

    @property
    @loaded
    def source_options(self):
        if not self.index_enabled:
            return {'disable_index' : True}
        else:
            return {}

    def is_live(self):
        """Can be used to determine if a source object is live or offline.
        The result is always False for a CaptureJob."""
        return False

    @property
    @loaded
    def name(self):
        """The capture job name"""
        return self.data.config.name

    @property
    @loaded
    def size_on_disk(self):
        """The capture job actual size, corresponding to the one shown by the
        Shark UI shows."""
        return self.get_status()['packet_size']

    @property
    @loaded
    def size_limit(self):
        """The capture job maximum size, corresponding to the one shown by the
        Shark UI shows."""
        return self.data.config.packet_retention.size_limit

    @property
    def packet_start_time(self):
        return self.get_status()['packet_start_time']

    @property
    def packet_end_time(self):
        return self.get_status()['packet_end_time']

    @property
    def interface(self):
        """an :py:class:`Interface` object, representing the interface used as a packet
        source for this job."""
        interfaces = Interface4.get_all(self.shark)
        for interface in interfaces:
            if self.data.config.interface_name == interface.id:
                return interface
        ValueError('{0} interface not found'.format(self.data.config.interface_description))

    @property
    def handle(self):
        """The internal capture job handle. The handle is sometimes required
        for advanced operations on the job.
        """
        return self.data.id


    @classmethod
    def get_all(cls, shark):
        """Get the complete list of capture jobs on given a Shark.

        ``shark`` is an :py:class:`rvbd.shark.shark.Shark` object

        Returns a list of ``CaptureJob`` objects

        size_on_disk, keep_size, packet_start_time,
                 packet_end_time,
        """
        jobs = []
        for j in shark.api.jobs.get_all():
            jobs.append(cls(shark, j))
        return jobs

    @classmethod
    def create(cls, shark, interface, name,
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
        """Create a new capture job"""

        def _calc_size(size, total):
            if isinstance(size, str) and size[-1] == '%':
                size = total * int(size[:-1]) /100
            elif not isinstance(size, (int, long)) and size is not None:
                size = utils.human2bytes(size)
            return size

        stats = shark.get_stats()
        packet_storage_total = stats['storage']['packet_storage'].total
        index_storage_total = stats['storage']['os_storage']['index_storage'].total
 
        packet_retention_size_limit = _calc_size(packet_retention_size_limit, packet_storage_total) if packet_retention_size_limit else None
        stop_rule_size_limit = _calc_size(stop_rule_size_limit, packet_storage_total) if stop_rule_size_limit else None
        indexing_size_limit = _calc_size(indexing_size_limit, index_storage_total) if indexing_size_limit else None

        packet_retention_packet_limit = int(packet_retention_packet_limit) if packet_retention_packet_limit else None
        stop_rule_size_limit = int(stop_rule_size_limit) if stop_rule_size_limit else None
        stop_rule_packet_limit = int(stop_rule_packet_limit) if stop_rule_packet_limit else None
        snap_length = int(snap_length) if snap_length else 65535
        indexing_size_limit = int(indexing_size_limit) if indexing_size_limit else None

        if indexing_time_limit:
            indexing_time_limit = int(timeutils.timedelta_total_seconds(indexing_time_limit))
        if packet_retention_time_limit:
            packet_retention_time_limit = int(timeutils.timedelta_total_seconds(packet_retention_time_limit))
        if stop_rule_time_limit:
            stop_rule_time_limit = int(timeutils.timedelta_total_seconds(stop_rule_time_limit))

        if requested_start_time:
            requested_start_time = requested_start_time.strftime(cls._timefmt)
        if requested_stop_time:
            requested_stop_time = requested_stop_time.strftime(cls._timefmt)

        jobrequest = { 'interface_name': interface.id }

        if name:
            jobrequest['name'] = name
        if packet_retention_size_limit or packet_retention_packet_limit or packet_retention_time_limit:
            jobrequest['packet_retention'] = dict()
            if packet_retention_size_limit:
                jobrequest['packet_retention']['size_limit'] = packet_retention_size_limit
            if packet_retention_packet_limit:
                jobrequest['packet_retention']['packet_limit'] = packet_retention_packet_limit
            if packet_retention_time_limit:
                jobrequest['packet_retention']['time_limit'] = packet_retention_time_limit
        if bpf_filter:
            jobrequest['bpf_filter'] = bpf_filter
        if requested_start_time:
            jobrequest['requested_start_time'] = requested_start_time
        if requested_stop_time:
            jobrequest['requested_stop_time'] = requested_stop_time
        if stop_rule_size_limit or stop_rule_packet_limit or stop_rule_time_limit:
            jobrequest['stop_rule'] = dict()
            if stop_rule_size_limit:
                jobrequest['stop_rule']['size_limit'] = stop_rule_size_limit
            if stop_rule_packet_limit:
                jobrequest['stop_rule']['packet_limit'] = stop_rule_packet_limit
            if stop_rule_time_limit:
                jobrequest['stop_rule']['time_limit'] = stop_rule_time_limit
        if snap_length:
            jobrequest['snap_length'] = int(snap_length)
        if indexing_synced or indexing_size_limit or indexing_time_limit:
            jobrequest['indexing'] = dict()
            if indexing_synced:
                jobrequest['indexing']['synced'] = indexing_synced
            if indexing_size_limit:
                jobrequest['indexing']['size_limit'] = indexing_size_limit
            if indexing_time_limit:
                jobrequest['indexing']['time_limit'] = indexing_time_limit
        if start_immediately:
            jobrequest['start_immediately'] = start_immediately

        job_id = shark.api.jobs.add(jobrequest)

        job = cls(shark, job_id)
        return job

    def start(self):
        """Start a job in the Shark appliance
        """
        self._api.state_update(self.id, {'state': "RUNNING"})

    def stop(self):
        """Stop a job in the Shark appliance
        """
        self._api.state_update(self.id, {'state': "STOPPED"})

    def clear(self, restart=False):
        """Clear data in the Shark appliance
        """
        self._api.state_update(self.id, {'state':'STOPPED', 'clear_packets':True})
        if restart:
            self.start()

    def delete(self):
        """Delete job from the Shark appliance
        """
        try:
            self.stop()
        except:
            pass
        self._api.delete(self.id)


    def add_clip(self, filters, description, locked=True):
        """
        Create a new trace clip under this job.

        `filters` limit which packets from the clip should go into
        this clip.  Since all packets in the new clip will be kept on
        disk if the clip is locked, this field typically includes
        time filters to limit the clip to a fixed time interval.

        `description` is a name for the clip, it is shown next to the
        clip in the Pilot user interface.

        If `locked` is True, packets in the new clip will not be deleted
        from disk as long as the clip exists.  Note that locking packets
        in trace clips necessarily reduces the amount of disk capacity
        for existing capture jobs.

        Returns a trace clip object representing the new clip.
        """
        return Clip4.add(self.shark, self, filters, description, locked)

    def download(self, path=None):
        """Download the Job packets to a path.
        If path is None packets will be exported to a temporary file.
        A file object that contains the packets is returned.
        """
        return open(self._api.get_packets(self.id, path), 'rb')
        
    def get_state(self):
        """Return the state of the job (e.g. RUNNING, STOPPED)"""
        return self.get_status().state
    
    def get_status(self):
        """Return status information about the capture job."""
        return self._api.get_status(self.id)

    def get_stats(self):
        """Return statistics about the capture job."""
        return self._api.get_stats(self.id)

    def get_index_info(self):
        """Return statistics about the capture job index."""
        return self._api.get_index(self.id)
