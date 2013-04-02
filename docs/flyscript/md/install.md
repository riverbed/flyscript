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
* Python setuptools
    * Download latest from [here](https://pypi.python.org/pypi/setuptools)


<a id="quickstart"></a>

Quick Start
===========

## Online Installation

Install pip, then install flyscript from python package index:

    :::text
    $ easy_install pip
    $ pip install flyscript

Start coding!  

## Alternate approach - offline installation

The latest version of FlyScript can also be downloaded from either
GitHub or Riverbed's Splash page.  This way the SDK can be installed
offline for enviroments that may not have ready internet access.

Once the depenencies are downloaded (python and setuptools) grab the SDK from
one of the following locations:

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

After installation, flyscript package will be available to use in Python via `import rvbd`. 
Examples and documentation are also installed, but may be in different locations depending on
your specific environment.  Typical locations for each operating system are as follows:


 OS         |  Documentation                                                                   |  Scripts               
 ---------- |:--------------------------------------------------------------------------------:|:-----------------------:
 *Linux*    |  `/usr/local/share/doc/flyscript`                                                |  `/usr/local/bin`      
 *Mac*      |  `/System/Library/Frameworks/Python.framework/Versions/2.7/share/doc/flyscript`  |  `/usr/local/bin`      
 *Windows*  |  `C:\Python27\share\doc`                                                         |  `C:\Python27\Scripts` 




Upgrade and Uninstalling
========================

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

