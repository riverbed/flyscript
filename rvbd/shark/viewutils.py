# Copyright (c) 2013 Riverbed Technology, Inc.
#
# This software is licensed under the terms and conditions of the 
# MIT License set forth at:
#   https://github.com/riverbed/flyscript/blob/master/LICENSE ("License").  
# This software is distributed "AS IS" as set forth in the License.



"""
This is a set of utility functions for working with views.
"""

from __future__ import absolute_import

import csv
import logging
from datetime import datetime, timedelta
from collections import namedtuple

from rvbd.common.utils import DictObject
from rvbd.common.timeutils import tzutc, max_width


class OutputMixer(object):
    """
    Helper class that blends multiple data streams (ie from View.get_data)
    into a single combined stream.
    For example, given a "Bandwidth Over Time" view with separate
    outputs for bytes and packets, this class can be used to create
    a single output stream with bytes and packets columns.

    Mixing is only supported on simple time-based views that do
    not include any keys (e.g., bandwidth over time, etc.)

    See examples/shark/readview.py for typical usage.
    """

    sourceobj = namedtuple('sourceobj', ['output', 'prefix', 'offset'])
    
    def __init__(self):
        """
        """
        self._sources = []
        self._legend = []

    def add_source(self, src, prefix=None):
        """ Add new source to mixer

            `src` is time-based view object
        """
        if prefix is None:
            prefix = 'o%d' % len(self._sources)

        obj = self.sourceobj(output=src, prefix=prefix, offset=len(self._legend))
        self._sources.append(obj)

        for field in src.get_legend():
            if field.dimension:
                raise NotImplementedError()
            
            # create a new record overriding some fields
            entry = DictObject(field)
            entry.id = 'x%d' % len(self._legend)
            entry.name = prefix + entry.name

            self._legend.append(entry)
        
    def get_legend(self):
        """ Return the legend for each of the source objects
        """
        return self._legend

    def get_iterdata(self, *args, **kwargs):
        """ Return a generator for the combined stream of outputs from each source object
        """
        threshold = timedelta(seconds=1)
        if 'time_thresh' in kwargs:
            threshold = kwargs['time_thresh']
            del kwargs['time_thresh']

        template = [None] * len(self._legend)
        iters = [s.output.get_iterdata(*args, **kwargs) for s in self._sources]
        inputs = [next(i, None) for i in iters]

        # XXX
        infinity = datetime(year=9999, month=12, day=31, tzinfo=tzutc())

        def get_sample_time(s):
            if s is None:
                return infinity
            return s.t

        def min_sample():
            return min(inputs, key=get_sample_time)

        ms = min_sample()
        sample_time = ms.t
        vals = list(template)
        while ms is not None:
            i = inputs.index(ms)
            inputs[i] = next(iters[i], None)

            delta = ms.t - sample_time
            if delta >= threshold:
                yield DictObject.create_from_dict(dict(t=sample_time,
                                                       vals=[vals],
                                                       processed_pkts=None,
                                                       unprocessed_pkts=None))
                
                sample_time = ms.t
                vals = list(template)

            assert len(ms.vals) == 1

            V = ms.vals[0]
            off = self._sources[i].offset
            for j in range(len(V)):
                vals[off + j] = V[j]
                
            ms = min_sample()

        yield DictObject.create_from_dict(dict(t=sample_time,
                                               processed_pkts=None,
                                               unprocessed_pkts=None,
                                               vals=[vals]))


def print_data(legend, stream, timeformat='%Y/%m/%d %H:%M:%S.%f',
               include_sample_times=True,
               widths=None, limit=None, line_prefix=''):
    """
    Print the data of a given view output to stdout.
    
    `widths` is an optional list of integers, specifying how
    many characters wide each column should be.  If it is not
    specified, reasonable defaults are chosen.

    If `limit` is specified, only the first `limit` rows are printed.

    `line_prefix` is a string that is printed at the start of every line.
    """

    labels = []
    if include_sample_times:
        labels.append('Time')
    labels += [f.name for f in legend]

    def get_width(field):
        if field.type in ('INT16', 'UINT16', 'TCP_PORT', 'UDP_PORT'):
            return 5
        if field.type in ('INT32', 'UINT32'):
            return 10
        if field.type in ('INT64', 'UINT64', 'RELATIVE_TIME'):
            return 20
        if field.type in ('FLOAT', 'DOUBLE'):
            return 20
        if field.type == 'BOOLEAN':
            return 5
        if field.type == 'IPv4':
            return 15
        if field.type in ('STRING', 'SHORT_STRING'):
            # TODO should this be smaller?
            return 64
        if field.type == 'ABSOLUTE_TIME':
            return max_width(timeformat)

        #XXX
        logging.warn('uh oh do not know width of %s' % field.type)
        return 10

    if widths is None:
        widths = []
        if include_sample_times:
            widths.append(max_width(timeformat))

        widths += [get_width(field) for field in legend]

    justified = [label.ljust(widths[i]) for i, label in enumerate(labels)]
    print line_prefix + '  '.join(justified)

    total = 0
    for s in stream:
        if 'gap_start' in s or 'gap_end' in s:
            continue

        base = [s.t.strftime(timeformat).ljust(widths[0])]
        for vec in s.vals:
            fields = base + [str(v).ljust(widths[i + 1]) for i, v in enumerate(vec)]

            print line_prefix + '  '.join(fields)

        total += 1
        if total == limit:
            return
    

def write_csv(filename, legend, stream, include_column_names=True, include_sample_times=True):
    """
    Saves the data of a view output to a comma separated values (csv) file.

    `legend` is an output legend, typically just the result
    of `output.get_legend()`

    `stream` is a series of data samples, typically the result
    of `output.get_data()` or `output.get_iterdata()`

    If `include_column_names` is True, the first line in the file
    will be a summary row indicating the fileds that the file contains.

    If `include_sample_times` is True, the first column will be a
    timestamp.
    """

    ofile = open(filename, "wb")
    writer = csv.writer(ofile)
        
    if include_column_names:
        labels = []
        if include_sample_times:
            labels.append('Time')

            labels += [ f.name for f in legend ]
        writer.writerow(labels)

    for s in stream:
        for v in s["vals"]:
            sample = []
            if include_sample_times:
                sample.append(s["t"])
            
            sample += [str(f) for f in v]
                    
            writer.writerow(sample)

    ofile.close()


class Cursor(object):
    """Given a live view returns only new samples for each get_data call
    """
    def __init__(self, output):
        self.output = output
        self._last_end = 0

    def get_data(self):

        source = self.output.view.source
        view = self.output.view

        ti = view.get_timeinfo()
        
        start = self._last_end
    
        data = self.output.get_data(start=start, end=ti.end)
        
        self._last_end = ti.end
        
        return data
