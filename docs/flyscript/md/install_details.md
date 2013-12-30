Installing FlyScript - Step by Step
===================================

This page provides step-by-step instructions for installing FlyScript for either
online or offline scenarios.

* System Install on [Linux/Mac](#installsys-linuxmac) / 
  [Windows](#installsys-win) - Install the FlyScript package 
  into the system-wide site-packages directory

Dependencies
============

* Python version 2.6.X or 2.7.X
    * Download latest from [here](http://python.org/download/)
* Python setuptools
    * Download latest from [here](https://pypi.python.org/pypi/setuptools)
* Python requests library
    * Download latest from [here](https://pypi.python.org/pypi/requests)


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

Check that Python is installed and running the approriate version:

    :::text
    $ python -V
    Python 2.7.3

### Online Installation

1. Install pip utility:

        :::text
        $ easy_install pip

2. Install flyscript package:

        :::text
        $ pip install flyscript


### Offline Installation
With no network access, and the flyscript and requests packages 
copied to your system:

1. Extract the requests package in a suitable location.

2. As root or using sudo, install the requests package:

        :::text
        > cd requests-2.1.0
        > C:\Python27\python setup.py install
        ....
        ....

3. Extract the FlyScript package in a suitable location.

4. As root or using sudo, install the FlyScript package:

        :::text
        $ cd flyscript-0.5.2
        $ sudo python setup.py install
        Password:
        ....
        ....
        Installed /usr/lib/python2.7/site-packages/flyscript-0.5.2-py2.7.egg
        Processing dependencies for flyscript==0.5.2
        Finished processing dependencies for flyscript==0.5.2


### Verify Installation

5. Test your installation by running a simple test (note, you may have to refresh
   your path with `rehash` if the command is not found):

        :::text
        $ flyscript-about.py
        Package 'flyscript' version 0.5.2 installed

        Path to source:
          /usr/lib/python2.7/site-packages/flyscript-0.5.2-py2.7.egg/rvbd

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

### Online Installation
If your machine has access to the internet, then follow these steps:

1. If you don't yet have Python installed on your system, download
   Python from [python.org](http://www.python.org/getit/).  Be sure to pick the
   installer from the Python 2 section (2.7.6 at the time this
   document is written) since FlyScript does not currently support
   Python 3.  Download the installer for your platform (32bit
   vs. 64bit).

2. Install [Python Setuptools](https://pypi.python.org/pypi/setuptools).  Simplest
   approach, download the [ez_setup.py](http://peak.telecommunity.com/dist/ez_setup.py)
   script, then double-click the file in your downloads directory.  This should
   automatically determine the best installation for your configuration.

3. Add Python to your System Path:

    * Navigate to the Enviroment Variables window via
      Right-click on "My Computer"->Properties->Advanced->Environment Variables.

    * Add a new item to the "User variables for USERNAME" section in the top part of 
      the window with the following properties (assumes Python from Step 1 was
      installed into the default location).  If you already have an item named "Path"
      there, you can just add a semi-colon (";") and append the following text in the
      dialog box: <br>
      Name: Path <br>
      Value: C:\Python27;C:\Python27\Scripts<br>

4. Open command-line window (Start -> Search -> cmd.exe)

5. Change to your Python Scripts directory and install pip.

        :::text
        > cd C:\Python27\Scripts
        > easy_install.exe pip
        ....

6. Use pip to install flyscript.

        :::text
        > cd C:\Python27\Scripts
        > pip.exe install flyscript
        ....

### Offline Installation
For offline installation, ensure you have downloaded python, setuptools, requests, 
and flyscript ahead of time and follow steps 1 and 2 above.  With python and setuptools
installed install flyscript using the following steps:

1. Double click on the requests package to extract the contents.

2. Install the requests package using the system python.  Open a
   command prompt and type the following commands (change the cd command
   to match the directory requests is extracted into):

        :::text
        > cd c:\requests-2.1.0
        > C:\Python27\python setup.py install
        ....
        ....

3. Double click on the FlyScript package to extract the contents.

4. Install the FlyScript package using the system python.  Open a
   command prompt and type the following commands (change the cd command
   to match the directory FlyScript is extracted into):

        :::text
        > cd c:\flyscript-0.5.2
        > C:\Python27\python setup.py install
        ....
        ....
        Installed c:\Python27\site-packages\flyscript-0.5.2-py2.7.egg
        Processing dependencies for flyscript==0.5.2
        Finished processing dependencies for flyscript==0.5.2


### Verify Install
At this point, you should be able to run the examples included in
the FlyScript package.  Run the flyscript-about.py script as a simple test:

    :::text
    > cd c:\Python27\Scripts
    > c:\Python27\python flyscript-about.py
    Package 'flyscript' version 0.5.2 installed

    Path to source:
      c:\Python27\site-packages\flyscript-0.5.2-py2.7.egg\rvbd

    Modules provided:
      rvbd.common
      rvbd.extras
      rvbd.pilot
      rvbd.profiler
      rvbd.shark
      rvbd.stingray


Upgrading and Uninstalling
--------------------------

If you need to upgrade the FlyScript package to a newer version, and you are
offline, simply repeat the above installation steps.  This will install the
latest version alongside the older version.  Normally you do not need to delete
the older version.

With internet access, flyscript updates are as simple as:

    :::text
    > pip install -U flyscript

(note the '-U' for upgrade).

If you need to completely uninstall the FlyScript package, you must first find
complete installation directory.  You can get this directory from the flyscript-about.py
command (shown above), or you can run python:

    :::text
    $ python
    >>> import rvbd
    >>> help(rvbd)

This will display the path to the package __init__.py file.  Delete the entire directory 
leading up to rvbd/__init__.py.

