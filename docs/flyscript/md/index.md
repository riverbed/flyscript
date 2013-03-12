FlyScript
=========

Welcome, this is the documentation for FlyScript.

Getting Started
---------------

- If you are new to Shark and Pilot or if you prefer reading 
  background material to work "bottom up", begin with
  [a brief introduction to the Shark architecture](background.html).
- If you don't have FlyScript installed, read about
  [installing FlyScript](install.html)
- If you are already familiar with Shark and want to start hacking,
  jump to [a FlyScript tutorial](tutorial_shark.html).
- If you want to jump into the Profiler side of things, head to
  [a Profiler FlyScript tutorial](tutorial_profiler.html).
- If you have a specific question about how to use the FlyScript libraries,
  see the [library reference](#library_reference)
- Hopefully if none of the above apply, you'll find what you need
  among the [other links](#other).


<a id="library_reference"></a>

FlyScript library reference
-------------------------

The documentation contained here covers public interfaces.
The FlyScript implementation contains a number of
*private* interfaces, these are all identified
using the standard Python convention of
a leading underscore character (_) in the names of modules,
classes or functions.

The public interfaces documented here are intended to be
stable -- we will do our best to keep them
backward-compatible so that code written using these modules
will continue to function even when new version of the libraries
are released in the future.
For these reasons,
you should generally try to use the public modules.
Nevertheless, the private modules are often useful as a reference
to how the system works.

### Class Hierarchy


All the FlyScript code resides in a top-level Python package called `rvbd`.
The structure of sub-packages looks like this:

- `rvbd`: the top-level FlyScript package
    - [`rvbd.common`](common.html): code for common functionality
      across Riverbed products (e.g., authentication, version queries, etc.)
    - [`rvbd.shark`](shark.html): code for interacting with
      Cascade Shark appliances
    - [`rvbd.profiler`](profiler.html): code for interacting Cascade Profilers

<a id="other"></a>

Other documentation
-------------------
   - [A brief introduction to the Shark architecture](background.html)
   - [Installing FlyScript](install.html)
   - [A FlyScript tutorial](tutorial_shark.html)
   - [A Profiler FlyScript tutorial](tutorial_profiler.html).
   - [Notes for FlyScript developers](hacking.html)

