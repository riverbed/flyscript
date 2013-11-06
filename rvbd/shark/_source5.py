# Copyright (c) 2013 Riverbed Technology, Inc.
#
# This software is licensed under the terms and conditions of the 
# MIT License set forth at:
#   https://github.com/riverbed/flyscript/blob/master/LICENSE ("License").  
# This software is distributed "AS IS" as set forth in the License.

from rvbd.common.exceptions import *
from rvbd.shark import _source4 as s4

class Job5(s4.Job4):
    @property
    def dpi_enabled(self):
        return self.data['config']['indexing']['dpi_enabled']

    @dpi_enabled.setter
    def dpi_enabled(self, value):
        self.data['config']['indexing']['dpi_enabled'] = value

    def save(self):
        data = self.data['config'].copy()
        state = self.get_status()['state']

        try:
            self.stop()
        except RvbdHTTPException:
            #it's all good, the job was already STOPPED
            pass
        self._api.update(self.id, data)
        if state != "STOPPED":
            self._api.state_update(self.id, {'state':state})
        

class Interface5(s4.Interface4):    

    def save(self):
        if self.shark.model == "vShark":
            self._api.update(self.id, {
                    'name': self.data.name,
                    'description': self.data.description
                    })
        else:
            # we are in a normal shark, we have to
            # delete things we cannot modify
            data = self.data.copy()
            del data['interface_components']
            del data['link']
            del data['board']
            del data['is_promiscuous_mode']
            del data['type']
            del data['id']
            self._api.update(self.id, data)
        self.update()

    @s4.Interface4.name.setter
    def name(self, value):
        self.data.name = value
