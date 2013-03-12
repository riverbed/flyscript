Tutorial
========

This tutorial will show you how to interface with a [Cascade Shark](glossary.html#shark) 
using the FlyScript Python SDK.  This tutorial assumes a basic understanding of Python 
(if not, see the [Beginner's Guide to Python](http://wiki.python.org/moin/BeginnersGuide)).
In addition, if you should be familiar with Shark and [Pilot](glossary.html#pilot).
If you have never used Shark and Pilot, it may be helpful to first read
[a brief introduction](background.html) to the Shark architecture.

The tutorial has been organized so you can follow it sequentially.  Throughout the 
examples, you will be expected to fill in details specific to your environment.  These
will be called out using a dollar sign `$<name>` -- for example `$sharkhost` indicates you
should fill in the host name or IP address of a Shark appliance.

Whenever you see `>>>`, this indicates an interactive session using the Python
shell.  The command that you are expected to type follows the `>>>`.  The result of
the command follows.  Any lines with a `#` are just comments to describe what 
is happening.  In many cases the exact output will depend on your environment,
so it may not match precisely what you see in this tutorial.

Shark Objects
-------------

As with any Python code, the first step is to import the module(s)
we intend to use.
The FlyScript code for working with Shark appliances resides in a
module called `rvbd.shark`.
The main class in this module is [`Shark`](shark.html#sharkobjects).
This object represents a connection to a Shark appliance.

To start, start python from the shell or command line:

    :::pycon
    $ python
    Python 2.7.3 (default, Apr 19 2012, 00:55:09) 
    [GCC 4.2.1 (Based on Apple Inc. build 5658) (LLVM build 2335.15.00)] on darwin
    Type "help", "copyright", "credits" or "license" for more information.
    >>> 

Once in the python shell, let's create a Shark object:

    :::pycon
    >>> import rvbd.shark

    >>> sk = rvbd.shark.Shark('$sharkhost', auth=rvbd.common.UserAuth('$username', '$password'))

The first argument is the hostname or IP address of the Shark appliance.  The
second argument is a named parameter and identifies the authentication method
to use -- in this case, simple username/password is used.

As soon as the Shark object is created, a connection is established to the Shark appliance,
and the authentication credentials are validated.  If the username and password are 
not correct, you will immediately see an exception.

The `sk` object is the basis for all communication with the Shark appliance, whether 
that is running views, checking configuration, or simply retrieving information
about the appliance.  Lets take a look at some basic information about the
shark that we just connected to:

    :::pycon
    >>> info = sk.get_serverinfo()
    
    >>> info['version']
    '10.0'
    
    # Returns the uptime in nanoseconds
    >>> info['uptime']
    1747209615759000
    
    # Returns the local_time in nanoseconds since Jan 1, 1970
    >>> info['local_time']
    1355803849818051000
    
    # Utility function to print convert this time into a datetime object...
    >>> from rvbd.common.timeutils import nsec_string_to_datetime

    # Now let's see what that time really is...    
    >>> str(nsec_string_to_datetime(info['local_time']))
    '2012-12-18 04:10:49.818051+00:00'

    # Let's see the entire info structure
    >>> info
    {'build_time': 'Nov 27 2012 16:10:50',
     'build_type': 'Final',
     'build_variant': 'TurboCap',
     'has_webui': True,
     'hostname': 'shark',
     'internal_version': '10.0.1005.0241',
     'local_time': 1355803849818051000,
     'protocol_version': '4.0',
     'start_time': 1354056640202292000,
     'system_type': 'Linux',
     'timezone': '-0800',
     'uptime': 1747209615759000,
     'version': '10.0',
     'view_version': '3.5',
     'webui_SSL': True,
     'webui_port': 443,
     'webui_root_path': '/'}

Before moving on, exit the python interactive shell:

    :::pycon
    >>> [Ctrl-D]
    $

Views
-----

Let's create our first script.  We're going write a simple script that creates
and applies a view on the first capture interface on our shark appliance.

This script will use packets in a pcap file.  To start, download a copy of 
[tutorial-1.pcap](tutorial-1.pcap) and save it in a new directory.

In the same directory as the pcap file, create a file called `view.py` 
and insert the following code:

    :::python
    import rvbd.shark
    from rvbd.shark.types import Value, Key
    import pprint
    
    # Fill these in with appropriate values
    sharkhost = '$sharkhost'
    username = '$username'
    password = '$password'
    
    # Open a connection to the appliance and authenticate
    sk = rvbd.shark.Shark(sharkhost, auth=rvbd.common.UserAuth(username, password))
    
    # First, upload our pcap file, if it's not already present
    if not sk.exists('/{0}/tutorial-1.pcap'.format(username)):
        homedir = sk.get_dir(username)
        tracefile = homedir.upload_trace_file('tutorial-1.pcap', 'tutorial-1.pcap')
    else:
        # If it's already there, just grab a handle to it
        tracefile = sk.get_file('/{0}/tutorial-1.pcap'.format(username))
    
    # Now create a view on this tracefile.  Start by selecting the columns of interest
    columns = [ Key(sk.columns.ip.address),
                Value(sk.columns.generic.packets),
                Value(sk.columns.generic.bytes) ]
    
    view = sk.create_view(tracefile, columns, name="tutorial view")
    
    # Retrieve the data
    data = view.get_data(aggregated=True)
    
    # Close the view
    view.close()
    
    # Print the output to the screen
    printer = pprint.PrettyPrinter(2)
    printer.pprint(data)

Be sure to fill in appropriate values for `$sharkhost`, `$username` and `$password`.
Run this script as follows and you should see something like the following:

    :::text
    $ python view.py
    [ { 'p': 388,
        't': datetime.datetime(2012, 12, 18, 12, 41, 33, 808202, tzinfo=tzutc()),
        'vals': [ ['11.1.1.90', 384, 255208],
                  ['173.194.75.106', 13, 1025],
                  ['216.34.181.45', 48, 39486],
                  ['184.31.179.172', 263, 195713],
                  ['74.125.226.220', 10, 1446],
                  ['208.70.199.49', 16, 2960],
                  ['23.66.231.51', 3, 198],
                  ['23.66.231.41', 7, 1253],
                  ['74.125.226.219', 16, 10555],
                  ['11.1.1.100', 2, 100],
                  ['204.93.70.150', 6, 2472]]}]

Let's take a closer look at what this script is doing.  The first few
lines are simply importing a few libraries that we'll be using:

    :::python
    import rvbd.shark
    from rvbd.shark.types import Value, Key
    import pprint

Next, we create a Shark object that establishes our connection to the target
appliance:

    # Open a connection to the appliance and authenticate
    sk = rvbd.shark.Shark(sharkhost, auth=rvbd.common.UserAuth(username, password))

This next section ensures that the pcap file that we want to analyze is up
on the appliance.

    :::python
    # First, upload our pcap file, if it's not already present
    if not sk.exists('/{0}/tutorial-1.pcap'.format(username)):
        homedir = sk.get_dir(username)
        tracefile = homedir.upload_trace_file('tutorial-1.pcap', 'tutorial-1.pcap')
    else:
        # If it's already there, just grab a handle to it
        tracefile = sk.get_file('/{0}/tutorial-1.pcap'.format(username))

At this point, the variable `tracefile` is a handle to the tracefile 'tutorial-1.pacap' 
that now present on the filesystem of the shark appliance. 

Next, we're going to actually create a view.  The first step is to select the set
of columns that we're interested in collecting:

    :::python
    columns = [ Key(sk.columns.ip.address),
                Value(sk.columns.generic.packets),
                Value(sk.columns.generic.bytes) ]

Shark supports numerous columns, and any column can be either a key column or a value column. 
Each row of data will be aggregated according to the set of key columns selected.  The 
value columns define the set of additional data to collect per row.  In this
example, we are asking to collect total packets and bytes for each IP address
seen in the pcap file.

Now create the view:

    :::python
    view = sk.create_view(tracefile, columns, name="tutorial view")
    
The first argument is the `packet source`.  When creating a view, the packet source can 
be one of four types of source objects: Interfaces, Trace Files, Capture Jobs
and Trace Clips.  A packet source can be live (e.g. a Shark capture port) or 
offline (e.g. a Trace Clip). General information about packet sources can be 
found in the [glossary](glossary.html).  See the [Python classes](shark.html#sourceobjects)
for details on how to work with the various source types as objects.

We can now use the view object to get data:

    :::python
    # Retrieve the data
    data = view.get_data(aggregated=True)

Data Objects
------------

The data object returned by the `get_data()` method contains the key and value columns 
requested, but also returns a few addition fields of meta data.

First, edit `view.py` and comment out the line that closes the view - add a '#' in front of `view.close()`:

    :::python
    # Close the view
    # view.close()

Now rerun the python script, but pass the `-i` argument to python to drop into an interactive
shell after running the script.  This will allow us to inspect the data that
was returned:

    :::pycon
    $ python -i view.py
    [ { 'p': 388,
        't': datetime.datetime(2012, 12, 18, 12, 41, 33, 808202, tzinfo=tzutc()),
        'vals': [ ['11.1.1.90', 384, 255208],
                  ['173.194.75.106', 13, 1025],
                  ['216.34.181.45', 48, 39486],
                  ['184.31.179.172', 263, 195713],
                  ['74.125.226.220', 10, 1446],
                  ['208.70.199.49', 16, 2960],
                  ['23.66.231.51', 3, 198],
                  ['23.66.231.41', 7, 1253],
                  ['74.125.226.219', 16, 10555],
                  ['11.1.1.100', 2, 100],
                  ['204.93.70.150', 6, 2472]],
        'value_count': 11}]
    >>>

We are now back at the python prompt, but all the variables assigned in the 
script are available to use for inspection.

First of all, note that the data object itself is a list of length 1:

    :::pycon
    >>> type(data)
    <type 'list'>

    >>> len(data)
    1

Each element in the list is called a `sample`.  We only have a single sample 
in this output - we'll cover more about samples later. 

A sample has 3 fields in it:

   - `p` - number of packets processed
   - `t` - timestamp of the beginning of the sample interval
   - `vals` - the key and value columns that were requested when the view was created

For this output, there is only one sample.  In the sample interval, 388
packets were processed.  The sample interval started as 12:41:33.808202 on Dec 18, 2012.

The `get_data()` method supports a number of additional options that
allow us to change how the data is returned. For example, we can ask
for the data to be sorted by bytes, the third column (index 2 starting
from 0):

    :::pycon
    >>> data = view.get_data(aggregated=True, sortby=2)

    # Look only at the 'vals' for the first and only sample (index 0)
    >>> printer.pprint(data[0]['vals'])
    [ ['11.1.1.90', 384, 255208],
      ['184.31.179.172', 263, 195713],
      ['216.34.181.45', 48, 39486],
      ['74.125.226.219', 16, 10555],
      ['208.70.199.49', 16, 2960],
      ['204.93.70.150', 6, 2472],
      ['74.125.226.220', 10, 1446],
      ['23.66.231.41', 7, 1253],
      ['173.194.75.106', 13, 1025],
      ['23.66.231.51', 3, 198],
      ['11.1.1.100', 2, 100]]

Or sort by packets (index 1), in ascending order:

    :::pycon
    >>> data = view.get_data(aggregated=True, sortby=1, sorttype="ascending")

    >>> printer.pprint(data[0]['vals'])
    [ ['11.1.1.100', 2, 100],
      ['23.66.231.51', 3, 198],
      ['204.93.70.150', 6, 2472],
      ['23.66.231.41', 7, 1253],
      ['74.125.226.220', 10, 1446],
      ['173.194.75.106', 13, 1025],
      ['208.70.199.49', 16, 2960],
      ['74.125.226.219', 16, 10555],
      ['216.34.181.45', 48, 39486],
      ['184.31.179.172', 263, 195713],
      ['11.1.1.90', 384, 255208]]

Note that the list of columns has the same order as requested when the view was created.

Aggregated or Not
-----------------

Notice that with each call to `get_data()`, we are passing the argument `aggregated=True`.
This argument indicates that we are not interested in time-series data, we want 
only care about the `Key()` columns that were used to create the view.  But what happens
if you set `aggregated=False`?

Normally all data on the Shark appliance is collected in time intervals and will
return that data by time.  This is what happens when `aggregrated=False`.  The 
time interval must be set when you create the view, but by default it is 1 second.

Let's see what the output would look like when it's not aggregated.  Change the True to False 
and rerun the script:

    :::pycon
    >>> data = view.get_data(aggregated=False)

The output should look like this:

    :::pycon
    >>> len(data)
    6

    >>> printer.pprint(data)
    [ { 'p': 15,
        't': datetime.datetime(2012, 12, 18, 12, 41, 33, 808202, tzinfo=tzutc()),
        'vals': [['11.1.1.90', 13, 1025], ['173.194.75.106', 13, 1025]]},
      { 'p': 289,
        't': datetime.datetime(2012, 12, 18, 12, 41, 34, 808202, tzinfo=tzutc()),
        'vals': [ ['11.1.1.90', 289, 193299],
                  ['216.34.181.45', 44, 39222],
                  ['184.31.179.172', 203, 139597],
                  ['74.125.226.220', 10, 1446],
                  ['208.70.199.49', 6, 1028],
                  ['23.66.231.51', 3, 198],
                  ['23.66.231.41', 7, 1253],
                  ['74.125.226.219', 16, 10555]]},
      { 'p': 60,
        't': datetime.datetime(2012, 12, 18, 12, 41, 35, 808202, tzinfo=tzutc()),
        'vals': [['184.31.179.172', 60, 56116], ['11.1.1.90', 60, 56116]]},
      { 'p': 3,
        't': datetime.datetime(2012, 12, 18, 12, 41, 36, 808202, tzinfo=tzutc()),
        'vals': [['11.1.1.90', 2, 380], ['208.70.199.49', 2, 380]]},
      { 'p': 11,
        't': datetime.datetime(2012, 12, 18, 12, 41, 37, 808202, tzinfo=tzutc()),
        'vals': [ ['11.1.1.100', 2, 100],
                  ['11.1.1.90', 10, 2904],
                  ['208.70.199.49', 2, 332],
                  ['204.93.70.150', 6, 2472]]},
      { 'p': 10,
        't': datetime.datetime(2012, 12, 18, 12, 41, 39, 808202, tzinfo=tzutc()),
        'vals': [ ['208.70.199.49', 6, 1220],
                  ['11.1.1.90', 10, 1484],
                  ['216.34.181.45', 4, 264]]}]

Where as before `data` was a list of length one, it now has multiple
samples.  Each sample provides a snapshot of the key and value columns requested for
one interval starting at the time indicated by `t`. 

Looking in detail at the second sample:

    :::pycon
    >>> data[1]
    {'p': 289,
     't': datetime.datetime(2012, 12, 18, 12, 41, 34, 808202, tzinfo=tzutc()),
     'vals': [['11.1.1.90', 289, 193299],
      ['216.34.181.45', 44, 39222],
      ['184.31.179.172', 203, 139597],
      ['74.125.226.220', 10, 1446],
      ['208.70.199.49', 6, 1028],
      ['23.66.231.51', 3, 198],
      ['23.66.231.41', 7, 1253],
      ['74.125.226.219', 16, 10555]]}

    >>> from rvbd.common.timeutils import *

    >>> data[1]['t'].strftime("%x %X")
    '12/18/12 12:41:34'

From this, we can tell that the sample covers the time from 12:41:34 to 12:41:35. 
(Note, to be precise, it actually covers from 12:41:34.808202 to 12:41:35.808202)
Within that interval 289 packets were processed and host 11.1.1.90 was involved in each and
every one of those packets accountoing for 193,299 bytes.

Let's take a look at the time range covered for each sample using a little Python magic.

    :::python
    >>> for sample in data:
    ...     print "Start: {0}, processed {1} packets".format(sample['t'].strftime("%x %X"), sample['p'])
    ...
    Start: 12/18/12 12:41:33, processed 15 packets
    Start: 12/18/12 12:41:34, processed 289 packets
    Start: 12/18/12 12:41:35, processed 60 packets
    Start: 12/18/12 12:41:36, processed 3 packets
    Start: 12/18/12 12:41:37, processed 11 packets
    Start: 12/18/12 12:41:39, processed 10 packets

> Note: do not type in the leading `... ` for the second and third
lines above.  After typing in the first line (`for sample`), and press
enter, Python will prompt you with `... ` for additional commands to
be executed for each iteration of the for loop.  You *must* type in
the 4 leading spaces before `print`.  At the end of the second
line, when you press enter it will prompt again with `... `,
indicating that you may enter additional commands.  In this case, we are
done so just press enter again, and Python will execute the for loop.
See [Dive Into Python - 2.5: Indenting Code](http://www.diveintopython.net/getting_to_know_python/indenting_code.html) for more information.

Notice that 12:41:38 is missing?  This is not a bug -- it just means that there were no
packets in the trace file during that sample interval, so there is no data to show.

Before continuing on, exit from the Python shell:

Before moving on, exit the python interactive shell:

    :::pycon
    >>> [Ctrl-D]
    $

Processing View Data
--------------------

Ok, now let's enhance the script to do a bit more:

   * compute average packet size (bytes / packets)
   * select hosts sending small packets (< 100 bytes)
   * for each host, print out the protocols in use

Open up view.py and add a new import to the top of the file:

    :::python
    import rvbd.shark
    from rvbd.shark.types import Value, Key
    from rvbd.shark.filters import *            # <--- Add this line
    import pprint

Next, uncomment the line the closes the view, delete the lines that print the data 
and replace the last section that prints the output to the screen with the following code:

    :::python
    # Close the view
    view.close()

    # Print the output to the screen            # <--- delete these three lines
    # printer = pprint.PrettyPrinter(2)
    # printer.pprint(data)

    # Compute avg bytes/packet, and resort      # <--- add the rest of this to the script
    rows = data[0].vals
    filtered_rows = [row for row in rows if (row[2] / row[1]) < 100]

    print "{0} Hosts are sending small packets (avg size < 100 bytes)".format(len(filtered_rows))
    for row in filtered_rows:
        print "{0}\t{1} bytes/pkt".format(row[0], row[2] / row[1])

    # Now create a new view that breaks out the protocol / port for each host above
    columns = [ Key(sk.columns.ip.protocol_name),
                Value(sk.columns.generic.packets),
                Value(sk.columns.generic.bytes) ]

    for row in filtered_rows:
        filters = [SharkFilter('ip.address="{0}"'.format(row[0]))]
        view = sk.create_view(tracefile, columns, filters, name="tutorial view - ip {0}".format(row[0]))
        data = view.get_data(aggregated=True)
        view.close()

        print "\nHost {0}".format(row[0])
        for pp_row in data[0].vals:
            print "{0}\t{1} bytes/pkt".format(pp_row[0],pp_row[2] / pp_row[1])

Save your changes and rerun the script (without the `-i` this time):

    :::text
    $ python view.py
    3 Hosts are sending small packets (avg size < 100 bytes)
    173.194.75.106	78 bytes/pkt
    23.66.231.51	66 bytes/pkt
    11.1.1.100	50 bytes/pkt

    Host 173.194.75.106
    TCP	78 bytes/pkt

    Host 23.66.231.51
    TCP	66 bytes/pkt

    Host 11.1.1.100
    ICMP	50 bytes/pkt

This script now runs a total of 4 views, the first view collects bytes and packets per IP address.
The subsequent views collect bytes and packets per protocol for an individual IP address
using a `SharkFilter`:

    :::python
    filters = [SharkFilter('ip.address="{0}"'.format(row[0]))]

A SharkFilter allows you to form complex expressions using operators and various fields
within a packet.

Existing Views
--------------

In the above examples, we have always created a new view from scratch, then
closed that view when we were done.  Often, a view may be created and 
running for a longer period of time.  For example, a live view is 
continually being updated as new traffic is received.  Views may also be
created using the `Pilot` application.

If there are already open views on the Shark appliance,
we can access them with the `get_open_views()` method.  Start up a new
Python shell and lets give this a try:

    :::pycon
    $ python
    Python 2.7.3 (default, Apr 19 2012, 00:55:09) 
    [GCC 4.2.1 (Based on Apple Inc. build 5658) (LLVM build 2335.15.00)] on darwin
    Type "help", "copyright", "credits" or "license" for more information.

    >>> import rvbd.shark

    >>> sk = rvbd.shark.Shark('$sharkhost', auth=rvbd.common.UserAuth('$username', '$password'))

    >>> views = sk.get_open_views()

    >>> views
    [<View source="fs/admin/noon.cap" title="Bandwidth Over Time">,
     <View source="fs/admin/noon.cap" title="TCP Flags by Protocol Over Time"
     <View source="fs/admin/tutorial-1.pcap">]

> Your appliance will likely show a different set of open views.  You should
at least see the tutorail-1.pcap view in the list.  

This method returns a list of objects, one representing each open
view.  We can get information about the time interval covered by the
view with the `get_timeinfo()` method:

    :::pycon
    >>> view = views[0]

    >>> view.get_timeinfo()
    {'delta': 1000000000, 'end': 1195590918719742000, 'start': 1195590481719742000}

This method returns a struct with 3 fields:

   * `start` and `end` indicate the timestamp of the first and last samples
   covered by the view
   * `delta` specifies the interval of time covered by a single sample
   in nanoseconds (defaults to 1 second)

For a view applied to a `trace clip` or a static file,
the `start` and `end` times will be fixed for a particular view.
For a view applied to a `capture port` or the virtual device
associated with a `capture job`, the `end` time will be
regularly updated as new packets arrive and are processed.

The views created above by the view.py script had only a single `output`
associated with it.  In general, 
a view may have multiple outputs associated with it.
Each output has the same basic structure - it contains a list of samples as
described above.

In this example, we are looking at the "TCP Flags by Protocol Over Time"
view which has separate outputs for the different flags that can appear
in TCP headers.
In `Pilot`, these outputs show up as separate graphs.
In FlyScript, there is a separate `output object <outputobjects>`
for each output, we can get at them with the `all_outputs()` method:

    :::pycon
    >>> view.all_outputs()
    [<view output OUID_Fin>,
     <view output OUID_Psh>,
     <view output OUID_Urg>,
     <view output OUID_Ack>,
     <view output OUID_Rst>,
     <view output OUID_Syn>]

> The number of outputs returned is based upon the view selected.  The view
created above as part of the tutorial only has a single output at index 0. 
Note that if the view you have selected does not have 6 outputs, adjust the 
array index below.

Let's use the helper routine `print_data()` in the module
`rvbd.shark.viewutils` to print the data in the view to the console:

    :::pycon
    >>> from rvbd.shark.viewutils import print_data

    # Grab the 6th output corresponding to the SYN flag, adjust as necessary
    # for the view selected
    >>> output = view.all_outputs()[5]

    >>> output
    <view output OUID_Syn>

    >>> print_data(output.get_legend(), output.get_data())
    Time                        Protocol            Packets
    2012/05/10 12:31:37.502796  http                1      
    2012/05/10 12:31:51.502796  http                1      
    2012/05/10 12:32:51.502796  http                1      
    2012/05/10 12:32:56.502796  http                1      
    2012/05/10 12:33:16.502796  https               1      
    2012/05/10 12:33:27.502796  http                2      
    2012/05/10 12:33:51.502796  http                1      
    ...

Note that the method `View.get_data()` simply calls the get_data() function for 
the first output of a view.  As such, the following are equivalent:

    :::pycon
    # Retrieving the data for the first output:
    >>> output0 = view.get_output(0)
    >>> data0 = output0.get_data()

    # Equivalent shortcut from the view object:
    >>> data = view.get_data()

