# Copyright (c) 2013 Riverbed Technology, Inc.
#
# This software is licensed under the terms and conditions of the 
# MIT License set forth at:
#   https://github.com/riverbed/flyscript/blob/master/LICENSE ("License").  
# This software is distributed "AS IS" as set forth in the License.


from rvbd.shark._api_helpers import APIGroup, APITimestampFormat
import urllib

class API4Group(APIGroup):

    base_headers = {}

    def _xjtrans(self, urlpath, method, data, as_json, timestamp_format=APITimestampFormat.NANOSECOND, params=None, custom_headers=None):
        """Issue the given API request using either JSON or XML
        (dictated by the as_json parameter)."""
        self.add_base_header('X-RBT-High-Precision-Timestamp-Format', timestamp_format)
        
        # XXXWP Changing the method so that the caller can specify some extra headers
        headers =  dict(self.base_headers)
        if isinstance(custom_headers, dict):
            headers.update(custom_headers)

        # we are dealing with a url so let's sanitize it.
        # this may break code but at least prevents flyscript to send insane urls to the server
        # define insane: url that contains spaces
        urlpath = urllib.quote(urlpath)

        if as_json:
            return self.shark.conn.json_request(self.uri_prefix + urlpath, method=method,
                                                  data=data, params=params, extra_headers=headers)
        else:
            return self.shark.conn.xml_request(self.uri_prefix + urlpath, method=method,
                                                 body=data, check_result=True,
                                                 params=params, extra_headers=headers)

    def add_base_header(self, key, value=""):
        if isinstance(key, basestring):
            self.base_headers[key] = value

    def remove_base_header(self, key):
        if isinstance(key, basestring):
            self.base_headers.pop(key, None)

class Common(API4Group):
    def get_services(self, as_json=True, timestamp_format=APITimestampFormat.NANOSECOND):
        """Return the set of services running on this system
        """
        return self._xjtrans("/services", "GET", None, as_json, timestamp_format)

    def get_auth_info(self, as_json=True, timestamp_format=APITimestampFormat.NANOSECOND):
        """Return authentication information necessary to properly log in to the system.
        """
        return self._xjtrans("/auth_info", "GET", None, as_json, timestamp_format)

    def login(self, credentials, as_json=True, timestamp_format=APITimestampFormat.NANOSECOND):
        """Log in to the system using the given credentials. Returns the session cookie for use in subsequent calls.
        """
        return self._xjtrans("/login", "POST", credentials, as_json, timestamp_format)

    def logout(self, as_json=True, timestamp_format=APITimestampFormat.NANOSECOND):
        """Log out from the system by invalidating the session cookie
        """
        headers = {'connection':'close'}
        return self._xjtrans("/logout", "POST", {}, as_json, timestamp_format, custom_headers=headers)

    def ping(self, as_json=True, timestamp_format=APITimestampFormat.NANOSECOND):
        return self._xjtrans("/ping", "GET", None, as_json, timestamp_format)
    
    def info(self):
        return self._xjtrans("/info", "GET", None, True, APITimestampFormat.NANOSECOND)

class Settings(API4Group):
    def get_basic(self, as_json=True, timestamp_format=APITimestampFormat.NANOSECOND):
        """ Retrieves the basic configuration settings """
        return self._xjtrans("/settings/basic", "GET", None, as_json, timestamp_format)
    
    def update_basic(self, config, as_json=True, timestamp_format=APITimestampFormat.NANOSECOND):
        """ Updates the basic configuration settings """
        return self._xjtrans("/settings/basic", "PUT", config, as_json, timestamp_format)
    
    def get_auth(self, as_json=True, timestamp_format=APITimestampFormat.NANOSECOND):
        """ Retrieves the authentication settings """
        return self._xjtrans("/settings/auth", "GET", None, as_json, timestamp_format)

    def update_auth(self, config, as_json=True, timestamp_format=APITimestampFormat.NANOSECOND):
        """ Updates the authentication settings """
        return self._xjtrans("/settings/auth", "PUT", config, as_json, timestamp_format)

    def get_audit(self, as_json=True, timestamp_format=APITimestampFormat.NANOSECOND):
        """ Retrieves the audit settings """
        return self._xjtrans("/settings/audit", "GET", None, as_json, timestamp_format)

    def update_audit(self, config, as_json=True, timestamp_format=APITimestampFormat.NANOSECOND):
        """ Updates the audit settings """
        return self._xjtrans("/settings/audit", "PUT", config, as_json, timestamp_format)

    def get_cors_domains(self, as_json=True, timestamp_format=APITimestampFormat.NANOSECOND):
        """ Retrieves the cors_domains settings """
        return self._xjtrans("/settings/cors_domains", "GET", None, as_json, timestamp_format)

    def update_cors_domains(self, config, as_json=True, timestamp_format=APITimestampFormat.NANOSECOND):
        """ Updates the cors_domains settings """
        return self._xjtrans("/settings/cors_domains", "PUT", config, as_json, timestamp_format)
    
    def update_firewall_config(self, config, as_json=True, timestamp_format=APITimestampFormat.NANOSECOND):
        """ Updates the firewall settings """
        return self._xjtrans("/settings/firewall", "POST", config, as_json, timestamp_format)
    
    def get_firewall_config(self, as_json=True, timestamp_format=APITimestampFormat.NANOSECOND):
        """ Returns the firewall settings """
        return self._xjtrans("/settings/firewall", "GET", None, as_json, timestamp_format)

    def get_raw(self):
        """ Returns the raw settings contained in the configuration file in plain text"""
        resp = self.shark.conn.request(self.uri_prefix + "/settings/raw", "GET")
        data = resp.read()
        return data

    def update_raw(self, settings):
        self.shark.conn.request(self.uri_prefix + "/settings/raw", "PUT",
                                body=settings, extra_headers={'Content-Type' : 'text/plain'})

    def reset_raw(self):
        self.shark.conn.request(self.uri_prefix + "/settings/raw", "PUT",
                                body='', extra_headers={'Content-Type' : 'text/plain', 'Content-length' : 0})

    def get_protocol_groups(self):
        """ Returns the protocol_groups settings contained in the configuration file in plain text"""
        resp = self.shark.conn.request(self.uri_prefix + "/settings/protocol_groups", "GET")
        data = resp.read()
        return data

    def update_protocol_groups(self, settings):
        resp = self.shark.conn.request(self.uri_prefix + "/settings/protocol_groups", "PUT",
                                       body=settings, extra_headers={'Content-Type' : 'text/plain'})
        resp.read()

    def get_protocol_names(self):
        """ Returns the protocol_names settings contained in the configuration file in plain text"""
        resp = self.shark.conn.request(self.uri_prefix + "/settings/protocol_names", "GET")
        data = resp.read()
        return data

    def update_protocol_names(self, settings):
        resp = self.shark.conn.request(self.uri_prefix + "/settings/protocol_names", "PUT",
                                       body=settings, extra_headers={'Content-Type' : 'text/plain'})
        resp.read()
        
    def get_notification(self, as_json=True, timestamp_format=APITimestampFormat.NANOSECOND):
        """ Returns notification and SMTP settings from management daemon"""
        return self._xjtrans("/settings/notification", "GET", None, as_json, timestamp_format)

    def update_notification(self, config, as_json=True, timestamp_format=APITimestampFormat.NANOSECOND):
        """ Updates notification and SMTP settings on management daemon"""
        return self._xjtrans("/settings/notification", "PUT", config, as_json, timestamp_format)

    def send_test_email(self, config, as_json=True, timestamp_format=APITimestampFormat.NANOSECOND):
        """ Send a test email using the given config"""
        return self._xjtrans("/settings/notification/send_test_mail", "POST", config, as_json, timestamp_format)

    def send_test_trap(self, config, as_json=True, timestamp_format=APITimestampFormat.NANOSECOND):
        return self._xjtrans('/settings/notification/send_test_trap', "POST", config, as_json, timestamp_format)


    def get_profiler_export(self, as_json=True, timestamp_format=APITimestampFormat.NANOSECOND):
        """Get the profiler export
        """
        return self._xjtrans('/settings/profiler_export', 'GET', None, as_json, timestamp_format)

    def update_profiler_export(self, params=None, as_json=True, timestamp_format=APITimestampFormat.NANOSECOND):
        """Set the profiler export
        """
        return self._xjtrans('/settings/profiler_export', 'PUT', params, as_json, timestamp_format)

class Interfaces(API4Group):
    def get_all(self, params=None, as_json=True, timestamp_format=APITimestampFormat.NANOSECOND):
        """ Lists the interfaces on the system """
        return self._xjtrans("/interfaces", "GET", None, as_json, timestamp_format, params=params)

    def get_details(self, handle, as_json=True, timestamp_format=APITimestampFormat.NANOSECOND):
        """ Retrieves information about an interface """
        return self._xjtrans("/interfaces/%s" % handle, "GET", None, as_json, timestamp_format)

    def update(self, handle, config, as_json=True, timestamp_format=APITimestampFormat.NANOSECOND):
        """ Updates the interface configuration """
        return self._xjtrans("/interfaces/%s" % handle, "PUT", config, as_json, timestamp_format)

    def start_blink(self, handle, as_json=True, timestamp_format=APITimestampFormat.NANOSECOND):
        """ Sets an interface LED to blink mode. """
        return self._xjtrans("/interfaces/%s/blink_status" % handle, "PUT", {"blink_status":"ON"}, as_json, timestamp_format)

    def stop_blink(self, handle, as_json=True, timestamp_format=APITimestampFormat.NANOSECOND):
        """ Sets an interface LED to non-blink mode. """
        return self._xjtrans("/interfaces/%s/blink_status" % handle, "PUT", {"blink_status":"OFF"}, as_json, timestamp_format)

    def create_export(self, handle, config=None, as_json=True, timestamp_format=APITimestampFormat.NANOSECOND):
        """ Create an export and return url """
        return self._xjtrans("/interfaces/%s/exports" % handle, "POST", config, as_json, timestamp_format)

    def get_all_exports(self, handle, as_json=True, timestamp_format=APITimestampFormat.NANOSECOND):
        """ List all exports for this job """
        return self._xjtrans("/interfaces/%s/exports" % handle, "GET", None, as_json, timestamp_format)

    def get_export_details(self, handle, export_id, as_json=True, timestamp_format=APITimestampFormat.NANOSECOND):
        """ Return details for a specific export """
        return self._xjtrans("/interfaces/%s/exports/%s" % (handle, export_id), "GET", None, as_json, timestamp_format)

    def get_packets_from_export(self, handle, export_id, path=None):
        """ Fetch packets from export ID """
        return self.shark.conn.download(self.uri_prefix + "/interfaces/%s/exports/%s/packets" % (handle, export_id), path)
    
    def get_packets(self, handle, path=None, params=None):
        """ Directly fetch packets for this interface, with optional parameters """
        return self.shark.conn.download(self.uri_prefix + "/interfaces/%s/packets" % handle, path, params=params)

    def delete_export(self, handle, export_id):
        """ Delete an export """
        return self._xjtrans("/interfaces/%s/exports/%s" % (handle, export_id), "DELETE", None, True, APITimestampFormat.NANOSECOND)


class Jobs(API4Group):
    def get_all(self, as_json=True, timestamp_format=APITimestampFormat.NANOSECOND):
        """ Lists the capture jobs on the system """
        return self._xjtrans("/jobs" , "GET", None, as_json, timestamp_format)
    
    def add(self, config, as_json=True, timestamp_format=APITimestampFormat.NANOSECOND):
        """ Add a new capture job to the system """
        return self._xjtrans("/jobs", "POST", config, as_json, timestamp_format)

    def delete(self, handle):
        """ Updates the capture jobs configuration """
        return self._xjtrans("/jobs/%s" % handle, "DELETE", None, True, APITimestampFormat.NANOSECOND)

    def get_details(self, handle, as_json=True, timestamp_format=APITimestampFormat.NANOSECOND):
        """ Retrieves information about a capture job """
        return self._xjtrans("/jobs/%s" % handle, "GET", None, as_json, timestamp_format)

    def update(self, handle, config, as_json=True, timestamp_format=APITimestampFormat.NANOSECOND):
        """ Updates the capture jobs configuration """
        return self._xjtrans("/jobs/%s" % handle, "PUT", config, as_json, timestamp_format)

    def create_export(self, handle, config=None, as_json=True, timestamp_format=APITimestampFormat.NANOSECOND):
        """ Create an export and return url """
        return self._xjtrans("/jobs/%s/exports" % handle, "POST", config, as_json, timestamp_format)

    def get_all_exports(self, handle, as_json=True, timestamp_format=APITimestampFormat.NANOSECOND):
        """ List all exports for this job """
        return self._xjtrans("/jobs/%s/exports" % handle, "GET", None, as_json, timestamp_format)

    def get_export_details(self, handle, export_id, as_json=True, timestamp_format=APITimestampFormat.NANOSECOND):
        """ Return details for a specific export """
        return self._xjtrans("/jobs/%s/exports/%s" % (handle, export_id), "GET", None, as_json, timestamp_format)

    def delete_export(self, handle, export_id):
        """ Delete an export """
        return self._xjtrans("/jobs/%s/exports/%s" % (handle, export_id), "DELETE", None, True, APITimestampFormat.NANOSECOND)

    def get_packets_from_export(self, handle, export_id, path=None):
        """ Fetch packets from export ID """
        return self.shark.conn.download(self.uri_prefix + "/jobs/%s/exports/%s/packets" % (handle, export_id), path)

    def get_packets(self, handle, path=None, params=None):
        """ Directly fetch packets for this job, with optional parameters """
        return self.shark.conn.download(self.uri_prefix + "/jobs/%s/packets" % handle, path, params=params)

    def state_update(self, handle, config, as_json=True, timestamp_format=APITimestampFormat.NANOSECOND):
        """ Updates the capture jobs status """
        return self._xjtrans("/jobs/%s/status" % handle, "PUT", config, as_json, timestamp_format)
  
    def get_config(self, handle, as_json=True, timestamp_format=APITimestampFormat.NANOSECOND):
        """ Retrieves configuration information about a capture job """
        return self._xjtrans("/jobs/%s/config" % handle, "GET", None, as_json, timestamp_format)
        
    def get_status(self, handle, as_json=True, timestamp_format=APITimestampFormat.NANOSECOND):
        """ Retrieves status information about a capture job """
        return self._xjtrans("/jobs/%s/status" % handle, "GET", None, as_json, timestamp_format)
        
    def get_index(self, handle, as_json=True, timestamp_format=APITimestampFormat.NANOSECOND):
        """ Retrieves index information about a capture job """
        return self._xjtrans("/jobs/%s/index" % handle, "GET", None, as_json, timestamp_format)

    def get_stats(self, handle, as_json=True, timestamp_format=APITimestampFormat.NANOSECOND):
        """ Retrieves statistics about a capture job """
        return self._xjtrans("/jobs/%s/stats" % handle, "GET", None, as_json, timestamp_format)
        
class Clips(API4Group):
    def get_all(self, as_json=True, timestamp_format=APITimestampFormat.NANOSECOND):
        """ Lists the trace clips on the system """
        return self._xjtrans("/clips" , "GET", None, as_json, timestamp_format)
    
    def add(self, config, as_json=True, timestamp_format=APITimestampFormat.NANOSECOND):
        """ Add a new trace clip to the system """
        return self._xjtrans("/clips", "POST", config, as_json, timestamp_format)
    
    def get_details(self, handle, as_json=True, timestamp_format=APITimestampFormat.NANOSECOND):
        """ Retrieves information about a trace clip """
        return self._xjtrans("/clips/%s" % handle, "GET", None, as_json, timestamp_format)
    
    def update(self, handle, config, as_json=True, timestamp_format=APITimestampFormat.NANOSECOND):
        """ Updates the trace clip configuration """
        return self._xjtrans("/clips/%s" % handle, "PUT", config, as_json, timestamp_format)
    
    def delete(self, handle):
        """Delete a trace clip."""
        return self._xjtrans('/clips/%s' % handle, "DELETE", None, True, APITimestampFormat.NANOSECOND)

    def set_locked(self, handle, config, as_json=True, timestamp_format=APITimestampFormat.NANOSECOND):
        """ Locks/unlocks the trace clip """
        return self._xjtrans("/clips/%s/status" % handle, "PUT", config, as_json, timestamp_format)
    
    def create_export(self, handle, config=None, as_json=True, timestamp_format=APITimestampFormat.NANOSECOND):
        """ Create an export and return url """
        return self._xjtrans("/clips/%s/exports" % handle, "POST", config, as_json, timestamp_format)
    
    def get_all_exports(self, handle, as_json=True, timestamp_format=APITimestampFormat.NANOSECOND):
        """ List all exports for this job """
        return self._xjtrans("/clips/%s/exports" % handle, "GET", None, as_json, timestamp_format)
    
    def get_export_details(self, handle, export_id, as_json=True, timestamp_format=APITimestampFormat.NANOSECOND):
        """ Return details for a specific export """
        return self._xjtrans("/clips/%s/exports/%s" % (handle, export_id), "GET", None, as_json, timestamp_format)

    def delete_export(self, handle, export_id):
        """ Delete an export """
        return self._xjtrans("/clips/%s/exports/%s" % (handle, export_id), "DELETE", None, True, APITimestampFormat.NANOSECOND)

    def get_packets_from_export(self, handle, export_id, path=None):
        """ Fetch packets from export ID """
        return self.shark.conn.download(self.uri_prefix + "/clips/%s/exports/%s/packets" % (handle, export_id), path)

    def get_packets(self, handle, path=None, params=None):
        """ Directly fetch packets from this clip, with optional parameters """
        return self.shark.conn.download(self.uri_prefix + "/clips/%s/packets" % handle, path, params=params)
        
    def get_config(self, handle, as_json=True, timestamp_format=APITimestampFormat.NANOSECOND):
        """ Retrieves configuration information about a trace clip """
        return self._xjtrans("/clips/%s/config" % handle, "GET", None, as_json, timestamp_format)
        
    def get_status(self, handle, as_json=True, timestamp_format=APITimestampFormat.NANOSECOND):
        """ Retrieves status information about a trace clip """
        return self._xjtrans("/clips/%s/status" % handle, "GET", None, as_json, timestamp_format)
        
    def get_index(self, handle, as_json=True, timestamp_format=APITimestampFormat.NANOSECOND):
        """ Retrieves index information about a trace clip """
        return self._xjtrans("/clips/%s/index" % handle, "GET", None, as_json, timestamp_format)

class Files(API4Group):
    def get_all(self, details = False, recursive= False, as_json=True, timestamp_format=APITimestampFormat.NANOSECOND):
        """ Lists all user files on the system """

        # This call includes some parameters in the url
        url = "/fs"

        params = {}

        if details == True:
            params['details'] = True

        if recursive:
            params['recursive'] = True

        return self._xjtrans(url , "GET", None, as_json, timestamp_format, params=params)

    def upload_raw(self, path, data, headers):
        """Raw wrapper around the file upload. """
        if path[0] == '/':
            path = path[1:]
        return self.shark.conn.upload(self.uri_prefix + "/fs/%s" % path, data, extra_headers=headers)
                        
    def upload_xjobject(self, path, data, headers, as_json=True, timestamp_format = APITimestampFormat.NANOSECOND):
        """Upload an XML or JSON-encoded file object."""
        if path[0] == '/':
            path = path[1:]

        return self._xjtrans("/fs/%s" % path, "POST", data, as_json, timestamp_format, custom_headers = headers)
    
    def get_details(self, path, params=None, as_json=True, details = False, recursive = False,
                    timestamp_format=APITimestampFormat.NANOSECOND):
        """Retrieves information about a disk file """
        if path[0] == '/':
            path = path[1:]

        # This call includes some parameters in the url
        url = "/fs/%s" % path

        if params is None:
            params = {}
            
        if details == True:
            params['details'] = True

        if recursive:
            params['recursive'] = True

        return self._xjtrans(url, "GET", None, as_json, timestamp_format, params)

    def upload_trace(self, path, filename, local_file_ref ):
        """Convenience function to upload a trace file."""
        headers = {'Content-Disposition' : filename,
                   'Content-Type' : 'application/octet-stream'}
        if path[0] == '/':
            path = path[1:]
        return self.shark.conn.upload(self.uri_prefix + "/fs/%s" % path, local_file_ref, extra_headers=headers)
    
    def download(self, path, local_path=None):
        """Convenience function to download a file."""
        if path[0] == '/':
            path = path[1:]
        return self.shark.conn.download(self.uri_prefix + "/fs/%s/download" % path, path=local_path)
        
    def delete(self, path):
        """Delete a file from the system."""
        if path[0] == '/':
            path = path[1:]
        return self._xjtrans('/fs/%s' % path, "DELETE", None, True, APITimestampFormat.NANOSECOND)

    def update(self, path, config, as_json=True, timestamp_format=APITimestampFormat.NANOSECOND):
        """ Updates the disk file """
        if path[0] == '/':
            path = path[1:]
        return self._xjtrans("/fs/%s" % path, "PUT", config, as_json, timestamp_format)

    def checksum(self, path, as_json=True, timestamp_format=APITimestampFormat.NANOSECOND):
        """ Obtains a disk file checksum """
        if path[0] == '/':
            path = path[1:]
        return self._xjtrans("/fs/%s/checksum" % path, "GET", None, as_json, timestamp_format)

    def move(self, path, config, as_json=True, timestamp_format=APITimestampFormat.NANOSECOND):
        """ Moves a disk file """
        if path[0] == '/':
            path = path[1:]
        return self._xjtrans("/fs/%s/move" % path, "POST", config, as_json, timestamp_format)
    
    def copy(self, path, config, as_json=True, timestamp_format=APITimestampFormat.NANOSECOND):
        """ Moves a disk file """
        if path[0] == '/':
            path = path[1:]
        return self._xjtrans("/fs/%s/copy" % path, "POST", config, as_json, timestamp_format)
    
    def create_index(self, path, as_json=True, timestamp_format=APITimestampFormat.NANOSECOND):
        """ Creates an index for a disk file """
        if path[0] == '/':
            path = path[1:]
        return self._xjtrans("/fs/%s/index" % path, "POST", None, as_json, timestamp_format)

    def delete_index(self, path):
        """ Deletes an index for a disk file """
        if path[0] == '/':
            path = path[1:]
        return self._xjtrans("/fs/%s/index" % path, "DELETE", None, True, APITimestampFormat.NANOSECOND)

    def index_info(self, path, as_json=True, timestamp_format=APITimestampFormat.NANOSECOND):
        """ Gets information on an index for a disk file """
        if path[0] == '/':
            path = path[1:]
        return self._xjtrans("/fs/%s/index" % path, "GET", None, as_json, timestamp_format)

    def update_timeskew(self, path, packets, as_json=True, timestamp_format=APITimestampFormat.NANOSECOND):
        """ Creates a timeskew estimation for a multi-segment file """
        url = "/fs/%s/timeskew_estimate" % path

        params = {
            'packet_count': packets
            }

        if path[0] == '/':
            path = path[1:]
        return self._xjtrans(url, "PUT", None, as_json, timestamp_format, params=params)

    def delete_timeskew(self, path):
        """ Deletes a timeskew estimation for a multi-segment file """
        if path[0] == '/':
            path = path[1:]
        return self._xjtrans("/fs/%s/timeskew_estimate" % path, "DELETE", None, True, APITimestampFormat.NANOSECOND)

    def get_timeskew(self, path, as_json=True, timestamp_format=APITimestampFormat.NANOSECOND):
        """ Gets information on a timeskew estimation for a multi-segment file """
        if path[0] == '/':
            path = path[1:]
        return self._xjtrans("/fs/%s/timeskew_estimate" % path, "GET", None, as_json, timestamp_format)

    def create_export(self, path, config=None, as_json=True, timestamp_format=APITimestampFormat.NANOSECOND):
        """ Create an export and return url """
        if path[0] == '/':
            path = path[1:]
        return self._xjtrans("/fs/%s/exports" % path, "POST", config, as_json, timestamp_format)

    def get_all_exports(self, path, as_json=True, timestamp_format=APITimestampFormat.NANOSECOND):
        """ List all exports for this job """
        if path[0] == '/':
            path = path[1:]
        return self._xjtrans("/fs/%s/exports" % path, "GET", None, as_json, timestamp_format)

    def get_export_details(self, path, export_id, as_json=True, timestamp_format=APITimestampFormat.NANOSECOND):
        """ Return details for a specific export """
        if path[0] == '/':
            path = path[1:]
        return self._xjtrans("/fs/%s/exports/%s" % (path, export_id), "GET", None, as_json, timestamp_format)

    def delete_export(self, path, export_id):
        """ Delete an export """
        if path[0] == '/':
            path = path[1:]
        return self._xjtrans("/fs/%s/exports/%s" % (path, export_id), "DELETE", None, True, APITimestampFormat.NANOSECOND)

    def get_packets_from_export(self, path, export_id, local_path=None):
        """ Fetch packets from export ID """
        if path[0] == '/':
            path = path[1:]
        return self.shark.conn.download(self.uri_prefix + "/fs/%s/exports/%s/packets" % (path, export_id), local_path)

    def get_packets(self, path, local_path=None,  params=None):
        """ Directly fetch packets from file on server, with optional parameters """
        if path[0] == '/':
            path = path[1:]
        return self.shark.conn.download(self.uri_prefix + "/fs/%s/packets" % path, local_path, params=params)
        
class Users(API4Group):
    def get(self, as_json=True, timestamp_format=APITimestampFormat.NANOSECOND):
        """ Lists the users on the system """
        return self._xjtrans("/auth/users" , "GET", None, as_json, timestamp_format)

    def add(self, config, as_json=True, timestamp_format=APITimestampFormat.NANOSECOND):
        """ Add a user to the system """
        return self._xjtrans("/auth/users", "POST", config, as_json, timestamp_format)

    def get_details(self, username, as_json=True, timestamp_format=APITimestampFormat.NANOSECOND):
        """ Retrieves information about a user """
        return self._xjtrans("/auth/users/%s" % username, "GET", None, as_json, timestamp_format)

    def delete(self, username):
        """ Deletes the given user from the system """
        return self._xjtrans("/auth/users/%s" % username, "DELETE", None, True, APITimestampFormat.NANOSECOND)

    def update(self, user, config):
        """Updates user configuration"""
        return self._xjtrans('/auth/users/{0}'.format(user), 'PUT', config, True, APITimestampFormat.NANOSECOND)

class Groups(API4Group):
    def get(self, as_json=True, timestamp_format=APITimestampFormat.NANOSECOND):
        """ Lists the groups on the system """
        return self._xjtrans("/auth/groups" , "GET", None, as_json, timestamp_format)

    def get_details(self, groupname, as_json=True, timestamp_format=APITimestampFormat.NANOSECOND):
        """ Retrieves information about a group on the system """
        return self._xjtrans("/auth/groups/%s" % groupname, "GET", None, as_json, timestamp_format)

    def add(self, config, as_json=True, timestamp_format=APITimestampFormat.NANOSECOND):
        """ Add a group to the system """
        return self._xjtrans("/auth/groups", "POST", config, as_json, timestamp_format)

    def delete(self, groupname):
        """ Deletes the given group from the system """
        return self._xjtrans("/auth/groups/%s" % groupname, "DELETE", None, True, APITimestampFormat.NANOSECOND)


class Licenses(API4Group):
    def get(self, as_json=True, timestamp_format=APITimestampFormat.NANOSECOND):
        """ Lists all licenses in the system """
        return self._xjtrans("/settings/licenses" , "GET", None, as_json, timestamp_format)

    def get_details(self, license_key, as_json=True, timestamp_format=APITimestampFormat.NANOSECOND):
        """ Get details for a specific license key """
        return self._xjtrans("/settings/licenses/%s" % license_key, "GET", None, as_json, timestamp_format)

    def get_status(self, as_json=True, timestamp_format=APITimestampFormat.NANOSECOND):
        """ Get system-wide licensing status """
        return self._xjtrans("/settings/licenses/status" , "GET", None, as_json, timestamp_format)

    def add_license(self, config, as_json=True, timestamp_format=APITimestampFormat.NANOSECOND):
        """ Add new license to the system """
        return self._xjtrans("/settings/licenses", "POST", config, as_json, timestamp_format)

    def delete_license(self, license_key):
        """ Delete a license from the system. """
        return self._xjtrans("/settings/licenses/%s" % license_key, "DELETE", None, True, APITimestampFormat.NANOSECOND)

    def generate_license_req(self, config, as_json=True, timestamp_format=APITimestampFormat.NANOSECOND):
        """ Generate a license request. """
        return self._xjtrans("/settings/licenses/request", "POST", config, as_json, timestamp_format)


class Views(API4Group):
    def add(self, config, as_json=True, timestamp_format=APITimestampFormat.NANOSECOND):
        """Add and run a new view"""
        return self._xjtrans("/views", "POST", config, as_json, timestamp_format)

    def get_all(self, as_json=True, timestamp_format=APITimestampFormat.NANOSECOND):
        """Return the list of all running views"""
        return self._xjtrans("/views" , "GET", None, as_json, timestamp_format)

    def close(self, handle):
        """Close the running view"""
        return self._xjtrans("/views/%s" % handle, "DELETE", None, True, APITimestampFormat.NANOSECOND)
        
    def get_config(self, handle, as_json=True, timestamp_format=APITimestampFormat.NANOSECOND):
        """Return the configuration of the given view"""
        return self._xjtrans("/views/%s" % handle, "GET", None, as_json, timestamp_format)

    def get_acl(self, handle, as_json=True, timestamp_format=APITimestampFormat.NANOSECOND):
        """Return the access control list of the given view"""
        return self._xjtrans("/views/%s/acl" % handle, "GET", None, as_json, timestamp_format)

    def update_acl(self, handle, as_json=True, timestamp_format=APITimestampFormat.NANOSECOND):
        """Return the access control list of the given view"""
        # XXX/demmer should this be a PUT??
        return self._xjtrans("/views/%s/acl" % handle, "POST", None, as_json, timestamp_format)

    def get_legend(self, handle, output, as_json=True, timestamp_format=APITimestampFormat.NANOSECOND):
        """Return the legend for the given view output"""
        return self._xjtrans("/views/%s/data/%s/legend" % (handle, output), "GET", None, as_json, timestamp_format)
        
    def get_data(self, handle, output, as_json=True, timestamp_format=APITimestampFormat.NANOSECOND, **params):
        """Return the output for the given view"""
        return self._xjtrans("/views/%s/data/%s" % (handle, output), "GET", None, as_json, timestamp_format, params)

    def get_stats(self, handle, as_json=True, timestamp_format=APITimestampFormat.NANOSECOND):
        """Return the statistics for the given view"""
        return self._xjtrans("/views/%s/stats" % handle, "GET", None, as_json, timestamp_format)
    
    def get_processor_stats(self, handle, as_json=True, timestamp_format=APITimestampFormat.NANOSECOND):
        """Return the processor statistics for the given view"""
        return self._xjtrans("/debug/handles/%s" % handle, "GET", None, as_json, timestamp_format)

    def create_watch(self, handle, config, as_json=True, timestamp_format=APITimestampFormat.NANOSECOND):
        """Create a new watch on the view"""
        return self._xjtrans("/views/%s/watches" % handle, "POST", config, as_json, timestamp_format)

    def get_watches(self, handle, as_json=True, timestamp_format=APITimestampFormat.NANOSECOND):
        """Obtain the list of watches for a running view"""
        return self._xjtrans("/views/%s/watches" % handle, "GET", as_json, timestamp_format)

    def delete_watch(self, handle, watch_id, as_json=True, timestamp_format=APITimestampFormat.NANOSECOND):
        """Delete a watch from the view"""
        return self._xjtrans("/views/%s/watches/%s" % (handle, watch_id), "DELETE", None, as_json, timestamp_format)

    def get_watch(self, handle, watch_id, as_json=True, timestamp_format=APITimestampFormat.NANOSECOND):
        """Get settings for a watch on a running view"""
        return self._xjtrans("/views/%s/watches/%s" % (handle, watch_id), "GET", None, as_json, timestamp_format)

    def update_watch(self, handle, watch_id, config, as_json=True, timestamp_format=APITimestampFormat.NANOSECOND):
        """Update settings for a watch on a running view"""
        return self._xjtrans("/views/%s/watches/%s" % (handle, watch_id), "PUT", config, as_json, timestamp_format)

    def disable_watch(self, handle, watch_id, as_json=True, timestamp_format=APITimestampFormat.NANOSECOND):
        """Disable a watch on a running view"""
        return self._xjtrans("/views/%s/watches/%s/disable" % (handle, watch_id), "POST", None, as_json, timestamp_format)

    def enable_watch(self, handle, watch_id, as_json=True, timestamp_format=APITimestampFormat.NANOSECOND):
        """Enable a watch on a running view"""
        return self._xjtrans("/views/%s/watches/%s/enable" % (handle, watch_id), "POST", None, as_json, timestamp_format)

    # XXX/demmer lock/unlock/stop
    
class System(API4Group):
    def get_info(self, as_json=True, timestamp_format=APITimestampFormat.NANOSECOND):
        """Return the system info"""
        return self._xjtrans("/system/info", "GET", None, as_json, timestamp_format)

    def restart(self, config, as_json=True, timestamp_format=APITimestampFormat.NANOSECOND):
        """Restart the probe or reboot the system"""
        return self._xjtrans("/system/restart", "POST", config, as_json, timestamp_format)

    def get_events(self, as_json=True, timestamp_format=APITimestampFormat.NANOSECOND):
        """Return the events list"""
        return self._xjtrans("/debug/events", "GET", None, as_json, timestamp_format)
    
    def get_sysdump(self, path, config, as_json=True, timestap_format=APITimestampFormat.NANOSECOND):
        """Dump log archive
        """
        return self.shark.conn.download(self.uri_prefix + "/system/sysdump", path, params=config)

class Certificates(API4Group):
    
    def get(self, as_json=True, timestamp_format=APITimestampFormat.NANOSECOND):
        """ Returns the certificates settings """
        return self._xjtrans("/settings/certificates", "GET", None, as_json, timestamp_format)
    
    
    def update_profiler_export_certificate(self, certificate_data, as_json=True, timestamp_format=APITimestampFormat.NANOSECOND): 
        """ Set a new Profiler Export certificate"""
        return self._xjtrans("/settings/certificates/profiler_export", "PUT", certificate_data, as_json, timestamp_format)
    
    def generate_profiler_export_certificate(self, certificate_data, as_json=True, timestamp_format=APITimestampFormat.NANOSECOND):
        """ Generate new Trusted Profiler certificate"""
        return self._xjtrans("/settings/certificates/profiler_export/generate", "POST", certificate_data, as_json, timestamp_format)
    
    def copy_web_certificate(self, as_json=True, timestamp_format=APITimestampFormat.NANOSECOND): 
        """ Reuses the web certificate as profiler export certificate"""
        return self._xjtrans("/settings/certificates/profiler_export/copy_web", "POST", None, as_json, timestamp_format)
    
    
    def update_web_certificate(self, certificate_data, as_json=True, timestamp_format=APITimestampFormat.NANOSECOND): 
        """ Set a new Web certificate"""
        return self._xjtrans("/settings/certificates/web", "PUT", certificate_data, as_json, timestamp_format)
    
    def generate_web_certificate(self, certificate_data, as_json=True, timestamp_format=APITimestampFormat.NANOSECOND):
        """ Generate new web certificate"""
        return self._xjtrans("/settings/certificates/web/generate", "POST", certificate_data, as_json, timestamp_format)
        
    def copy_profiler_export_certificate(self, as_json=True, timestamp_format=APITimestampFormat.NANOSECOND): 
        """ Reuses the Profiler Export's certificate as web certificate"""
        return self._xjtrans("/settings/certificates/web/copy_profiler_export", "POST", None, as_json, timestamp_format)
       
    
    def add_trusted_profiler_certificate(self, certificate_data, as_json=True, timestamp_format=APITimestampFormat.NANOSECOND): 
        """ Add a new Trusted Profiler certificate"""
        return self._xjtrans("/settings/certificates/trusted_profilers", "POST", certificate_data, as_json, timestamp_format)
    
    def delete_trusted_profiler_certificate(self, id, as_json=True, timestamp_format=APITimestampFormat.NANOSECOND):
        """ Delete a new Trusted Profiler certificate by its id"""
        return self._xjtrans("/settings/certificates/trusted_profilers/"+id, "DELETE", None, as_json, timestamp_format)

class Stats(API4Group):
    def get_memory(self, as_json=True, timestamp_format=APITimestampFormat.NANOSECOND):
        """ Returns the memory stats """
        return self._xjtrans("/stats/memory", "GET", None, as_json, timestamp_format)
        
    def get_profiler_export(self, as_json=True, timestamp_format=APITimestampFormat.NANOSECOND):
        """ Returns the profiler export stats """
        return self._xjtrans("/stats/profiler_export", "GET", None, as_json, timestamp_format)
        
    def get_storage(self, as_json=True, timestamp_format=APITimestampFormat.NANOSECOND):
        """Returns the storage stats
        """
        return self._xjtrans("/stats/storage", "GET", None, as_json, timestamp_format)

class Info(API4Group):
    def get_fields(self, as_json=True):
        """Returns all the extractor fields
        """
        return self._xjtrans("/fields.json", 'GET', None, as_json)

class Misc(API4Group):
    def ping(self, method="GET", data=None, headers=None):
        """Run the ping command using the specified method and
        optionally passing the given data. Note that for POST/PUT the
        server will echo back exactly what was posted.

        For GET, the content type can be requested using an Accept
        header of either text/xml or application/json.
        """
        resp = self.shark.conn.request(self.uri_prefix + "/ping", method, body=data, extra_headers=headers)
        return resp.read()


class Update(API4Group):
    def get(self):
        return self._xjtrans('/system/update', 'GET', None, True, APITimestampFormat.NANOSECOND)

    def load_iso_from_url(self, data):
        """Download upload iso from an url"""
        return self._xjtrans('/system/update/url', 'POST', data, True, APITimestampFormat.NANOSECOND)

    def upload_iso(self, f):
        """Given a file descriptor `f`, uploads the content to the server as an upload iso
        """
        headers = {'Content-Disposition' : 'update.iso',
                   'Content-Type' : 'application/octet-stream'}
        
        return self.shark.conn.upload(self.uri_prefix + "/system/update/iso", data=f, extra_headers=headers)

    def delete_iso(self, data):
        """Delete a previously uploaded iso"""
        return self._xjtrans('/system/update/state', 'PUT', data, True, APITimestampFormat.NANOSECOND)

    def update(self, data):
        """Perform update of the shark

        `init_id` is the id of the image on the server that is ready for update
        """
        return self._xjtrans('/system/update/state', 'PUT',
                             data,
                             True, APITimestampFormat.NANOSECOND)

class Storage(API4Group):
    """Encapsulates the storage informations that can be found in
    Maintenance page in the webui
    """
    def get(self):
        """Gets the storage configuration from the Server
        """
        return self._xjtrans('/system/storage', 'GET', None, True, APITimestampFormat.NANOSECOND)

    def reinitialize(self):
        """Reinitializes the packet storage
        """
        return self._xjtrans('/system/storage/reinitialize', 'POST', None, True, APITimestampFormat.NANOSECOND)

    def format(self, data):
        """Formats packet storage
        """
        return self._xjtrans('/system/format_storage', 'POST', data, True, APITimestampFormat.NANOSECOND )


class API4_0(object):
    version = '4.0'
    common_version = '1.0'
    def __init__(self, shark):
        self.shark = shark
        self.common = Common("/api/common/"+self.common_version, self.shark)
        self.settings = Settings("/api/shark/"+self.version, self.shark)
        self.interfaces = Interfaces("/api/shark/"+self.version, self.shark)
        self.jobs = Jobs("/api/shark/"+self.version, self.shark)
        self.clips = Clips("/api/shark/"+self.version, self.shark)
        self.fs = Files("/api/shark/"+self.version, self.shark)
        self.licenses = Licenses("/api/shark/"+self.version, self.shark)
        self.certificates = Certificates("/api/shark/"+self.version, self.shark)
        self.system = System("/api/shark/"+self.version, self.shark)
        self.view = Views("/api/shark/"+self.version, self.shark)
        self.stats = Stats("/api/shark/"+self.version, self.shark)
        self.info = Info('/api/shark/'+self.version+'/info', self.shark)
        self.users = Users('/api/shark/'+self.version, self.shark)
        self.groups = Groups('/api/shark/'+self.version, self.shark)
        self.update = Update('/api/shark/'+self.version, self.shark)
        self.storage = Storage('/api/shark/'+self.version, self.shark)

        # For the misc handlers just make them methods of the api class itself
        m = Misc('/api/shark/'+self.version, self.shark)
        self.ping = m.ping

__all__ = ['API4_0']
