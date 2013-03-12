#!/usr/bin/env python

# Copyright (c) 2013 Riverbed Technology, Inc.
#
# This software is licensed under the terms and conditions of the 
# MIT License set forth at:
#   https://github.com/riverbed/flyscript/blob/master/LICENSE ("License").  
# This software is distributed "AS IS" as set forth in the License.



'''
This script applies a "top talkers" view periodically to a given
capture job and stores the results in Mongo DB.  It is intended to
be used together with the Node.js script get-talkers.js in this
directory which exports the date from Mongo via a REST interface.
The web page in examples/web/static/talkers/ reads data via this
interface and renders an interactive top talkers visualization.
'''

import rvbd.shark
from rvbd.common.service import UserAuth
from rvbd.common.timeutils import TimeParser
import pymongo

import time
from datetime import datetime, timedelta
from dateutil import tz

import optparse
parser = optparse.OptionParser()
parser.add_option('--shark', action='store', dest='sharkhost',
                  default='tigershark',
                  help='Hostname of shark appliance')
parser.add_option('-j', '--job', action='store', dest='jobname',
                  default='Client side',
                  help='Name of capture job to use')
parser.add_option('--db', action='store', dest='dbname', default='mydb',
                  help='Name of database to use')
parser.add_option('-c', '--clean', action='store_true', dest='clean',
                  default=False,
                  help='Clean the database collections first')
parser.add_option('-s', '--start', dest='start_time', default=None,
                  help='start searching from the given time')
parser.add_option('-e', '--end', dest='end_time', default=None,
                  help='stop searching at the given time')
parser.add_option('-l', '--limit', dest='limit', default=None,
                  help='limit number of samples in each interval')

(options, args) = parser.parse_args()
if len(args) > 1:
    parser.error('unexpected arguments')
    

# things that can't be changed
talkers_collection = 'talkers'
timeseries_collection = 'timeseries'
protocols_collection = 'protocols'
query_interval = timedelta(hours=1)
report_interval = timedelta(seconds=5)

report_ms = int(report_interval.total_seconds() * 1000)
query_ms = int(query_interval.total_seconds() * 1000)

conn = pymongo.Connection()
db = conn[options.dbname]

if options.clean:
    print 'dropping collections: %s, %s, %s' \
          % (talkers_collection, timeseries_collection, protocols_collection)
    db.drop_collection(talkers_collection)
    db.drop_collection(timeseries_collection)
    db.drop_collection(protocols_collection)
        

if talkers_collection in db.collection_names():
    talkers = db[talkers_collection]
else:
    print 'initializing new talkers collection'
    talkers = db.create_collection(talkers_collection, capped=True,
                                   size=800*1024*1024)
    talkers.create_index([('time', pymongo.ASCENDING),
                          ('length', pymongo.ASCENDING)])

if protocols_collection in db.collection_names():
    protocols = db[protocols_collection]
else:
    print 'initializing new protocols collection'
    protocols = db.create_collection(protocols_collection, capped=True,
                                     size=200*1024*1024)
    protocols.create_index([('time', pymongo.ASCENDING),
                            ('length', pymongo.ASCENDING) ])

if timeseries_collection in db.collection_names():
    timeseries = db[timeseries_collection]
else:
    print 'initializing new timeseries collection'
    timeseries = db.create_collection(timeseries_collection, capped=True,
                                      size=20*1024*1024)
    talkers.create_index([('time', pymongo.ASCENDING),
                          ('length', pymongo.ASCENDING)])


def round_time(dt):
    ''' round a datetime to the most recent even hour'''
    return dt.replace(minute=0, second=0, microsecond=0)

timefmt = '%m/%d/%Y %H:%M:%S'

if options.start_time is not None:
    start_time = TimeParser().parse(options.start_time)
elif talkers.count() == 0:
    start_time = round_time(datetime.now())
    print 'no start time, starting from %s' % start_time.strftime(timefmt)
else:
    last = talkers.find(sort=[('$natural', pymongo.DESCENDING)])
    last_tm = last[0]['time'] + timedelta(microseconds=1000*last[0]['length'])
        
    start_time = round_time(last_tm)
    
    print 'last record came at %s, starting at %s' % (str(last_tm), start_time.strftime(timefmt))

shark = rvbd.shark.Shark(options.sharkhost, auth=UserAuth('admin', 'admin'))
job = shark.get_capture_job_by_name(options.jobname)

def find_in_legend(l, n):
    for i in range(len(l)):
        if l[i].field == n:
            return i
    raise KeyError()

from rvbd.shark.types import Value, Key

def get_top_talkers(start, end):
    fields = ( Key('tcp.client_ip'),
               Key('tcp.server_ip'),
               Value('generic.bytes') )
               
    print 'querying talkers in %r-%r' % (start, end)
    with shark.create_view(job, fields, start_time=start, end_time=end) as view:
        o = view.all_outputs()[0]
        fields = o.get_legend()

        fmap = ( ( find_in_legend(fields, 'tcp.client_ip'), 'client_address'),
                 ( find_in_legend(fields, 'tcp.server_ip'), 'server_address'),
                 ( find_in_legend(fields, 'generic.bytes'), 'bytes' ) )

        samples = []
        for s in o.get_iterdata(delta=report_interval):
            for v in s['vals']:
                D = { 'time': s['t'], 'length': report_ms }
                for i, n in fmap:
                    D[n] = v[i]
                samples.append(D)

    if len(samples) == 0:
        return
    
    times = {}
    rolledup = {}
    for s in samples:
        if s['time'] not in times:
            times[s['time']] = 0
        times[s['time']] += s['bytes']

        key = (s['client_address'], s['server_address'])
        if key not in rolledup:
            rolledup[key] = 0
        rolledup[key] += s['bytes']

    if options.limit is not None:
        samples.sort(key = lambda s: s['bytes'], reverse=True)
        samples = samples[:int(options.limit)]
        samples.sort(key = lambda s: s['time'])

    print 'inserting %d samples covering %r-%r' % (len(samples), start, end)
    talkers.insert(samples)

    rolledsamples = [ { 'client_address': k[0],
                        'server_address': k[1],
                        'bytes': rolledup[k],
                        'time': start,
                        'length': query_ms }
                      for k in rolledup ]
    print 'inserting %d rolled up samples' % len(rolledsamples)
    talkers.insert(rolledsamples)

    ts = [ dict(time=t, bytes=times[t], length=report_ms) for t in times ]
    ts.sort(key=lambda d: d['time'])
    timeseries.insert(ts)

    interval = timedelta(minutes=5)
    short_ts = [ ]
    short_ts.append({'time': ts[0]['time'], 'bytes': 0,
                     'length': int(interval.total_seconds() * 1000) })
    samp_end = ts[0]['time'] + interval

    for samp in ts:
        if samp['time'] >= samp_end:
            short_ts.append({'time': samp['time'], 'bytes': 0,
                             'length': short_ts[0]['length']})
            samp_end = samp['time'] + interval
        short_ts[-1]['bytes'] += samp['bytes']
        
    timeseries.insert(short_ts)

    fields = ( Key('generic.application'), Value('generic.bytes') )
    print 'querying protocols in %r-%r' % (start, end)
    with shark.create_view(job, fields, start_time=start, end_time=end) as view:
        o = view.all_outputs()[0]
        fields = o.get_legend()

        fmap = ( ( find_in_legend(fields, 'generic.application'), 'application' ),
                 ( find_in_legend(fields, 'generic.bytes'), 'bytes') )

        samples = []
        for s in o.get_iterdata(delta=report_interval):
            for v in s['vals']:
                D = { 'time': s['t'], 'length': report_ms }
                for i, n in fmap:
                    D[n] = v[i]
                    
                samples.append(D)

    if len(samples) == 0:
        return
        
    rolledup = {}
    for s in samples:
        if s['application'] not in rolledup:
            rolledup[s['application']] = 0
        rolledup[s['application']] += s['bytes']

    if options.limit is not None:
        samples.sort(key = lambda s: s['bytes'], reverse=True)
        samples = samples[:int(options.limit)]

    print 'inserting %d proto samples covering %r-%r' % (len(samples), start, end)
    protocols.insert(samples)

    rolledsamples = [ { 'application': app,
                        'bytes': rolledup[app],
                        'time': start,
                        'length': query_ms }
                      for app in rolledup ]
    print 'inserting %d rolled up proto samples' % len(rolledsamples)
    protocols.insert(rolledsamples)
    

if options.end_time is None:
    end_time = None
else:
    end_time = TimeParser().parse(options.end_time)

while end_time is None or start_time < end_time:
    end = start_time + query_interval

    pause = (end - datetime.now()).total_seconds()
    if pause > 0:
        print 'next query interval ends at %s, pausing for %d seconds' % (end.strftime(timefmt), pause)
        time.sleep(pause)
    
    get_top_talkers(start_time, end)
    start_time = end
