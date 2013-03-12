Installing FlyScript - Step by Step
===================================

This page provides step-by-step instructions for installing FlyScript under two 
different scenarios, virtualenv and system-wide:

* Install with virtualenv on [Linux/Mac](#installvenv-linuxmac) / 
  [Windows](#installvenv-win) - Install the FlyScript package
  and all necessary supporting files in a local directory.  This
  does not affect the system installation. 

* System Install on [Linux/Mac](#installsys-linuxmac) / 
  [Windows](#installsys-win) - Install the FlyScript package 
  into the system-wide site-packages directory

Dependencies
============

* Python version 2.6.X or 2.7.X
    * Download latest from [here](http://python.org/download/)
* (optional) virtualenv
    * Download latest from [here](http://www.virtualenv.org/en/latest/)


Installation in a Virtual Environment
=====================================


This method installs the FlyScript package along will all supporting files
into local subdirectory of your choice.  This method does not
require root or admin access and does not interfere with the system
installation of Python.  As such, it is usually the recommended method
unless you have a need to install it globally for all users.  

<a id="installvenv-linuxmac"></a>

Linux/Mac
---------

You must already have Python installed on your system to continue.
If not, please install Python from [python.org](http://www.python.org/getit/)
or ask your system adminstrator to install Python.  You will need
either Python 2.6.x or 2.7.x to use the FlyScript SDK.

1. Check that Python is installed and running the approriate version:

        :::text
        $ python -V
        Python 2.7.3

2. Download a copy of the flyscript tar file.
   The tar file will be named "flyscript-&lt;version&gt;.tar.gz".  The rest of 
   these instructions will assume version 0.5.

3. Extract the FlyScript package in a suitable location (this will 
   put the files in the current users home directory):

        :::text
        $ cd ~
        $ tar xvzf flyscript-0.5.tar.gz
        flyscript-0.5/
        flyscript-0.5/docs/
        ...

4. Create a virtual environment.  This will be the location where 
   a private copy of all the necessary packages are installed.  Note
   that this step requires access to the internet and previously installed
   virtualenv package:

        :::text
        $ virtualenv myflyscript
        Installing setuptools............................done.
        Installing pip.....................done.

5. Install the FlyScript package into your new environment:

        :::text
        $ cd flyscript-0.5
        $ ~/myflyscript/bin/python setup.py install
        ....
        ....
        Installed /Users/cwhite/myflyscript/lib/python2.7/site-packages/flyscript-0.5-py2.7.egg
        Processing dependencies for flyscript==0.5
        Finished processing dependencies for flyscript==0.5

6. Test your installation by running a simple test:

        :::text
        $ python flyscript-0.5/examples/about.py
        Package 'flyscript' version 0.5 installed

        Path to source:
          /Users/cwhite/myflyscript/lib/python2.7/site-packages/flyscript-0.5-py2.7.egg/rvbd

        Modules provided:
          rvbd.common
          rvbd.extras
          rvbd.pilot
          rvbd.profiler
          rvbd.shark
          rvbd.stingray

You can now run any of the tools in the bin directory just by calling them at the command line. 

If you write your own scripts, be sure to execute them with ~/myflyscript/bin/python rather
than just python.  This will use the private copy of python and pull in the all the packages
that were just installed locally within that environment.

For more information about virtualenv, see [virtualenv website](http://www.virtualenv.org/en/latest).

<a id="installvenv-win"></a>

Windows
-------

1. If you don't yet have Python installed on your system, download
   Python from [python.org](http://www.python.org/getit/).  Be sure to pick the
   installer from the Python 2 section (2.7.3 at the time this
   document is written) since FlyScript does not currently support
   Python 3.  Download the installer for your platform (32bit
   vs. 64bit).

2. Download a copy of the flyscript tar file.
   The tar file will be named "flyscript-&lt;version&gt;.tar.gz".  The rest of 
   these instructions will assume version 0.5.

3. Double click on the FlyScript package to extract the contents.
   Select a suitable location such as "C:\".  This will extract the
   package contents to "C:\flyscript-0.5\"

4. Create a virtual environment.  This will be the location where a
   private copy of all the necessary packages are installed.  Note
   that this step requires access to the internet and the virtualenv
   package to have been installed.  Open a command
   prompt and type the following commands:

        :::text
        > c:\Users\home
        > virtualenv myflyscript
        Installing setuptools............................done.
        Installing pip.....................done.

6. Complete installation of the FlyScript package into the Python
   site-packages directory.  Open a command prompt and type the following commands:

        :::text
        > cd c:\flyscript-0.5
        > c:\myflyscript\Scripts\python setup.py install
        ....
        ....
        Installed c:\myflyscript\lib\python2.7\site-packages\flyscript-0.5-py2.7.egg
        Processing dependencies for flyscript==0.5
        Finished processing dependencies for flyscript==0.5

6. At this point, you should be able to run the examples included in
   the FlyScript package.  Run the about.py script as a simple test:

        :::text
        > c:\Python27\python c:\flyscript-0.5\examples\about.py
        Package 'flyscript' version 0.5 installed

        Path to source:
          c:\myflyscript\lib\python2.7\site-packages\flyscript-0.5-py2.7.egg\rvbd

        Modules provided:
          rvbd.common
          rvbd.extras
          rvbd.pilot
          rvbd.profiler
          rvbd.shark
          rvbd.stingray

You can now run any of the tools in the Scripts directory just by calling them at the command line. 

If you write your own scripts, be sure to execute them with c:\myflyscript\Scripts\python rather
than just python.  This will use the private copy of python and pull in the all the packages
that were just installed locally within that environment.

For more information about virtualenv, see [virtualenv website](http://www.virtualenv.org/en/latest).
On success, this will print the FlyScript package version, the
location of the source files and list the modules provided.


Upgrading and Uninstalling
--------------------------

If you are using a virtual environment, there is no reason to upgrade, you simply delete
the old environment and repeat the installation procedure.  (Be sure to move out any
files you created or modified before deleting the old environment though!)

At any time you can simply uninstall this by deleting the entire
subdirectory ~/myflyscript (or c:\myflyscript on windows).


System-Wide Installation 
========================

Use these instructions to install the FlyScript package system-wide, into the site-packages
directory.  This will make the FlyScript package available to all users. 

<a id="installsys-linuxmac"></a>

Linux/Mac
---------

You must already have Python installed on your system to continue.
If not, please install Python from [python.org](http://www.python.org/getit/)
or ask your system adminstrator to install Python.  You will need
either Python 2.6.x or 2.7.x to use the FlyScript SDK.

Follow steps 1-3 above as for [Linux/Mac VirtualEnv Installation](#installvenv-linuxmac)

1. Check that Python is running 2.6.x or 2.7.x.

2. Download a copy of the flyscript tar file.

3. Extract the FlyScript package in a suitable location.

4. As root or using sudo, install the FlyScript package:

        :::text
        $ cd flyscript-0.5
        $ sudo python setup.py install
        Password:
        ....
        ....
        Installed /usr/lib/python2.7/site-packages/flyscript-0.5-py2.7.egg
        Processing dependencies for flyscript==0.5
        Finished processing dependencies for flyscript==0.5

6. Test your installation by running a simple test (note, you may have to refresh
   your path with `rehash` if the command is not found):

        :::text
        $ python flyscript-0.5/examples/about.py
        Package 'flyscript' version 0.5 installed

        Path to source:
          /usr/lib/python2.7/site-packages/flyscript-0.5-py2.7.egg/rvbd

        Modules provided:
          rvbd.common
          rvbd.extras
          rvbd.pilot
          rvbd.profiler
          rvbd.shark
          rvbd.stingray

<a id="installsys-win"></a>

Windows
-------

Follow steps 1-3 above as for [Windows VirtualEnv Installation](#installvenv-win)

1. Download and install Python 2.6.x or 2.7.x.

2. Download a copy of the flyscript tar file.

3. Double click on the FlyScript package to extract the contents.

6. Install the FlyScript package using the system python.  Open a
   command prompt and type the following commands:

        :::text
        > cd c:\flyscript-0.5
        > C:\Python27\python setup.py install
        ....
        ....
        Installed c:\Python27\site-packages\flyscript-0.5-py2.7.egg
        Processing dependencies for flyscript==0.5
        Finished processing dependencies for flyscript==0.5

6. At this point, you should be able to run the examples included in
   the FlyScript package.  Run the about.py script as a simple test:

        :::text
        > c:\Python27\python c:\flyscript-0.5\examples\about.py
        Package 'flyscript' version 0.5 installed

        Path to source:
          c:\Python27\site-packages\flyscript-0.5-py2.7.egg\rvbd

        Modules provided:
          rvbd.common
          rvbd.extras
          rvbd.pilot
          rvbd.profiler
          rvbd.shark
          rvbd.stingray


Upgrading and Uninstalling
--------------------------

If you need to upgrade the FlyScript package to a newer version, simply repeat the above installation 
steps.  This will install the latest version alongside the older version.  Normally you do not
need to delete the older version.

If you need to completely uninstall the FlyScript package, you must first find complete installation
directory.  You can get this directory from the about.py command (shown above), or you can 
run python:

    :::text
    $ python
    >>> import rvbd
    >>> help(rvbd)

This will display the path to the package __init__.py file.  Delete the entire directory 
leading up to rvbd/__init__.py.

