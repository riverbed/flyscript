rvbd.profiler
=============

{module rvbd.profiler}

All interaction with a Profiler requires an instance of rvbd.profiler.Profiler.
This class establishes a connection to the Profiler.  

{anchor columns ## Profiler Columns and Groupbys}

One of the key pieces of information `Profiler` keeps track of are all of the
different Column types, and under what context they are appropriate.  For
instance, if we are running a Traffic Summary report, then 'time' is not a
valid column of data since this report type organizes its information in other
ways.

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

The [Profiler tutorial](tutorial_profiler.html#a-note-about-columns) goes into
more detail on how these columns can be queried.

{anchor profilerobjects ## Profiler objects}

{module rvbd.profiler.profiler silent}

{class Profiler}

{method get\_columns}
{method get\_columns\_by\_ids}
{method search\_columns}
{method version}

{anchor reportobjects ## Base Report object}

{module rvbd.profiler.report silent}

{class Report}

{method run}
{method wait\_for\_complete}
{method status}
{method get\_data}
{method get\_iterdata}
{method get\_legend}
{method delete}

{anchor trafficsummaryreport ## Traffic Summary Report}

{class TrafficSummaryReport}

{method run}

{anchor trafficoverallreport ## Traffic Overall Time Series Report}

{class TrafficOverallTimeSeriesReport}

{method run}

{anchor trafficflowlistreport ## Traffic Flow List Report}

{class TrafficFlowListReport}

{method run}

{anchor identityreport ## Identity Report}

{class IdentityReport}

{method run}


