# Copyright (c) 2013 Riverbed Technology, Inc.
#
# This software is licensed under the terms and conditions of the 
# MIT License set forth at:
#   https://github.com/riverbed/flyscript/blob/master/LICENSE ("License").  
# This software is distributed "AS IS" as set forth in the License.



from rvbd.common.utils import DictObject

class ExtractorField(DictObject):
    @classmethod
    def get_all(cls, shark):
        return [cls(field) for field in shark.api.info.get_fields()]
