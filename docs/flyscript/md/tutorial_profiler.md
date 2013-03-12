Profiler Tutorial
=================

This tutorial will walk through the main components of the FlyScript 
interfaces for [Cascade Profiler](glossary.html#profiler).  As with the 
[Shark Tutorial](tutorial.md) this discussion will assume a basic understanding
of the Python programming language.


The tutorial has been organized so you can follow it sequentially.  Throughout
the examples, you will be expected to fill in details specific to your
environment.  These will be called out using a dollar sign `$<name>` -- for
example `$sharkhost` indicates you should fill in the host name or IP address
of a Shark appliance.

Whenever you see `>>>`, this indicates an interactive session using the Python
shell.  The command that you are expected to type follows the `>>>`.  The
result of the command follows.  Any lines with a `#` are just comments to
describe what is happening.  In many cases the exact output will depend on your
environment, so it may not match precisely what you see in this tutorial.

Profiler Overview
-----------------

Cascade Profiler provides centralized reporting and analysis of the data
collected by other Cascade appliances (i.e., Gateway, Sensor, and Shark) and
Steelhead products on a single user interface.  Through the FlyScript
interfaces, this wealth of data becomes more easily accessible.

Profiler Objects
----------------

Profiler is made of up two primary objects,
[`Profiler`](profiler.html#profilerobjects), and
[`Report`](profiler.html#reportobjects).  `Profiler` provides the primary
interface to the appliance, handling initialization, setup, and communication
via REST API calls.  The `Report` object talks through `Profiler` to create new
reports and pull data from existing reports.  In most cases though, your
scripts will use a more helpful object tailored to the desired report, such as
a `TrafficSummaryReport` or a `TrafficOverallTimeSeriesReport`.  We'll cover
those shortly.

Outside of handling all the communication back and forth, `Profiler` also
handles all of the different report columns that could be desired.  It provides
a helpful interface to offer up available columns by report type, and ensures
that any chosen columns are in fact appropriate.  

With that brief overview, let's get started.

Profiler Startup
----------------

As with any Python code, the first step is to import the module(s)
we intend to use.
The FlyScript code for working with Profiler appliances resides in a
module called `rvbd.profiler`.
The main class in this module is [`Profiler`](profiler.html#profilerobjects).
This object represents a connection to a Profiler appliance.

To start, start python from the shell or command line:

    :::pycon
    $ python
    Python 2.7.3 (default, Apr 19 2012, 00:55:09) 
    [GCC 4.2.1 (Based on Apple Inc. build 5658) (LLVM build 2335.15.00)] on darwin
    Type "help", "copyright", "credits" or "license" for more information.
    >>> 

Once in the python shell, let's create a Profiler object:

    :::pycon
    >>> import rvbd.profiler
    >>> from rvbd.common.service import UserAuth
    >>> p = rvbd.profiler.Profiler('$hostname', auth=UserAuth('$username', '$password'))

The first argument is the hostname or IP address of the Profiler appliance.  The
second argument is a named parameter and identifies the authentication method
to use -- in this case, simple username/password is used.  OAuth 2.0 is supported as well, but
we will focus on basic authentication for this tutorial.

As soon as the Profiler object is created, a connection is established to the appliance,
 the authentication credentials are validated, and heirarchy of available columns is loaded. 
 If the username and password are not correct, you will immediately see an exception.  Also,
if this is the first time initializing a `Profiler` object, there will be a short delay
while all of the columns are fetched from the appliance and cached locally.

The `p` object is the basis for all communication with the Profiler appliance.
We can get some basic version information by simply looking at the 'version' attrubute:

    :::pycon
    >>> print p.version
    '10.1 (release 20130204_1200)'

Before moving on, exit the python interactive shell:

    :::pycon
    >>> [Ctrl-D]
    $

Generating Reports
------------------

Reports are the mechanisim to extract all the myriad of data from `Profiler` into
any format desired.  We will create a short script that provides a command-line interface
to generate reports on the fly.

Create a new file in a working directory of your choice, call it `myreport.py`,
and insert the following lines:


    :::python
    import rvbd.profiler

    from rvbd.common.service import UserAuth
    from rvbd.profiler.filters import TimeFilter
    from rvbd.profiler.report import TrafficSummaryReport

    import pprint

    # connection information
    username = '$username'
    password = '$password'
    auth = UserAuth(username, password)
    host = '$profiler_host'

    # create a new profiler instance
    p = rvbd.profiler.Profiler(host, auth=auth)

    # setup basic info for our report
    columns = [p.columns.key.host_ip,
               p.columns.value.avg_bytes,
               p.columns.value.network_rtt]
    sort_column = p.columns.value.avg_bytes
    timefilter = TimeFilter.parse_range("last 5 m")
    
    # initialize a new report, and run it
    report = TrafficSummaryReport(p)
    report.run('hos', columns, timefilter=timefilter, sort_col=sort_column)

    # grab the data, and legend (it should be what we passed in for most cases)
    data = report.get_data()
    legend = report.get_legend()

    # once we have what we need, delete the report from the profiler
    report.delete()

    # print out the top ten hosts!
    pprint.pprint(data[:10])

Be sure to fill in appropriate values for `$profiler_host`, `$username` and `$password`.
Run this script as follows and you should see something like the following:

    :::text
    $ python myreport.py
    [['10.100.6.12', 1733552.81667, ''],
     ['10.99.18.154', 1027017.35, 0.124],
     ['10.100.5.12', 814550.3, ''],
     ['10.100.5.13', 707320.527778, ''],
     ['10.100.6.14', 691441.777778, ''],
     ['10.100.6.10', 525593.25, ''],
     ['10.100.120.108', 455330.638889, ''],
     ['10.100.5.11', 443483.577778, ''],
     ['10.100.6.11', 385050.85, ''],
     ['10.100.201.33', 371349.105556, 0.046]]

We've created our first report!  Let's take a closer look at what we just did.  

    :::python
    import rvbd.profiler

    from rvbd.common.service import UserAuth
    from rvbd.profiler.filters import TimeFilter
    from rvbd.profiler.report import TrafficSummaryReport

    import pprint

These first few lines import our FlyScript modules and prepare them for use in
the rest of the script.  Common convention has custom modules (like Flyscript)
at the top, and built-in, or library modules at the bottom, such as pprint.


    :::python
    # connection information
    username = '$username'
    password = '$password'
    auth = UserAuth(username, password)
    host = '$profiler_host'

These are our login credentials.  We have them hard-coded into the script for 
an example here, but we will show how to have these supplied on the command line
shortly.

    :::python
    # create a new profiler instance
    p = rvbd.profiler.Profiler(host, auth=auth)

    # setup basic info for our report
    columns = [p.columns.key.host_ip,
               p.columns.value.avg_bytes,
               p.columns.value.network_rtt]
    sort_column = p.columns.value.avg_bytes
    timefilter = TimeFilter.parse_range("last 5 m")
    
    # initialize a new report, and run it
    report = TrafficSummaryReport(p)
    report.run('hos', columns, timefilter=timefilter, sort_col=sort_column)

Now things get interesting.  After initializing a new profiler instance,
we define some of the settings we want to use in our report.  
    `columns` is a list of column types we want to use in our report
    `sort_column` indicates which column profiler should use to sort on
    `timefilter` provides a time range for what time period the report should
        be limited to

Next, a new report instance is created, and the variables we just defined are
used to generate a report.

    :::python
    # grab the data, and legend (it should be what we passed in for most cases)
    data = report.get_data()
    legend = report.get_legend()

    # once we have what we need, delete the report from the profiler
    report.delete()

    # print out the top ten hosts!
    pprint.pprint(data[:10])

Here, the comments pretty well walk through what is happening.  Deleting
reports helps keep things tidy, but doesn't cause harm if they are left around.
After a period of time the appliance will cleanup any leftover reports after 24
hours.

Finally, since we included a column to sort on in our report request, we can
just limit the output to the first ten items to get the top ten.

Reporting Columns
-----------------

We chose only a small subset of the available columns for our example script.
We could include any columns applicable for this report type.  To help identify
which columns are available, we could start up a python console and try some of
the commands we showed in the [A Note About Columns](profiler_columns.html)
section, or we could use one of the provided example scripts called
`profiler_columns.py`.

Let's try using the example script and then we can enhance our example a bit 
more.

The example script should have been installed in one of your local `bin`
directories.  Try the following command to see if its on your path:

    :::text
    $ where profiler_columns.py

If that doesn't return a path, then you will need to add the directory it 
has been installed to to your shell's system path.

Now that you are setup, let's find some columns.

In our example, we glossed over the specific realm, centricity, and groupby that
was selected.  For a TrafficSummaryReport, those three items could be as follows:


    :::text
    |--------------+-------------------------------------------------------------|
    | `realm`      |  `traffic_summary`                                          |
    | `centricity` |  `hos`, `int`                                               |
    | `groupby`    |  any type except `time_host_user`, our example used `host`  |
    |--------------+-------------------------------------------------------------|


Enter the following:

    :::text
    $ profiler_columns.py -h
    Usage: profiler_columns.py PROFILER_HOSTNAME <options>

    Options:
      -h, --help            show this help message and exit

    [...text continues...]


And you will see all of the available options to the script.  One thing you
will see are options for host, username, and password.  Where we had
those hardcoded in our example, now we pass them as options to the script.

    :::text
    $ profiler_columns.py $hostname -u $username -p $password

This will just execute and print nothing out if it was able to successfully
connect.  Now, let's add our triplet information:

    :::text
    $ profiler_columns.py $hostname -u $username -p $password -r traffic_summary
      -c hos -g host --list-columns

    Key Columns        Label                  ID     
    -------------------------------------------------
    group_name         Group                  23     
    [...text continues...]

    Value Columns                    Label                               ID     
    ----------------------------------------------------------------------------
    avg_bytes                        Avg Bytes/s                         33     
    avg_bytes_app                    Avg App Bytes/s                     504    
    [...text continues...]


The available key and value columns will be presented.  If additional columns were 
desired for your report, select from this list.

We have chosen `host` as our groupby option, but to get a full list of what is available,
use the '--list-groupbys' option:

    :::text
    $ profiler_columns.py $hostname -u $username -p $password --list-groupbys

    GroupBy                      Id     
    ------------------------------------
    host_pair                    hop    
    ip_mac_pair                  ipp    
    port_group                   pgr    
    [...text continues...]

Note that the correct value to pass in the profiler_columns.py script is the
groupby name, not the Id.

Once you have found the set of columns you are interested in, you will now have
a means of including them in your report request.  The following syntax would
be one way to reference them:

    :::python
    columns = [p.columns.key.host_ip,
               p.columns.value.avg_bytes,
               p.columns.value.network_rtt]

Assuming `p` is a profiler instance, this would be one format to create
a list of key and value columns.  Keys are named `p.columns.key.<colname>` and
values are named `p.columns.value.<colname>`.

Additional discussion on columns can be found [here](profiler_columns.html).


Extending the Example
---------------------

As a last item to help get started with your own scripts, we will extend our example
with two helpful features: command-line options and table outputs.

Rather than show how to update your existing example script, we will post the new
script below, then walk through key differences that add the features we are looking for.

    :::python
    #!/usr/bin/env python

    from rvbd.profiler.filters import TimeFilter
    from rvbd.profiler.report import TrafficSummaryReport
    from rvbd.profiler.app import ProfilerApp
    from rvbd.common.utils import Formatter

    import optparse

    class ExampleApp(ProfilerApp):

        def add_options(self, parser):
            group = optparse.OptionGroup(parser, "Example Options")
            group.add_option('-r', '--timerange', dest='timerange', default=None,
                             help='Time range to limit report to, e.g. "last 5 m"')
            parser.add_option_group(group)

        def main(self):
            p = self.profiler

            report = TrafficSummaryReport(p)

            columns = [p.columns.key.host_ip,
                       p.columns.value.avg_bytes,
                       p.columns.value.network_rtt]
            sort_column = p.columns.value.avg_bytes

            timefilter = TimeFilter.parse_range(self.options.timerange)

            report.run('hos', columns, timefilter=timefilter, sort_col=sort_column)
            data = report.get_data()
            legend = report.get_legend()
            report.delete()

            header = [c.key for c in columns]
            Formatter.print_table(data[:10], header)

    ExampleReport().run()
    
Copy that code into a new file, and run it, you will find the same base set of 
options used for profiler_columns.py are now included in this script.  Primarily,
`hostname`, `username`, `password` are now all items to be passed to the script.

We also get a nicely formatted table, too!

First we needed to import some new items:

    :::python
    #!/usr/bin/env python

    from rvbd.profiler.filters import TimeFilter
    from rvbd.profiler.report import TrafficSummaryReport
    from rvbd.profiler.app import ProfilerApp
    from rvbd.common.utils import Formatter

    import optparse

That bit at the top is called a shebang, it tells the system that it should
execute this script using the program after the '#!'.  We are also importing
`ProfilerApp` and `Formatter` classes to help with our new updates.  The
built-in library `optparse` is used to parse command-line options.

    :::python
    class ExampleApp(ProfilerApp):

        def add_options(self, parser):
            group = optparse.OptionGroup(parser, "Example Options")
            group.add_option('-r', '--timerange', dest='timerange', default=None,
                             help='Time range to limit report to, e.g. "last 5 m"')
            parser.add_option_group(group)

This section begins the definition of a new class, which inherits from the
class ProfilerApp.  This is some of the magic of object-oriented programming,
a lot of functionality is defined as part of ProfilerApp, including the 
basics of authentication, and setting up a profiler instance, and we get all 
of that for _free_, just by inheriting from it.  In fact, we go beyond that,
and _extend_ its functionality by defining the function `add_options`.  Here,
we add a new option to pass in a timerange on the commandline.  

    :::python
        def main(self):
            p = self.profiler

            report = TrafficSummaryReport(p)

            columns = [p.columns.key.host_ip,
                       p.columns.value.avg_bytes,
                       p.columns.value.network_rtt]
            sort_column = p.columns.value.avg_bytes

            timefilter = TimeFilter.parse_range(self.options.timerange)

            report.run('hos', columns, timefilter=timefilter, sort_col=sort_column)
            data = report.get_data()
            legend = report.get_legend()
            report.delete()

            header = [c.key for c in columns]
            Formatter.print_table(data[:10], header)

    ExampleReport().run()

This is the main part of the script, and remains mostly unchanged from our previous
version.  Rather than create the profiler instance directly, that is now being
done for us as part of ProfilerApp.  We just need to reference it as shown.

The timefilter option is now being pulled from the command-line,
`self.options.timerange`, so we have one additional item that can be varied
from run to run.

Next, we have to run some small magic to pull out the key information from each
of the column objects.  The expression in the brackets for the header
assignment is called a [list
comprehension](http://docs.python.org/2/tutorial/datastructures.html#list-comprehensions).
Think of it like a condensed for-loop.  Once we have a header, we pass that along
with our data to the `Formatter.print_table` function, and that will print out 
our data nicely formatted into columns.

The last line calls the main run-loop as defined in the ProfilerApp class, 
and the rest should function as before.











