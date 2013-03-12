A Note About Columns
====================

As mentioned earlier, one of the key pieces of information `Profiler` keeps
track of are all of the different Column types, and under what context they are
appropriate.  For instance, if we are running a Traffic Summary report, then
'time' is not a valid column of data since this report type organizes its
information in other ways.

Column types fall into two categories: keys and values.  Keys are column types
that represent the primary organization/grouping of the data, and values are
all of the different calculations that can be made.

The contexts for columns that are available are defined by three values: realm,
centricity, and groupby.  A breakdown of how these three inter-relate is shown
in the following table:

        |-----------------------------+------------+----------------------|
        | realm                       | centricity | groupby              |
        |-----------------------------+------------+----------------------|
        | traffic_summary             | hos,int    | all (except thu)     |
        | traffic_overall_time_series | hos,int    | tim                  |
        | traffic_flow_list           | hos        | hos                  |
        | identity_list               | hos        | thu                  |
        |-----------------------------+------------+----------------------|

As FlyScript develops further, this table and the available permutations will expand.

Let's take a look at how these work a little more closely.  Startup a new
instance of your Python interpreter, similar to before:
  
    :::pycon
    $ python
    Python 2.7.3 (default, Apr 19 2012, 00:55:09) 
    [GCC 4.2.1 (Based on Apple Inc. build 5658) (LLVM build 2335.15.00)] on darwin
    Type "help", "copyright", "credits" or "license" for more information.

    >>> import rvbd.profiler
    >>> from rvbd.common.service import UserAuth
    >>> p = rvbd.profiler.Profiler('$hostname', auth=UserAuth('$username', '$password'))

Now, lets investigate which columns are available for a specific type of report:

    :::pycon
    >>> realms = ['traffic_summary']
    >>> centricities = ['hos']
    >>> groupbys = ['hos']

    >>> columns = p.search_columns(realms=realms, centricities=centricities, groupbys=groupbys)
    
Here we have setup three local variables, and passed them as arguments to the `search_columns` 
method on our `profiler` object.  Note the brackets around each of the definitions we made,
those mean we created a `list` object for all three variables.  In this case, the list
contains only a single object, the string.

Let's take a look at what that method returned:

    :::pycon
    >>> len(columns)
    146

So, a total of 146 columns can be chosen for a report with those three filters!  Note your 
specific number may vary here, depending on the specific version of Profiler you are running.

    :::pycon
    >>> columns[:2]
    [<rvbd.profiler._types.Column(cid=31, key=total_pkts, iskey=False label=Total Packets)>,
     <rvbd.profiler._types.Column(cid=427, key=in_avg_conns_rsts, iskey=False label=Avg Resets/s (Rx))>]

This command uses [slicing](http://stackoverflow.com/questions/509211/the-python-slice-notation) 
to show only the first two elements of the list.  Notice these are objects themselves,
with quite a bit of information associated with each one.  These objects are used extensively
within `profiler`, but the main thing to keep in mind is that you can refer to columns
by their text value (the 'key' attribute), by index value (the 'cid' attribute in the example
above), or by the actual object itself.

Another way to access one of the columns, is through the `profiler` object as an attribute:

    :::pycon
    >>> print p.columns.value.total_pkts
    <rvbd.profiler._types.Column(cid=31, key=total_pkts, iskey=False label=Total Packets)>

    >>> print p.columns.key.time
    <rvbd.profiler._types.Column(cid=98, key=time, iskey=True label=Time)>

To see the complete list of all column keys you could enter the following:

    :::pycon
    >>> print p.columns.keys
    [...long list of objects...]

    >>> print p.columns.values
    [...long list of objects...]

