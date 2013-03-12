rvbd.shark
==========

{module rvbd.shark}

This documentation assumes you are already familiar with the
Riverbed Shark Appliance,
specifically concepts like Capture Jobs and Views.
If you are not already familiar with these concepts,
see the [introduction to the Shark architecture](background)
and/or the [Shark manual](http://www.riverbed.com/us/products/cascade/cascade_shark_overview.php).

The primary interface to the Shark-related flyscript functionality
is the class `rvbd.shark.Shark`.
An instance of this object represents a connection to a Shark server,
and can be used to examine packet sources and existing views on the
server, as well as to configure and create new views, capture jobs, etc.

There are many more classes in the Shark libraries, representing
things like views, capture jobs, trace clips, etc.
But these should never be instantiated directly from scripts,
they are returned by methods on Shark objects.

{anchor sharkobjects ## Shark objects}

{class Shark}

The following methods provide general information about a Shark

{method get_serverinfo}
{method get_protocol_version}
{method get_logininfo}
{method get_stats}

* * *

The following methods are used to access [views](glossary.html#view).
Each of these methods returns a [view object](#viewobjects).

{method get_open_views}
{method get_open_view_by_handle}
{method create_view}
{method create_view_from_template}
   
* * *

The following methods are used to access packet sources
(e.g., to obtain an object that can be used as an argument to
{methodref create_view}, {methodref create_job}, etc...
The objects they return are described below in the section
[Packet source objects](#sourceobjects).

{method get_interfaces}
{method get_interface_by_name}
{method get_capture_jobs}
{method get_capture_job_by_name}
{method create_job}
{method get_clips}
{method create_clip}
{method get_trace_clip_by_description}
{method get_files}

* * *

The following methods are used to work directly with trace files
on the Shark appliance filesystem:

{method get_dir}
{method get_file}
{method exists}
{method create_dir}
{method create_multisegment_file}
{method create_merged_file}
{method upload_trace_file}

* * *

The following methods are used to access
[extractor fields](glossary.html#extractorfield).

{method get_extractor_fields}
{method find_extractor_field_by_name}
{method search_extractor_fields}


{anchor sourceobjects ## Packet source objects}

The objects described in this section are used to access packet sources.
None of these objects are directly instantiated from external code,
they are returned by methods on `Shark` or other routines.
Any of the objects in this section may be used as the `src`
argument to {methodref Shark.create_view}.

{anchor capturejobobjects ### Capture Job objects}

Capture job objects are used to work with capture jobs.
These objects are not instantiated directly but are returned from
{methodref Shark.get_capture_jobs}
and {methodref Shark.get_capture_job_by_name}.

{module rvbd.shark._source4 silent}
{class Job4 silent}

Capture job objects have the following properties:

{method name}
{method size_on_disk}
{method size_limit}
{method packet_start_time}
{method packet_end_time}
{method interface}
{method handle}

* * *

The following methods access information about a job:

{method get_status}
{method get_state}
{method get_stats}
{method get_index_info}

* * *

The following methods are useful for controlling a capture job:

{method start}
{method stop}
{method clear}

* * *

The following methods can be used to create and delete jobs,
though `create()` does the same thing as `Shark.create_clip()`.

{method create}
{method delete}

* * *

Finally, these methods are useful for creating trace clips and
for downloading raw packets from a capture job.

{method add_clip}
{method export}

{anchor traceclips ### Trace Clip objects}

Trace clip objects are used to work with trace clips.
These objects are not instantiated directly but are returned from
methods such as {methodref Shark.get_clips}.


{class Clip4 silent}

These methods provide a way to obtain clip objects, though it
is usually easier to use methods like `Shark.get_clips`.

{method get}
{method get_all}

Trace clip objects have the following properties:

<!-- document properties -->
{method description}
{method size}

{method add}
{method delete}

{anchor extractorobjects ## Extractor Field objects}

Extractor Field objects represent individual extractor fields.
These objects are returned by `Shark.get_extractor_fields`,
`Shark.find_extractor_field_by_name`, and `Shark.search_extractor_fields`.

<!--
replace ticks above with method references when ridl issues
worked out
{methodref Shark.get_extractor_fields},
{methodref Shark.find_extractor_field_by_name}, and
{methodref Shark.search_extractor_fields}.
-->

Each extractor field is a python
[`namedtuple`](http://docs.python.org/library/collections.html#collections.namedtuple)
with the following fields:

   * `name`: the name of the field, e.g., `ip.source_ip`
   * `desc`: a brief description of the field
   * `type`: a string describing the type of the field
     (e.g., integer, string ip address, etc.)


{anchor viewobjects ## View objects}

View objects are returned from `Shark.create_view`.

<!-- {methodref Shark.create_view} -->

A View object encapsulates everything needed to read data from
an existing view on a Shark.
Every view has one or more associated *outputs*.
For example, the standard "Bandwidth over time" view has separate
outputs for "bits over time", "bytes over time", and "packets over time".
In flyscript, a View object contains an associated Output object for
each output.  To read data from a view, you must first locate the
appropriate Output object, then use the method
!methodref Output.get_data .

View objects have the following methods:

{module rvbd.shark._view4 silent}
{class View4 silent}

{method is_ready}
{method get_progress}
{method get_timeinfo}
{method close}
{method get_legend}
{method get_data}
{method get_iterdata}
{method all_outputs}
{method get_output}


{anchor outputobjects ### Output objects}

{class Output4 silent}

{method get_legend}
{method get_data}
{method get_iterdata}


rvbd.shark.viewutils
====================

{module rvbd.shark.viewutils}

## Utilities for writing view data

{function print_data}
{function write_csv}

## Mixing multiple view outputs

{class OutputMixer}
{method add_source}
{method get_legend}
{method get_iterdata}

