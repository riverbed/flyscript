# Copyright (c) 2013 Riverbed Technology, Inc.
#
# This software is licensed under the terms and conditions of the 
# MIT License set forth at:
#   https://github.com/riverbed/flyscript/blob/master/LICENSE ("License").  
# This software is distributed "AS IS" as set forth in the License.


import time
from rvbd.common import timeutils
from rvbd.shark import _interfaces
import json

def _to_native(string, legend_entry):
    """ convert `string` to an appropriate native type given `legend_entry` """
    if legend_entry.calculation == 'AVG':
        string, den = string.split(':', 1)
        denominator = int(den)
    else:
        denominator = 1
    
    if legend_entry.type.startswith('INT') \
      or legend_entry.type.startswith('UINT') \
      or legend_entry.type in ( 'TCP_PORT', 'UDP_PORT'):
        if legend_entry.base == 'DEC':
            baseval = 10
        elif legend_entry.base == 'HEX':
            baseval = 16
        else:
            raise ValueError('do not know how to handle integer base %s' %
                             legend_entry.base)
        return int(string, baseval) / denominator

    if legend_entry.type == 'DOUBLE':
        return float(string) / denominator

    if legend_entry.type == 'BOOLEAN':
        if string.lower() == 'false':
            return False
        elif string.lower() == 'true':
            return True
        else:
            raise ValueError('%s is not a boolean' % string)

    if legend_entry.type == 'ABSOLUTE_TIME':
        return timeutils.nsec_string_to_datetime(string)
    
    # XXX RELATIVE_TIME -> timedelta
    # XXX anything with IPv4 or ETHER?

    return string

class View4(_interfaces.View):
    def __init__(self, shark, handle, config=None):
        super(View4, self).__init__()
        
        self.shark = shark
        self.handle = handle
        self._outputs = {}

        if config is None:
            self.config = shark.api.view.get_config(handle)
        else:
            self.config = config

    def __repr__(self):
        d = {}
        d['source'] = self.config['input_source']['path']
        if 'info' in self.config and 'title' in self.config['info']:
            d['title'] = self.config['info']['title']
           
        return '<View ' + ' '.join(['%s="%s"' % (k, d[k]) for k in d.keys()]) + '>'

    @classmethod
    def _create_from_template(cls, shark, source, template, name=None, sync=True):
        #
        # Partial support. Just take the view in JSON format and apply it.
        #
        template_json = json.loads(template)
        #change the source
        template_json['input_source']['path'] = source.source_path
        res = shark.api.view.add(template_json)
        handle = res.get('id')
        view = cls(shark, handle, template_json)
        if not source.is_live() and sync:
            try:
                view._poll_completion()
                view._postapply()
            except:
                view.close()
                raise

        return view

    @classmethod
    def _create(cls, shark, source, columns, filters, sync=True, name=None,
                cfg_params=None, template=None, charts=None):

        parsed_columns = list()
        for column in columns:
            xfield = shark.find_extractor_field_by_name(str(column.field))
            column.field = xfield.id
            column.description = column.description or xfield.description
            parsed_columns.append(column)

        template = {
            'info' : {},
            'processors': [cls._format_columns(parsed_columns)],
            'parameters': {},
            'watches': [],
            'input_source': {
                'path': source.source_path,
                }
            }

        if filters is not None:
            template['input_source']['filters'] = filters

        template['input_source'].update(source.source_options)

        if name is not None:
            template['info']['title'] = name
            
        res = shark.api.view.add(template)

        handle = res.get('id')

        view = cls(shark, handle, template)
        return cls._process_view(view, source, sync)

    @staticmethod
    def _format_columns(columns):
        res = dict()
        res['keys'] = list()
        res['metrics'] = list()
        for i, column in enumerate(columns):
            key = 'keys' if column.key else 'metrics'
            value = dict([('field', str(column)), ('id', 'c'+str(i))])
            if key == 'metrics':
                value['operation'] = column.operation
            res[key].append(value)
        res['id'] = 'Flyscript_Processor'
        res['outputs'] = [dict(fields=list(dict(id='c'+str(i)) for i in range(len(columns))),
                                           id='OOUID_Flyscript')]
        return res


    @classmethod
    def _get_all(cls, shark):
        return [v['id'] for v in shark.api.view.get_all()]

    def get_timeinfo(self):
        """ Return a dictionary object with details about the time
        range covered by this view.  The returned object has the
        following entries:

        * `start`: the time of the first packet for which data is available
        * `end`: the end time of the last sample (XXX explain better)
        * `delta`: the size of each sample
        """
        res = self.shark.api.view.get_stats(self.handle)
        timeinfo = res.get('time_details')
        if 'delta' in timeinfo:
            timeinfo['delta'] = timeinfo['delta']
        return timeinfo

    def _poll_completion(self):
        while True:
            res = self.shark.api.view.get_stats(self.handle)
            status = res.get('state')
            if status == "DONE":
                break
            time.sleep(0.5)

    def _postapply(self):
        for processor in self.config['processors']:
            for output in processor['outputs']:
                self._outputs[output['id']] = Output4(self, output['id'])

        self.ti = self.get_timeinfo()

    def close(self):
        """Close this view on the server (which permanently deletes
        the view plus any associated configuration and output data)."""
        return self.shark.api.view.close(self.handle)

    def is_ready(self):
        """ Returns a boolean indicating whether data can be
        retrieved from this view or not.  If this function returns
        False, the view data is still being computed, its progress
        can be followed with the method get_progress().
        """
        stats = self.shark.api.view.get_stats(self.handle)

        return stats['state'] == 'DONE'

    def get_progress(self):
        """ For views applied to non-live sources (i.e., to trace clips
        or trace files), returns an integer between 0 and 100 indicating
        the percentage of the packet source that has been processed.
        Output data is not available on the view until this value reaches
        100% """

        stats = self.shark.api.view.get_stats(self.handle)
        if stats.state == 'DONE' or stats.input_size == 0:
            return 100
        if stats.input_size != 0:
            return int(float(stats.processed_size)/stats.input_size * 100)
        

class Output4(_interfaces.Output):
    def __init__(self, view, ouid):
        super(Output4, self).__init__()
        
        self.view = view
        self.id = ouid
        self._legend = self.get_legend()

    def get_legend(self):
        """ Return the legend for this output.  The legend consists of
        an ordered list of entries, one for each column of data in this
        output.  Each entry is a dictionary object with the following
        entries:

        * `name`: A short name for the field
        * `description`: A slightly longer, more descriptive name for the field
        * `field`: the name of the extractor field that produces this column
        * `calculation`: how data from multiple packets in a sample
          is aggregated (e.g., "SUM", "AVG", etc.)

        The following parameters are intended for internal shark use:

        * `type`
        * `id`
        * `base`
        * `dimension`
        """
        return self.view.shark.api.view.get_legend(self.view.handle, self.id)

    def _parse_output_params(self, start=None, end=None, delta=None,
                             aggregated=False, sortby=None,
                             sorttype="descending", fromentry=0, toentry=0):
        if start == None:
            start = self.view.ti.start

        if end == None:
            end = self.view.ti.end

        if aggregated and delta is not None:
            raise RuntimeError('cannot specify both delta and aggregated')

        if aggregated:
            # XXXCJ - adding delta is required because end is the *beginning*
            # of the last sample interval, not the end...
            delta = end - start + self.view.ti.delta
        elif delta == None:
            delta = self.view.ti.delta

        if hasattr(delta, 'seconds'):
            # looks like a timedelta
            # total_seconds() would be nice but was added in python 2.7
            delta = ((delta.days * 24 * 3600) + delta.seconds) * 10**9

        params = {
            'start': start,
            'end':   end,
            'delta': delta
            }

        if aggregated:
            params['aggregated'] = None

        if sortby:
            params.update({
                'sortby' : 'x'+str(sortby),
                'sorttype' : sorttype,
                'fromentry' : int(fromentry),
                'toentry' : int(toentry)
                })

        return params

    def get_iterdata(self, start=None, end=None, delta=None,
                     aggregated=False,
                     sortby=None, sorttype="descending",
                     fromentry=0, toentry=0):
        """
        Returns an iterator to the output data. This function is ideal for
        sequential parsing of the view data, because it downloads the
        dataset incrementally as it is accessed.

        `start` and `end` are `datetime.datetime` objects representing
        the earliest and latest packets that should be considered.
        If `start` and `end` are unspecified, the start/end of the
		underlying packet source are used.

        `delta` is a `datetime.timedelta` object that can be used to
        override the default data aggregation interval.  If this
        parameter is unspecified, the underlying view sample interval
        (which defaults to 1 second) is used.  If this parameter is
        specified, it must be an even multiple of the underlying
        view sample interval.

        If `aggregated` is True, the parameter `delta` is automatically
        computed to be the full extent of this request (i.e., the difference
        between the effective start and end times).  This is useful if
        you do not care about timeseries data (e.g., if the data from
        this view is to be plotted in a single chart that has no
        time component).

        The `sortby` parameter is one of the fields of the output (x1, x2 ...)

        The `sorttype` can be:
        * `ascending`: the output is sorted from smallest to largest
        * `descending`: the output is sorted largest to smallest

        The `fromentry` parameter represent the first sorted item we want
        to appear in the output.  0 means from the first one.

        The `toentry` parameter represent the last sorted item we want to
        appear in the output.  0 means all of them.
        """
        params = self._parse_output_params(start, end, delta, aggregated, sortby, sorttype, fromentry, toentry)

        res = self.view.shark.api.view.get_data(self.view.handle, self.id, **params)

        samples = res.get('samples')
        if samples is None:
            return

        for sample in samples:
            if 'vals' not in sample:
                continue

            sample['t'] = timeutils.nsec_string_to_datetime(sample['t'])
            def convert_one(vec):
                return [ _to_native(v, self._legend[i])
                         for i, v in enumerate(vec) ]
            sample['vals'] = [ convert_one(v) for v in sample['vals']]
            yield sample
