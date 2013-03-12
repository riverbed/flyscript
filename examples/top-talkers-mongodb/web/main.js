// TODO:
//  - normalize location better
//  - force layout parameters
//  - y scale gives powers of 10 that map to weird KB/MB/etc values
//  - control for # of nodes
//  - better "skin" around the whole thin

function format_bytes(n) {
    var suffix = [ 'B', 'KB', 'MB', 'GB', 'TB' ];
    for (var i in suffix) {
        if (n < 8*1024) {
            return Math.round(n).toString() + ' ' + suffix[i];
        }
        n /= 1024;
    }
    
    return Math.round(n).toString() + ' PB';
}

function format_rate(n) {
    n *= 8;
    var suffix = [ 'bps', 'kbps', 'Mbps', 'Gbps' ];
    for (var i in suffix) {
        if (n < 8*1024) {
            return Math.round(n).toString() + ' ' + suffix[i];
        }
        n /= 1024;
    }
    
    return Math.round(n).toString() + ' Tbps';
}

// convert a count of bytes into a nearby "round" number for
// use on a scale/legend/etc
function round_bytes(n) {
    var LN1024 = 10*Math.LN2;
    var units = Math.pow(1024, Math.floor(Math.log(n) / LN1024));
    var frac = n / units;
    if (frac > 800) {
        return units*1024;
    } else if (frac > 250) {
        return units * 500;
    } else if (frac > 60) {
        return units * 100;
    } else if (frac > 20) {
        return units * 50;
    } else if (frac > 6) {
        return units * 10;
    } else {
        return units;
    }
}

function ipconv(svg, w, h) {
    var ipc = {},
        nodes = [],
        nodeByAddr = {},
        links = [],
        node_on = { },
        link_on = { };

    var legend_width = 62;
    var visw = w - legend_width;

    var vis = svg.append('g')
        .attr('width', visw)
        .attr('height', h)
        .attr('clip-path', 'url(#boundary)');
    vis.append('clipPath')
        .attr('id', 'boundary')
      .append('rect')
        .attr('width', visw)
        .attr('height', h);

    var force = d3.layout.force()
        .on("tick", tick)
	.friction(0.5)
        .linkDistance(100)
        .charge(-350)
        .size([visw, h]);

    var radius_scale = d3.scale.sqrt()
            .range([2, 25]);
    function node_radius(n) { return radius_scale(n.bytes);  }

    var lwidth_scale = d3.scale.linear()
            .range([0, 12]);
    function link_width(link) {
        var w = Math.max(lwidth_scale(link.bytes), 2);
        return w.toString() + 'px';
    }

    var node_scale = svg.append('circle')
            .attr('class', 'scale')
            .attr('cx', visw + legend_width/2)
            .attr('cy', 40);
    var node_label = svg.append('text')
            .attr('class', 'scale')
            .attr('x', visw + legend_width/2)
            .attr('text-anchor', 'middle')
            .attr('y', 80);
    var link_scale = svg.append('line')
            .attr('class', 'scale')
            .attr('x1', visw + 5)
            .attr('x2', w - 5)
            .attr('y1', 100).attr('y2', 100)
            .attr('stroke-width', 0);
    var link_label = svg.append('text')
            .attr('class', 'scale')
            .attr('text-anchor', 'middle')
            .attr('x', visw + legend_width/2)
            .attr('y', 118);
    
    function update_scales(nodes) {
        var maxnode = d3.max(nodes, function(n) { return n.bytes; })
        var maxlink = d3.max(nodes, function(n) {
            return d3.max(n.links, function(l) { return l.bytes; } );
        } );

        radius_scale.domain([0, maxnode]);
        lwidth_scale.domain([0, maxlink]);

        var noderef = round_bytes(maxnode);
        node_scale.attr('r', radius_scale(noderef));
        node_label.text(format_bytes(noderef));

        var wref = round_bytes(maxlink);
        link_scale.attr('stroke-width', lwidth_scale(wref).toString() + 'px');
        link_label.text(format_bytes(wref));
    }

    function swidth(link) {
        var w = link.bytes / 400000;
        if (w < 1) { w = 1; }
        if (w > 10) { w = 10; }
        return (w.toString() + 'px');
    }

    var xscale = null, yscale = null;
    function tick() {
        var pad = 5;
        xscale = d3.scale.linear()
            .domain(d3.extent(nodes, function(n) { return n.x; }))
            .range([pad, visw-pad]);
        yscale = d3.scale.linear()
            .domain(d3.extent(nodes, function(n) { return n.y; }))
            .range([pad, h-pad]);

        vis.selectAll("line.link")
          .attr("x1", function(d) { return xscale(d.source.x); })
          .attr("y1", function(d) { return yscale(d.source.y); })
          .attr("x2", function(d) { return xscale(d.target.x); })
          .attr("y2", function(d) { return yscale(d.target.y); });

        vis.selectAll("circle.node")
            .attr("cx", function(d) { return xscale(d.x); })
            .attr("cy", function(d) { return yscale(d.y); });
    }

    ipc.reset = function() {
        nodes.forEach(function(n) {
            n.bytes = 0;
            n.links = [];
        } );
        links = [];
    };
    
    ipc.update = function(data) {
        // make sure we know about all nodes
        function addNode(a) {
            if (!(a in nodeByAddr)) {
                var node = nodeByAddr[a] = {
                    addr: a,
                    bytes : 0,
                    links: []
                };
                nodes.push(node);
            }
        }

        data.forEach(function(d) {
            addNode(d.client_address);
            addNode(d.server_address);
        } );
        
        // create/update links
        data.forEach(function(d) {
            var source = nodeByAddr[d.client_address],
                target = nodeByAddr[d.server_address],
                bytes = d.bytes;

            var link = null;
            source.links.forEach(function(l) {
                if ((l.source == source && l.target == target)
                    || (l.source == target && l.target == source)) {
                    link = l;
                }
            } );
            if (link == null) {
                link = { id: links.length, source: source, target: target, bytes: 0 };
                links.push(link);
                source.links.push(link);
                target.links.push(link);
            }
            
            link.bytes += bytes;
            source.bytes += bytes;
            target.bytes += bytes;
        } );
        
        update_scales(nodes);

        // Restart the force layout.
        force
            .nodes(nodes)
            .links(links)
            .start();

        // Update the nodes
        node = vis.selectAll("circle.node")
            .data(nodes.filter(function(n) { return (n.bytes > 0); } ), 
                  function(d) { return d.addr; })
            .attr("r", node_radius);
        
        // Enter any new nodes.
        var sel = node.enter().append("circle")
                .attr("class", "node")
                .attr("r", node_radius)
                .call(force.drag);
        
        for (var e in node_on) {
            sel.on(e, node_on[e]);
        }

        // Exit any old nodes.
        node.exit().remove();

        // Update the links
        link = vis.selectAll("line.link")
            .data(links, function(d) { return d.id; })
            .style('stroke-width', link_width);

        // Enter any new links.
        sel = link.enter().insert("line", ".node")
            .attr("class", "link")
            .style("stroke-width", link_width);
        for (var e in link_on) {
            sel.on(e, link_on[e]);
        }

        // Exit any old links.
        link.exit().remove();

        //console.log('on update, enter has ' + node.enter()[0].length
        //            + ', exit has ' + node.exit()[0].length);
    };

    ipc.nodeon = function(e, f) {
        node_on[e] = f;
        vis.selectAll('circle.node').on(e, f);
    };

    ipc.linkon = function(e, f) {
        link_on[e] = f;
        vis.selectAll('line.link').on(e, f);
    };

    ipc.xscale = function(x) { return xscale(x); }
    ipc.yscale = function(y) { return yscale(y); }

    return ipc;
}

function timeline(select, dismiss) {
    var ret = {};
    
    var g = null, width = 0, height = 0;
    var start_time = null, end_time = null;
    var tscale = null, brush = null;

    function selection() {
        if (brush == null || brush.empty()) {
            dismiss(ret);
        } else {
            var times = brush.extent();
            select(times[0], times[1], ret);
        }
    }

    function render_axes() {
        var xaxis = d3.svg.axis()
                .scale(tscale)
                .tickSize(4);
        g.append('svg:g')
            .attr('class', 'x axis')
            .attr('transform', 'translate(0,' + (height-30) + ')')
            .call(xaxis);
        
        g.append('g')
            .attr('class', 'brush')
            .call(brush)
          .selectAll('rect')
             .attr('height', height - 30);
    }

    function yformat(n) { return format_rate(n); }
    
    var yscale = null, path = null, samples = null;
    function render_points() {
        g.append('path')
            .data([samples])
            .attr('class', 'bwthumbnail')
            .attr('d', path);

        var yaxis = d3.svg.axis()
                .scale(yscale)
                .orient('right')
                .ticks(3)
                .tickSize(4)
                .tickFormat(yformat);
        g.append('svg:g')
            .attr('class', 'y axis')
            .attr('transform', 'translate(' + (width-50) + ',0)')
            .call(yaxis);
    }
        

    ret.draw = function(gelem, w, h, start, end) {
        g = gelem;
        width = w;
        height = h;
        start_time = start;
        end_time = end;

        tscale = d3.time.scale()
            .domain([start_time, end_time])
            .range([0, w-50]);

        brush = d3.svg.brush()
            .x(tscale)
            .on('brushend', selection);
        
        render_axes();
    }

    ret.redraw = function(gelem) {
        g = gelem;
        render_axes();
        render_points()
    }

    ret.set_samples = function(data) {
        samples = data;
        yscale = d3.scale.linear()
            .domain([0, d3.max(samples, function(d) { return d.y; })])
            .range([height-30, 0]);

        path = d3.svg.area()
            .interpolate('linear')
            .x(function(d) { return tscale(d.t); })
            .y0(height-30)
            .y1(function(d) { return yscale(d.y); });
        render_points();
    }
    
    ret.start = function() { return start_time; }
    ret.end = function() { return end_time; }

    return ret;
}

function tipmgr(selector) {
    var ret = {};

    var timers = {};
    var tip = selector.append('span')
            .attr('class', 'tooltip')
            .style('visibility', 'hidden');
    var p = tip.append('p');
    var cur_owner = null;

    ret.display = function(who, x, y, html) {
        if (timers[who] != null) { clearTimeout(timers[who]); }
        timers[who] = setTimeout(function() {
            timers[who] = null;
            cur_owner = who;
            p.html(html);
            tip.style('visibility', 'visible')
                .style('left', Math.max(0, x-90))
                .style('top', Math.max(0, y-86));
        }, 50);
    }

    ret.undisplay = function(who) {
        if (timers[who] != null) { clearTimeout(timers[who]); }
        timers[who] = setTimeout(function() {
            timers[who] = null;
            if (who != cur_owner) { return; }
            tip.style('visibility', 'hidden');
            cur_owner = null;
        }, 250);
    }

    return ret;
}

function build(selector, w, h, impl) {
    var ipch = Math.round(h * 0.6);

    var svg = selector
      .insert("svg", ".contenthere")
        .style('display', 'inline')
        .style('float', 'left')
        .attr('width', w)
        .attr('height', h);

    var max_hosts = 200;

//    var count = selector.append('input')
//            .attr('type', 'range')
//            .attr('min', 10)
//            .attr('max', 1000)
//            .attr('value', max_hosts)
//            .on('mouseup', function() { set_max_hosts($(this).val()); } );

    var ipc = ipconv(svg, w, ipch);

    var tipper = tipmgr(selector);
    
    ipc.nodeon('mouseover', function(n) {
        // XXX use d3.mouse?
        var x = Math.round(ipc.xscale(n.x));
        var y = Math.round(ipc.yscale(n.y));
        var html = n.addr + '<br/>' + format_bytes(n.bytes);
        tipper.display(n.addr, x, y, html);
    } );
    ipc.nodeon('mouseout', function(n) {
        tipper.undisplay(n.addr);
    } );

    ipc.linkon('mouseover', function(l) {
        var conn = l.source.addr + ' - ' + l.target.addr;
        var xy = d3.mouse(svg.node());
        tipper.display(conn, xy[0], xy[1],
                       conn + '<br/>' + format_bytes(l.bytes));
    } );
    ipc.linkon('mouseout', function(l) {
        var conn = l.source.addr + ' - ' + l.target.addr;
        tipper.undisplay(conn);
    } );
    
    var th = Math.round(h * 0.2);
    
    var timestack = [ timeline(time_select, time_dismiss) ]

    var timeg = [ null, null ]
    timeg[0] = svg.append('g')
        .attr('transform', 'translate(0,' + ipch + ')');
    
    function time_dismiss(series) {
        if (series == timestack[0]) {
            console.log('ignore empty click in top');
        } else if (series == timestack[1]) {
            timeg[0].remove();
            timestack.shift();

            timeg[0] = timeg[1];
            
            var trans = timeg[0]
              .transition()
                .attr('transform', 'translate(0,' + ipch + ')');
            
            if (timestack.length == 1) {
                timeg[1] = null;
            } else {
                trans.each('end', function(x) {
                    timeg[1] = svg.append('g')
                        .attr('transform', 'translate(0,' + (ipch+th) + ')');
                    timestack[1].redraw(timeg[1]);
                } );
            }

            ipc.reset();
            impl.data(timestack[0].start(), timestack[0].end(),
                      max_hosts, ipc.update);
        } else {
            console.log('XXX uh oh cannot find source of click');
            console.log('stack has ' + timestack.length);
        }
    }

    function time_select(start, end, series) {
        console.log('select from ' + start + ' to ' + end);
        ipc.reset();
        impl.data(start, end, max_hosts, ipc.update);
        
        var newtl = timeline(time_select, time_dismiss);
        if (series == timestack[0]) {
            if (timeg[1] != null) {
                timeg[1].remove();
            }

            timestack.unshift(newtl);

            timeg[1] = timeg[0]
            timeg[1]
              .transition()
                .attr('transform', 'translate(0,' + (ipch+th) + ')')
                .each('end', function(x) {
                    timeg[0] = svg.append('g')
                        .attr('transform', 'translate(0,' + ipch + ')');
                    newtl.draw(timeg[0], w, th, start, end);
                    impl.timeseries(start, end, w, newtl.set_samples);  } );

        } else if (series == timestack[1]) {
            // XXX timeg[0].empty() didn't work here...
            timeg[0].remove();
            timeg[0] = svg.append('g')
                .attr('transform', 'translate(0,' + ipch + ')');
            newtl.draw(timeg[0], w, th, start, end);

            timestack[0] = newtl;
            impl.timeseries(start, end, w, newtl.set_samples);
        } else {
            console.log('XXX uh oh cannot find source of click');
            return;
        }
    }

    function set_max_hosts(n) {
        console.log('set max hosts to ' + n);
        max_hosts = n;

        impl.data(timestack[0].start(), timestack[0].end(), max_hosts,
                  function(data) { ipc.reset(); ipc.update(data); } );
    }


    impl.timeinfo(function(start, end) {
        impl.data(start, end, max_hosts, ipc.update);

        timestack[0].draw(timeg[0], w, th, start, end);
        impl.timeseries(start, end, w, timestack[0].set_samples);
    } );
}

function node(url, outercallback) {
    var ret = {};

    // convert a Date object to an ISO 8601 string
    function format_date(d) {
        function pad(n, len) { var s = n.toString(); while (s.length < len) s = '0' + s; return (s); }
        return d.getUTCFullYear()
            + '-' + pad(d.getUTCMonth()+1, 2)
            + '-' + pad(d.getUTCDate(), 2)
            + 'T' + pad(d.getUTCHours(), 2)
            + ':' + pad(d.getUTCMinutes(), 2)
            + ':' + pad(d.getUTCSeconds(), 2)
            + '.' + pad(d.getUTCMilliseconds(), 3) + 'Z';
    }

    ret.timeinfo = function(callback) {
        $.getJSON(url + '/times', function(o) {
            callback(new Date(o.start), new Date(o.end));
        });
    }

    ret.timeseries = function(start, end, pts, callback) {
        var params = '?start=' + format_date(start)
                + '&end=' + format_date(end)
                + '&points=' + pts;
        $.getJSON(url + '/timeseries' + params, function (raw) {
            var data = raw.map(function(o) { return { t: new Date(o.t), y: o.y }; } );
            callback(data);
        } );
    }

    var pending = null;
    ret.data = function(start, end, count, callback) {
        if (pending != null) { pending.abort(); }
        var params = '?start=' + format_date(start)
                + '&end=' + format_date(end)
                + '&count=' + count;
        pending = $.getJSON(url + '/conversations' + params, function(args) {
            pending = null;
            callback(args);
        } );
    }

    outercallback(ret);
}

$(document).ready(function() {
    var w = 800;
    var h = 750;

    var callback = function(impl) { build(d3.select('body'), w, h, impl); }
    node('http://10.32.128.26:8080', callback);

} );
