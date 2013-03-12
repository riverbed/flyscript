Installing FlyScript
====================

This page provides detailed instructions for installing the FlyScript SDK.

* [Quick Start](#quickstart) - If you're familiar with Python, jump right in

* [Detailed Step by Step](install_details.html) - for a little extra guidance


<a id="dependencies"></a>

Dependencies
============

* Python version 2.6.X or 2.7.X
    * Download latest from [here](http://python.org/download/)
* (optional) virtualenv
    * Download latest from [here](http://www.virtualenv.org/en/latest/)


<a id="quickstart"></a>

Quick Start
===========

## Recommended approach - using virtualenv

The recommended approach will install FlyScript inside of a virtualenv
to help isolate it from other dependencies on your system and also
allow it to be used without root permissions.

Install [virtualenv](http://www.virtualenv.org/en/latest/)

Create new environment: 

    :::text
    $ virtualenv flyscript


Install flyscript package inside new virtual environemnt:

    :::text
    (flyscript)$ pip install flyscript

Start coding!  

## Alternate approach - download package

The latest version of FlyScript can also be downloaded from either
GitHub or Riverbed's Splash page.  This way the SDK can be installed
offline for enviroments that may not have ready internet access.

#### Install virtualenv
(Optional) Before installing the SDK using either approach below,
download and install the virtualenv package using the instructions
from here: [http://www.virtualenv.org/en/latest/](http://www.virtualenv.org/en/latest/)

#### GitHub

Clone the repository to a local directory and run setup from there
 using the following command:

    :::text
    $ cd ~
    $ git clone git://github.com/riverbed/flyscript.git
    $ cd flyscript
    $ python setup.py install
    
#### Riverbed Splash - download the package from the web

Or download the latest tarball from the Splash page:
[https://splash.riverbed.com/community/product-lines/flyscript](https://splash.riverbed.com/community/product-lines/flyscript).
Once the tarball has been downloaded, change to that directory,
and install from there:

    :::text
    $ tar xvzf flyscript-0.5.tar.gz
    $ cd flyscript
    $ python setup.py install


Start coding!  

Directory Layout
================

The SDK tarball has the following directories included:

* `flyscript-0.5/docs` - this documentation

* `flyscript-0.5/examples` - list of simple examples that demonstrate basic concepts
    * shark - examples for interacting with Cascade Shark appliance
    * profiler - examples for communication with Cascade Profiler

* `flyscript-0.5/rvbd` - root of all python code
    * `common` - modules common across all products
    * `extras` - misc modules or utilities
    * `pilot/profiler/shark` - modules specific to a given product

After installation, the examples scripts will be included in your local bin 
directory, and the docs included along with the source files.


Upgrade and Uninstalling
========================

Virtual Environment
-------------------

If you are using a virtual environment, there is no reason to upgrade, you simply delete
the old environment and repeat the installation procedure.  (Be sure to move out any
files you created or modified before deleting the old environment though!)

At any time you can simply uninstall this by deleting the entire
subdirectory ~/myflyscript (or c:\myflyscript on windows).


System Installation
-------------------

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

