# Copyright (c) 2013 Riverbed Technology, Inc.
#
# This software is licensed under the terms and conditions of the 
# MIT License set forth at:
#   https://github.com/riverbed/flyscript/blob/master/LICENSE ("License").  
# This software is distributed "AS IS" as set forth in the License.

from _settings4 import Settings4
from _interfaces import loaded

#there is no functional need to put this class nested into Settings5 class
#leaving it as module object to simplify reuse and modularizzation
class Dpi(object):

    def __init__(self, shark):
        #take reference of the shark
        self.shark = shark
        #caches the settings for dpi
        self.data = None

class ProfilerExport(Settings4.ProfilerExport):
    def _load(self):
        self.data = self.shark.api.settings.get_profiler_export()
        #for backward compatibility with Settings4
        self._settings = self.data

    def _ensure_loaded(self):
        if self.data is None or len(self.data) == 1:
            self._load()

    def _lookup_profiler(self, address):
        for p in self.data.profilers:
            if p.address == address:
                return address
        raise ValueError('No profiler with addredss {0} has been found in the configuration'.format(address))

    @loaded
    def enable_dpi(self, address):
        p = self._lookup_profiler(address)
        p['dpi_enabled'] = True
        self._update()
    
    @loaded
    def disable_dpi(self, address):
        p = self._lookup_profiler(address)
        p['dpi_enabled'] = False
        self._update()

        

class Settings5(Settings4):
    '''Interface to various configuration settings on the shark appliance. Version 5.0 API'''    

    def __init__(self, shark):
        super(Settings5, self).__init__(shark)
        self.dpi = Dpi(shark)
        self.profiler_export = ProfilerExport(shark)
