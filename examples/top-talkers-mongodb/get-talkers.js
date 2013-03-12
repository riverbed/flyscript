#!node

// This application use Node.js to take data from Mongo DB in the
// format created by talkers-mongo.py and export it via a REST interface

var mongodb = require('mongodb');
var restify = require('restify');

var dbname = 'mydb';
var port = 8080;

var talkers = null, protocols = null, time_samples = null;
new mongodb.Db(dbname, new mongodb.Server("127.0.0.1", 27017, {}), {})
    .open(function (error, client) {
        if (error) throw error;
        talkers = new mongodb.Collection(client, 'talkers');
        protocols = new mongodb.Collection(client, 'protocols');
        time_samples = new mongodb.Collection(client, 'timeseries');
    } );


// format in iso 8601...
function format_date(d) {
    function pad(n, len) { var s = n.toString(); while (s.length < len) s = '0' + s; return (s); }
    return d.getFullYear()
        + '-' + pad(d.getMonth()+1, 2)
        + '-' + pad(d.getDate(), 2)
        + '-' + pad(d.getHours(), 2)
        + ':' + pad(d.getMinutes(), 2)
        + ':' + pad(d.getSeconds(), 2)
        + '.' + pad(d.getMilliseconds(), 3);
}

var server = restify.createServer();
server.use(restify.queryParser());

function times(req, res, next) {
    var response = {};
    var curs = talkers.find().sort({'$natural':1}).limit(1);
    curs.toArray(function(err, recs) {
        if (err) throw err;
        if (recs.length != 1) {
            return next(new restify.InternalError('got ' + recs.length + ' records from find'));
        }

        response.start = recs[0].time;
        
        var curs = talkers.find().sort({'$natural':-1}).limit(1);
        curs.toArray(function(err, recs) {
            if (err) throw err;
            if (recs.length != 1) {
                return next(new restify.InternalError('got ' + recs.length + ' records from find'));
            }
            
            response.end = recs[0].time;
            res.send(response);
        } );
    } );
}
server.get('/times', times);

// construct a set of queries that cover some time range
function build_queries(start, end) {
    // figure out first even hour after start and last even hour before end
    var hr_start;
    if (start.getMinutes() == 0 && start.getSeconds() == 0
        && start.getMilliseconds() == 0) {
        hr_start = start;
    } else {
        hr_start = new Date(start.getTime() + 60*60*1000);
        hr_start.setMinutes(0, 0, 0);
    }

    var hr_end = new Date(end.getTime())
    hr_end.setMinutes(0, 0, 0);
    
    // construct some appropriate mongodb queries
    var searches = [];
    if (hr_end > hr_start) {
        // small intervals from start to hr_start
        if (hr_start > start) {
            searches.push({time: { $gte: start, $lt: hr_start },
                           length: 5 * 1000 });
        }
        
        // hour intervals from hr_start to hr_end
        searches.push({time: { $gte: hr_start, $lt: hr_end },
                       length: 3600 * 1000 });
        
        // small intervals from hr_end to end
        if (end > hr_end) {
            searches.push({time: { $gte: hr_end, $lt: end },
                           length: 5 * 1000 });
        }
    } else {
        // just one search for the full range with small intervals
        searches.push({time: { $gte: start, $lt: end }, length: 5*1000 });
    }

    return searches;
};

function timeseries(req, res, next) {
    try {
        var start = new Date(req.query.start);
    } catch (err) {
        return next(new restify.InvalidArgumentError("Bad or missing start"));
    }
    
    try {
        var end = new Date(req.query.end);
    } catch (err) {
        return next(new restify.InvalidArgumentError("Bad or missing end"));
    }
    
    try {
        var points = parseInt(req.query.points);
    } catch (err) {
        return next(new restify.InvalidArgumentError("Bad or missing points"));
    }

    // total time between start and end in milliseconds
    var dt = end - start;
    
    // XXX smallest sampling interval in the database
    var interval = 5000;
    
    // figure out how many points to return
    points = Math.min(points, dt / interval);

    // now make dt be how much we need to aggregate.  round to an
    // even sampling interval
    var dt_intervals = Math.floor((dt/points) / interval);
    dt = interval * dt_intervals;
    

    // XXX map-reduce
    var samples = [ ];
    var start_tm = start.getTime();
    var tm = start_tm;
    while (tm < end.getTime()) {
        samples.push({time: new Date(tm), y: 0});
        tm += dt;
    }

    var samplen = (dt > 300*1000) ? 300 : 5;
    var divisor = samplen * dt_intervals;

    var search = time_samples.find({time: { $gte: start, $lt: end},
                                    length: samplen*1000 });
    search.each(function(err, rec) {
        if (err) {
            res.send(err);
        } else if (rec != null) {
            var i = Math.floor((rec.time.getTime() - start_tm) / dt);
            samples[i].y += rec.bytes / divisor;
        } else {
            res.send(samples);
        }
    } );
}
server.get('/timeseries', timeseries);

// utility object for aggregating a bunch of individual samples.
// call sample() repeatedly with the objects to aggregate,
// then call results() to get the aggregated results.
// XXX explain better
function aggregator(keyfunc, limit) {
    var ret = {};

    var complete = {};
    
    ret.sample = function(rec) {
        var key = keyfunc(rec);

        if (!(key in complete)) {
            var o = complete[key] = {};
            for (var field in rec) {
                if (field == 'length' || field == 'bytes') { continue; }
                o[field] = rec[field];
            }
            o.bytes = 0;
        }
        
        complete[key].bytes += rec.bytes;
    }

    ret.results = function() {
        var result = [];
        for (var key in complete) { result.push(complete[key]); }
        if (limit != undefined) {
            result.sort(function(a, b) { return b.bytes - a.bytes; } );
            result = result.splice(0, limit);
        }
        return result;
    }

    return ret;
}

function query(start, end, collection, keyfunc, count, callback) {
    // figure out first even hour after start and last even hour before end
    var hr_start;
    if (start.getMinutes() == 0 && start.getSeconds() == 0
        && start.getMilliseconds() == 0) {
        hr_start = start;
    } else {
        hr_start = new Date(start.getTime() + 60*60*1000);
        hr_start.setMinutes(0, 0, 0);
    }

    var hr_end = new Date(end.getTime())
    hr_end.setMinutes(0, 0, 0);
    
    // construct some appropriate mongodb queries
    var searches = [];
    if (hr_end > hr_start) {
        // small intervals from start to hr_start
        if (hr_start > start) {
            searches.push({time: { $gte: start, $lt: hr_start },
                           length: 5 * 1000 });
        }
        
        // hour intervals from hr_start to hr_end
        searches.push({time: { $gte: hr_start, $lt: hr_end },
                       length: 3600 * 1000 });
        
        // small intervals from hr_end to end
        if (end > hr_end) {
            searches.push({time: { $gte: hr_end, $lt: end },
                           length: 5 * 1000 });
        }
    } else {
        // just one search for the full range with small intervals
        searches.push({time: { $gte: start, $lt: end }, length: 5*1000 });
    }

    var ag = aggregator(keyfunc, count);
    
    function worker(searchlist) {
        //console.dir(searchlist[0]);
        var search = collection.find(searchlist.shift());
        search.each(function(err, rec) {
            if (err) {
                callback(err);
            } else if (rec != null) {
                ag.sample(rec);
            } else if (searchlist.length > 0) {
                worker(searchlist);
            } else {
                callback(ag.results());
            }
        } );
    }

    worker(searches);
}

//function get_talkers_slow(start, end, count, res) {
//    // figure out first even hour after start and last even hour before end
//    var hr_start;
//    if (start.getMinutes() == 0 && start.getSeconds() == 0
//        && start.getMilliseconds() == 0) {
//        hr_start = start;
//    } else {
//        hr_start = new Date(start.getTime() + 60*60*1000);
//        hr_start.setMinutes(0, 0, 0);
//    }
//
//    var hr_end = new Date(end.getTime())
//    hr_end.setMinutes(0, 0, 0);
//    
//    // construct some appropriate mongodb queries
//    var searches = [];
//    if (hr_end > hr_start) {
//        // small intervals from start to hr_start
//        if (hr_start > start) {
//            searches.push({time: { $gte: start, $lt: hr_start },
//                           length: 5 * 1000 });
//        }
//        
//        // hour intervals from hr_start to hr_end
//        searches.push({time: { $gte: hr_start, $lt: hr_end },
//                       length: 3600 * 1000 });
//        
//        // small intervals from hr_end to end
//        if (end > hr_end) {
//            searches.push({time: { $gte: hr_end, $lt: end },
//                           length: 5 * 1000 });
//        }
//    } else {
//        // just one search for the full range with small intervals
//        searches.push({time: { $gte: start, $lt: end }, length: 5*1000 });
//    }
//
//    var ag = aggregator(function(r) {
//        return r.client_address + '-' + r.server_address;
//    }, count);
//    
//    function worker(searchlist) {
//        //console.dir(searchlist[0]);
//        var search = talkers.find(searchlist.shift());
//        search.each(function(err, rec) {
//            if (err) {
//                res.send(err);
//            } else if (rec != null) {
//                ag.sample(rec);
//            } else if (searchlist.length > 0) {
//                worker(searchlist);
//            } else {
//                res.send(ag.results());
//            }
//        } );
//    }
//
//    worker(searches);
//}

function get_talkers_slow(start, end, count, res) {
    query(start, end, talkers,
          function(r) { return r.client_address + '-' + r.server_address },
          count, function(o) { res.send(o); } );
}


function get_talkers_mapreduce(start, end, count, res) {
    function ttmap() {
        emit({ client: this.client_address, server: this.server_address },
             this.bytes);
    }
    function ttreduce(k, vals) {
        var sum = 0;
        for (var i in vals) { sum += vals[i]; }
        return sum;
    }
    
    var opts = {
        out: { "inline": 1 },
        query: {"time": { $gt: start, $lt: end } },
        // XXX sort/limit
    };

    var search = talkers.mapReduce(ttmap, ttreduce, opts, function(err, results) {
        if (err) throw err;
        
        var data = results.map(function(o) { return {
            client_address: o._id.client,
            server_address: o._id.server,
            bytes: o.value }; } );

        // XXX sort/limit in db
        if (count > 0) {
            data.sort(function(a, b) { return b.bytes - a.bytes; } );
            data = data.splice(0, count);
        }
        res.send(data);
    } );
}

function conversations(req, res, next) {
    try {
        var start = new Date(req.query.start);
    } catch (err) {
        return next(new restify.InvalidArgumentError("Bad or missing start"));
    }
    
    try {
        var end = new Date(req.query.end);
    } catch (err) {
        return next(new restify.InvalidArgumentError("Bad or missing end"));
    }
    
    var count;
    try {
        count = parseInt(req.query.count);
    } catch (err) {
        count = 0;
    }
    
    get_talkers_slow(start, end, count, res);
    //get_talkers_mapreduce(start, end, count, res);
}
server.get('/conversations', conversations);

server.get('/protocols', function (req, res, next) {
    try {
        var start = new Date(req.query.start);
    } catch (err) {
        return next(new restify.InvalidArgumentError("Bad or missing start"));
    }
    
    try {
        var end = new Date(req.query.end);
    } catch (err) {
        return next(new restify.InvalidArgumentError("Bad or missing end"));
    }
    
    var count;
    try {
        count = parseInt(req.query.count);
    } catch (err) {
        count = 0;
    }
    
    query(start, end, protocols, function(r) { return r.application; },
          count, function(o) { res.send(o); } );
} );


function hello(req, res, next) {
    res.send('hello ' + req.params.name);
}

server.get('/hello/:name', hello);
server.head('/hello/:name', hello);

server.listen(port);
