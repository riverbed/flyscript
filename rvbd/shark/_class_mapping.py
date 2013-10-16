# Copyright (c) 2013 Riverbed Technology, Inc.
#
# This software is licensed under the terms and conditions of the 
# MIT License set forth at:
#   https://github.com/riverbed/flyscript/blob/master/LICENSE ("License").  
# This software is distributed "AS IS" as set forth in the License.


"""This files describes the class mapping for each Shark protocol version
"""

from __future__ import absolute_import


class Classes(object):
    def __getattr__(self, attr):
        try:
            return self.__getattribute__(attr)
        except AttributeError:
            raise NotImplementedError('API version {0} is not available for this shark version.'.format(attr))

        
class Classesv4(Classes):
    def __init__(self):
        #we must import here to let automatic registration
        #of classes working. If we import at module level
        #we will have multiple registration of classes between
        #different versions
        import rvbd.shark._source4 as v4
        from rvbd.shark import _view4, _fs, _settings4, _fields4

        self.Interface = v4.Interface4
        self.Job = v4.Job4
        self.Clip = v4.Clip4
        self.View = _view4.View4

        self.Directory = _fs.Directory4
        self.File = _fs.File4
        self.TraceFile = _fs.TraceFile4
        self.MultisegmentFile = _fs.MultisegmentFile4
        self.MergedFile = _fs.MergedFile4

        self.ExtractorField = _fields4.ExtractorField
        self.Settings = _settings4.Settings4


class Classesv5(Classesv4):
    def __init__(self):
        super(Classesv5, self).__init__()
        import rvbd.shark._source5 as v5
        from rvbd.shark import _settings5
        self.Job = v5.Job5
        self.Interface = v5.Interface5
        self.Settings = _settings5.Settings5

        
def path_to_class(shark, path):
    mapping = dict(
        interfaces=shark.classes.Interface,
        fs=shark.classes.File,
        clips=shark.classes.Clip,
        jobs=shark.classes.Job
    )
    p = path.split('/', 1)
    if p[0] == 'jobs':
        # lookup by name instead of id
        return mapping[p[0]].get(shark, None, p[1])
    else:
        return mapping[p[0]].get(shark, p[1])

