# Copyright (c) 2013 Riverbed Technology, Inc.
#
# This software is licensed under the terms and conditions of the 
# MIT License set forth at:
#   https://github.com/riverbed/flyscript/blob/master/LICENSE ("License").  
# This software is distributed "AS IS" as set forth in the License.


"""File and Directory classes encapsulate everything needed to handle
files and directory in Shark
"""

from __future__ import absolute_import

import os

from rvbd.shark._exceptions import SharkException
from rvbd.shark._interfaces import loaded, _InputSource
import datetime

class _FSResource(object):
    """This class contains methods to manage both Files and Directories.
    """
    data = None
    shark = None

    def __init__(self, shark, data):
        """Create a resource instance and it fetches all
        the  from remote. This will raise an exception if the remote
        directory  does  not exist. If the caller provides a data
        dictionary  it  just  sets  it without calling the API,
        this optimization is used by the list method.
        """
        path = data['id']
        assert shark is not None
        assert path is not None and len(path) > 0

        # Here it saves the shark reference so the caller does not have to
        # provide it for every call
        self.shark = shark
        #detect if we have a full dictionary of the resource or just its id
        if len(data) < 2 or 'created' not in data:
            # On the server side (and on the low level flyscript fs api) we
            # have two command to get resources details. 'get_all' returns
            # info about the root directory content, 'get_details' returns
            # info about all the other directories and files. The two
            # commands have different outputs on the low level and mostly of
            # the data available in the output of the second one are missing
            # in the first one output (id, creation date, modified date,
            # file # list) so this method have to set some so that the user
            # can use the directory reference. Also notice that whatever
            # action the user will try to do with the root directory
            # different from listing sub-dirs content will fail (e.g.
            # renaming a directory, creating a sub-dir, moving a directory,
            # uploading a trace file). Only Shark can control the root
            # directory
            if path == "/":
                self.data = self._get_root_details()
            else:
                self.data = self.shark.api.fs.get_details(path, details=True)
            assert isinstance(self.data, dict)

        else:
            assert isinstance(data, dict)
            self.data = data

    def _get_root_details(self):

        root_dirs = self.shark.api.fs.get_all(details=True, recursive=True)

        data = {}
        data["id"] = "/"

        # It would not make sense setting 0 here since that date would be
        # wrong
        data["created"] = None
        data["modified"] = None
        data["files"] = []
        data["dirs"] = []

        for current_dir_details in root_dirs:
            data["dirs"].append(Directory4(self.shark, current_dir_details["id"]))

        return data

    def remove(self):
        """Remove a remote resource and its details info
        """
        assert self.shark is not None
        assert self.data is not None

        self.shark.api.fs.delete(self.data["id"])
        self.data = None

    def move(self, new_path):
        """Move or rename a resource. 'new_path' should include the
        whole new path. If 'new_path' already exists and is a
        directory, then the resource is moved into that directory. If
        'new_path' does not exist, then the resource is renamed to the
        specified path."""
        assert self.shark is not None
        assert self.data is not None
        assert new_path is not None and len(new_path) > 0

        json_request = {"destination": new_path}
        self.shark.api.fs.move(self.data["id"], json_request)

        self._update_details(new_path)

    def get_info(self):
        """
        Retrieve info about a remote fs resource
        """
        assert self.shark is not None
        assert self.data is not None

        self.data = self.shark.api.fs.get_details(self.data["id"], details=True)
        return self.data

    @classmethod
    def exists(cls, shark, path):
        """Returns true if the resource exists, false otherwise
        """

        assert shark is not None
        assert path is not None and len(path) > 0

        try:
            shark.api.fs.get_details(path)
        except Exception:
            #vampolo: Exception is too generic, change it
            return False
        else:
            return True

    def _update_details(self, path):
        """Update the details object
        """
        assert self.shark is not None
        assert self.data is not None

        self.data = self.shark.api.fs.get_details(path, details=True)

    def __str__(self):
        return self.data["id"]

    def _ensure_loaded(self):
        # XXX we have a skeleton data dictionary even if the details
        # haven't been loaded yet.  look for a key that we must get
        # from the server: created
        if "created" not in self.data:
            self._load()
    
    def _load(self):
        self.data = self.shark.api.fs.get_details(self.data["id"], details=True)

    @property
    @loaded
    def path(self):
        """The file path
        """
        return self.data["id"]

    def is_live(self):
        """Can be used to determine if a source object is live or offline.
        The result is always False for a FS Resouce."""
        return False

    @property
    @loaded
    def created(self):
        """ Creation time timestamp
        """
        creation_time = None
        if self.data["created"] != None:
            creation_time = datetime.datetime.fromtimestamp(self.data["created"])
        return creation_time

    @property
    @loaded
    def modified(self):
        """ Modification time timestamp
        """
        modification_time = None
        if self.data["modified"] != None:
            modification_time = datetime.datetime.fromtimestamp(self.data["modified"])

        return modification_time


class Directory4(_FSResource):

    def __init__(self, shark, path):
        if not isinstance(path, dict):
            d = dict(id=path)
        else:
            d = path
        super(Directory4, self).__init__(shark, d)

    def __repr__(self):
        return "<Directory path='{0}'>".format(self.data.id)

    def _process_json_directories(self, json_data):
        """Process a json representing the directories
        This encapsulate the output of the fs get_details call to
        Flyscript objects
        """
        dir_list = list()
        file_list = list()
        for current_dir_details in json_data["dirs"]:
                dir_list.append(Directory4(self.shark, current_dir_details))

        for current_file_details in json_data["files"]:
            cls = File4._get_child_class(current_file_details)
            new_file = cls(self.shark, current_file_details)
            file_list.append(new_file)
        return dir_list, file_list

    @classmethod
    def create(cls, shark, path):
        """Create the directory and it returns a reference to it
        """
        error_msg = "An error occurred creating the directory "
        assert shark is not None
        assert path is not None and len(path) > 0

        # The API requires the directory name and the directory
        # parent dir as two separated parameters
        src_dir, dir_name = os.path.split(path)

        #Remove leading and trailing white space from the new resource name
        dir_name = dir_name.strip()

        if src_dir is not None and dir_name is not None and \
               len(src_dir) > 0 and len(dir_name) > 0:

            headers = { 'Content-Disposition' : dir_name,
                        'Content-Type' : 'application/x-shark-directory'
            }
            shark.api.fs.upload_raw(src_dir, None, headers)

            new_path = src_dir + "/" + dir_name
            return cls(shark, new_path)

        raise SharkException(error_msg + path + \
                             ": the path provided is not correct")

    def create_subdir(self, dir_name):
        """Create a sub-directory in the current directory and
        returns a reference to it. The 'dir_name' parameter should
        only include the directory name.
        """
        assert self.shark is not None

        complete_path = self.data["id"] + "/" + dir_name
        new_dir_ref = Directory4.create(self.shark, complete_path)
        self._update_details(self.data["id"])
        return new_dir_ref

    def list(self, recursive = False):
        """ List the directory content and return an array with the
        sub-directories and an array with the files
        """
        assert self.shark is not None
        
        #the get_details call has different result on / than on any
        #other directory, so we should take care of it
        res = self.shark.api.fs.get_details(
            self.data["id"], details = True, recursive = recursive)

        dir_list = []
        file_list = []

        if self.data['id'] == '/':
            #we are in the root case, res is thus a list of directories
            for directory in res:
                dir_list.append(Directory4(self.shark, directory))
            #no need to check for files, they are not in the root 
            #directory by design
        else:
            dir_list, file_list = self._process_json_directories(res)
        return dir_list, file_list

    def upload_trace_file(self, remote_file_name, local_path):
        """Upload a trace file and it returns a reference  to  it.
        'local_path' is the local file path, 'remote_file_name'
        contains only the file name
        """
        assert self.shark is not None

        complete_remote_path = self.data["id"] + "/" + remote_file_name
        return TraceFile4.upload(self.shark, complete_remote_path, local_path)
    

    def _walk(self, data, dirs):
        """Helper for walk in order to use recursive function without
        making subsequent REST calls
        """
        def data_lookup(data, id):
            """simply lookup a specific directory object
            by id from a json dictionary
            """
            if isinstance(data, list):
                #this is the case in which we are doing a
                #get_details of / that returns a list
                #so we check the id of the returned objects
                for item in data:
                    if item['id'] == id:
                        return item
            else:
                #this is the case of a get_details of a directory
                #so we look at the subdirectories
                for dir in data['dirs']:
                    if dir['id'] == id:
                        return dir
            

        for dir in dirs:
            sub_data = data_lookup(data, dir.data.id)
            sub_dirs, sub_files = self._process_json_directories(sub_data)
        
            yield dir.data.id, sub_dirs, sub_files
        
            for x in self._walk(sub_data, sub_dirs):
                yield x

    def walk(self):
        """Generate the file names in a directory tree by walking the tree in a top-down way. 
        For each directory in the tree rooted at directory top (including top itself),
        it yields a 3-tuple (dirpath, dirnames, filenames).
        """    
        res = self.shark.api.fs.get_details(
            self.data['id'], details=True, recursive=True)
        
        dirs = list()
        files = list()

        if self.data['id'] == '/':
            for dir in res:
                dirs.append(Directory4(self.shark, dir))
        else:
            dirs, files = self._process_json_directories(res)
        
        yield self.data['id'], dirs, files
        
        for x in self._walk(res, dirs):
            yield x

        
class File4(_FSResource, _InputSource):

    #this dictionary stores the string_type:class
    #for each supported File child
    types = dict()

    def __init__(self, shark, data):
        super(File4, self).__init__(shark, data)
        _InputSource.__init__(self, shark, data, shark.api.fs)

    @property
    def source_path(self):
        if self.data.id[0] == '/':
            return 'fs' + self.data.id
        else:
            return 'fs' + '/' + self.data.id

    @property
    def source_options(self):
        return {}

    @classmethod
    def get_all(cls, shark):
        res = list()
        for directory in shark.api.fs.get_all():
            for fi in directory['files']:
                clss = cls._get_child_class(fi)
                res.append(clss(shark, fi))
        return res

    @classmethod
    def _get_child_class(cls, fi):
        """Given a json representation of a file returns
        the correct class that represent that file
        """
        if fi['type'] in cls.types:
            clss = cls.types[fi['type']]
        else:
            clss = File4
        return clss

    @classmethod
    def get(cls, shark, path):
        assert shark is not None
        assert path is not None and len(path) > 0

        data = shark.api.fs.get_details(path, details=True)
        clss = cls._get_child_class(data)
        return clss(shark, data)

    def download(self, local_path):
        """Download a trace file. 'local_path' is the local file path
        """
        assert self.shark is not None

        self.shark.api.fs.download(self.data["id"], local_path)

    @property
    @loaded
    def size(self):
        """The resource disk size
        """
        return self.data["size"]

    @property
    def link_type(self):
        """The file link type (e.g. ethernet, 802.11...), as a lipbap DLT
        (see `<http://www.tcpdump.org/pcap3_man.html>`_)"""
        return self.data["link_type"]

    def copy(self, new_path):
        """Copy a file. 'new_path' should can be the whole new
        path or the destination folder.
        """
        assert self.shark is not None
        assert self.data is not None

        json_request = {"destination": new_path}
        self.shark.api.fs.copy(self.data["id"], json_request)

class FileMeta4(type):
    """This is the constructior for all the File-like classes.
    Basically it implements auto-registration of subclasses to the File
    class to make File being aware of all its children and have a
    dictionary that maps str_type:subclass.

    This allows function like File.get_all() to give back a list of all
    files in a shark appliance with the correct subclass
    """
    def __new__(cls, name, bases, attrs):
        file_subclass = super(FileMeta4, cls).__new__(cls, name, bases, attrs)
        for type_str in attrs['type_list']:
            File4.types[type_str] = file_subclass
        return file_subclass

class _AggregatedFile(File4):

    @classmethod
    def _create_aggregated_file(cls, type, shark, path, files):
        """Internal method to create a virtual file.
        This is used by create_merge_file and create_multisegment_file
        """
        error_msg = "An error occurred creating the aggregated file  "
        assert shark is not None
        assert path is not None and len(path) > 0
        assert isinstance(files, list) and len(files) > 0

        if type != "MULTISEGMENT_FILE" and type != "MERGED_FILE":
            raise SharkException(error_msg + \
                                 ": unknown aggregated file type " + type)

        aggr_file_dir, aggr_file_name = os.path.split(path)

        #Remove leading and trailing white space from the new resource name
        aggr_file_name = aggr_file_name.strip()

        json_dict = {}
        json_dict["type"] = type
        linked_files = []

        for linked_file in files:
            src_dir, file_name = os.path.split(linked_file.data["id"])
            linked_file_dict = {}
            linked_file_dict["path"] = file_name

            if type == "MULTISEGMENT_FILE":
                linked_file_dict["default_source"] = linked_file.default_file
                linked_file_dict["timeskew"] = linked_file.timeskew_val
            linked_files.append(linked_file_dict)

        json_dict["linked_sources"] = linked_files
        headers = {'Content-Disposition' : aggr_file_name}
        shark.api.fs.upload_xjobject(aggr_file_dir, json_dict, headers)

        new_path = aggr_file_dir + "/" + aggr_file_name
        if type == "MULTISEGMENT_FILE":

            return MultisegmentFile4(shark, {'id': new_path})
        else:
            return MergedFile4(shark, {'id': new_path})

    def list_linked_files(self):
        """ List the linked files that compose the aggregated file
        """
        trace_file_list = []
        assert self.shark is not None
        assert self.data is not None

        # The path parameter in a multisegment file contains only
        # the file name, therefore we have to add the resource
        # directory before it
        dir_name, file_name = os.path.split(self.data["id"])

        for linked_file in self.data["linked_sources"]:
            linked_file_path = dir_name + "/" + linked_file["path"]
            trace_file_list.append(TraceFile4(self.shark, linked_file_path))

        return trace_file_list

    def _load(self):
        self.data = self.shark.api.fs.get_details(self.data['id'], details=True)


class TraceFile4(File4):
    """This class contains method to manage Trace files.
    """
    __metaclass__ = FileMeta4
    default_file = False
    timeskew_val = 0
    description = ""
    type_list = ['PCAP_FILE', 'PCAPNG_FILE', 'ERF_FILE']

    def __repr__(self):
        assert self.data is not None
        src_dir, file_name = os.path.split(self.data["id"])
        return '<TraceFile4 {0}>'.format(file_name)

    @classmethod
    def upload(cls, shark, path, local_path):
        """Upload a trace file and it returns a reference  to  it.
        'path' contains the remote path, 'local_path' is the local
        file path, 'remote_file_name' contains only the file name
        """
        error_msg = "An error occurred uploading a trace" \
                    "file on the remote directory "
        assert shark is not None
        assert path is not None and len(path) > 0
        cls._validate_local_file(local_path, error_msg)

        file_dir, file_name = os.path.split(path)

        #Remove leading and trailing white space from a string
        file_name = file_name.strip()

        local_file_ref = open(local_path, "rb")

        headers = { 'Content-Disposition' : file_name,
                    'Content-Type' : 'application/octet-stream'
        }

        shark.api.fs.upload_raw(file_dir, local_file_ref, headers)
        local_file_ref.close()
        new_path = file_dir + "/" + file_name
        return TraceFile4(shark, {'id':new_path})

    def create_index(self):
        """Create an index on the trace file
        """
        error_msg = "An error occurred creating an index on the trace file "
        assert self.shark is not None
        assert self.data is not None

        try:
            self.shark.api.fs.create_index(self.data["id"])
        except Exception as e:
            msg = error_msg + self.data["id"] + ": " + str(e)
            raise SharkException(msg)

        self._update_details(self.data["id"])

    def remove_index(self):
        """Remove the index associated with the trace file
        """
        error_msg = "An error occurred removing an index on the trace file "
        assert self.shark is not None
        assert self.data is not None

        try:
            self.shark.api.fs.delete_index(self.data["id"])
        except Exception as e:
            msg = error_msg + self.data["id"] + ": " + str(e)
            raise SharkException(msg)

        self._update_details(self.data["id"])

    def index_info(self):
        """
        Returns index info if the file has an index associated
        """
        error_msg = "An error occurred removing an index on the trace file "
        assert self.shark is not None
        assert self.data is not None

        try:
            result = self.shark.api.fs.index_info(self.data["id"])
        except Exception as e:
            msg = error_msg + self.data["id"] + ": " + str(e)
            raise SharkException(msg)

        self._update_details(self.data["id"])
        return result

    def checksum(self):
        """
        Calculates the file checksum
        """
        assert self.shark is not None
        assert self.data is not None

        checksum = self.shark.api.fs.checksum(self.data["id"])

        return checksum

    @classmethod
    def _validate_local_file(cls, local_path, error_msg):
        if local_path == None:
            raise Exception(error_msg + local_path + \
                            ": the local file reference is None")

        if not os.path.isfile(local_path):
            raise Exception(error_msg + local_path + \
                            ": the local file does not exist")

    @property
    def link_layer(self):
        """The file link type (e.g. ethernet, 802.11...), as a lipbap DLT
        (see `<http://www.tcpdump.org/pcap3_man.html>`_)"""
        return self.data["link_type"]

    @property
    def trace_type(self):
        """ The trace file type PCAP_FILE, PCAPNG_FILE, ERF_FILE
        """
        return self.data["type"]


class MultisegmentFile4(_AggregatedFile):
    """This class contains method to manage Multisegment files.
    """
    __metaclass__ = FileMeta4
    type_list = ['MULTISEGMENT_FILE']

    def __repr__(self):
        assert self.data is not None
        src_dir, file_name = os.path.split(self.data["id"])
        return '<MultisegmentFile4 {0}>'.format(file_name)

    @classmethod
    def create_multisegment_file(cls, shark, path, files=None):
        """Creates a multisegment file starting from a
        """
        if files is None:
            files = []
        return cls._create_aggregated_file(cls.type_list[0], shark, path, files)

    def calculate_timeskew(self, packets):
        """
        Start the timeskew computation on the trace file. 'packets' contains
        the number of packets used for the timeskew computation
        """
        error_msg = "An error occurred calculating" \
                    "the time skew on the multisegment file "
        assert self.shark is not None
        assert self.data is not None

        if not isinstance(packets, int):
            raise SharkException(error_msg + \
                ": the 'packets' parameter is not an integer value")

        self.shark.api.fs.update_timeskew(self.data["id"], packets)
    
    def delete_timeskew(self):
        """Delete the timeskew computation on the trace file.
        """
        error_msg = "An error deleting the timeskew calculation" \
                    "on the multisegment file "
        assert self.shark is not None
        assert self.data is not None

        self.shark.api.fs.delete_timeskew(self.data["id"])
    
    def timeskew(self):
        """Return timeskew computation details.
        """
        assert self.shark is not None
        assert self.data is not None

        return self.shark.api.fs.get_timeskew(self.data["id"])


class MergedFile4(_AggregatedFile):
    __metaclass__ = FileMeta4
    type_list = ['MERGED_FILE']

    def __repr__(self):
        assert self.data is not None
        src_dir, file_name = os.path.split(self.data["id"])
        return '<MergedFile4 {0}>'.format(file_name)

    @classmethod
    def create_merged_file(cls, shark, path, files=None):
        """Creates a multisegment file starting from a
        """
        if files is None:
            files = []
        return cls._create_aggregated_file(cls.type_list[0], shark, path, files)
