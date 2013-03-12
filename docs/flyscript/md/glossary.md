
FlyScript Glossary
==================

<a id="shark"></a>
Shark
: Short for [Riverbed Cascade Shark Appliance](http://www.riverbed.com/us/products/cascade/cascade_shark_overview.php)
A physical appliance or virtual machine that provides
continuous, high-speed packet capture and includes sophisticated
analytics (using the concept of a [view](#view))
for extracting many different kinds of data and statistics
from the captured traffic.

<a id="pilot"></a>
Pilot
: Short for [Riverbed Cascade Pilot](http://www.riverbed.com/us/products/cascade/cascade_pilot.php)
A desktop application for interacting with a [Shark](#shark) appliance.

<a id="view"></a>
view
: The object used within [Shark](#shark) for all packet analysis.
A view consists of a packet source, optional filters to limit
which packets are analyzed, and a set of statistics to extract
along with rules for how to organize those statistics.
Described in [A brief introduction to the Shark architecture](background.html)
and in the
[reference manual](shark.html#viewobjects).

<a id="extractor"></a>
extractor
: A software component that can *extract* information
([fields](#extractorfield))
about some protocol from packets.
Each extractor is identified by a short name.
E.g., the `tcp` extractor parses the headers in TCP
packets and extracts fields such as port numbers, flags, etc.

<a id="extractorfield"></a>
extractor field
: An individual piece of information that can be computed by
an [extractor](#extractor).
Each field has a short descriptive name and is
usually identified by the name of the extractor followed
by a doubled colon, and the field name.
For example, `tcp::source_port` or `http::uri`.

<a id="packetsource"></a>
packet source
: An object used as the input for a [view](#view).
Can be a [capture port](#captureport), [capture job](#capturejob),
[trace clip](#traceclip), or trace file.

<a id="captureport"></a>
capture port
: A physical network interface on a Shark appliancbe.
Typically connected to a mirrored (SPAN) port on a switch.

<a id="capturejob"></a>
capture job
: A long-running background task on a Shark appliance that
records some or all of the packets arriving on a
[capture port](#captureport) to disk.
Recorded packets are stored in an efficient indexed structure
for efficient retrieval during [view](#view) processing.
The term "capture job" is mildly overloaded -- it can refer
abstractly to the ongoing process of indexing and saving packets,
or it can refer specifically to the set of packets stored on
disk as part of a job.

<a id="traceclip"></a>
trace clip
: A filtered subset of the packets that have been stored as part
of a capture job.
A trace clip typically includes a time-based filter to limit
the clip to only those packets that fall within a specific
time interval.
Trace clips may be *locked*, in which case the packets in the
clip will not be deleted from disk even as ongoing capture jobs
need to delete old packets to reclaim space for new packets.

<a id="filter"></a>
filter  
: A predicate applied to a stream of packets to select a subset
of the packets.
Used to limit which packets from a source should be processed
by a [view](#view) or to limit which packets from a
[capture job](#capturejob) should be included in a
[trace clip](#traceclip).
