
# rvbd.common.timeutils

{module rvbd.common.timeutils}

## Handling time zones

{function ensure_timezone}
{function force_to_utc}

## Conversions

The Shark and Profiler APIs often represesent time as seconds
(or microseconds or nanoseconds) since the Unix epoch (January 1, 1970).
Many of the methods on Shark objects and Profiler objects accept
`datetime.datetime` objects but if you need to work with the raw
numbers, these routines may be useful:

{function datetime_to_seconds}
{function datetime_to_microseconds}
{function datetime_to_nanoseconds}
{function usec_string_to_datetime}
{function nsec_to_datetime}
{function usec_string_to_timedelta}
{function timedelta_total_seconds}

## Parsing dates and times

{class TimeParser}
{method *}

## Parsing time ranges

{function parse_timedelta}
{function parse_range}
