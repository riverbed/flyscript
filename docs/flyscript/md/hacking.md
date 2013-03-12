
Notes for FlyScript Developers
==============================

This page contains notes about how to work with and modify
the core FlyScript libraries.

Coding Guidelines
-----------------

The first and most important rule when working on FlyScript is to
follow the guidelines established in
[PEP8](http://www.python.org/dev/peps/pep-0008/).
These guidelines cover the basics of formatting, commenting, naming, etc. 


### Class Hierarchy

The class hierarchy for the FlyScript Python package `rvbd` is
explained on [the main documentation page](index.html).
Pay particular attention to the Python convention of using a leading
underscore character to distinguish protected interfaces from public ones.
That is, classes and functions that are specific to a particular
version of a product and may change should be named with a leading
underscore.
If a module consists entirely of private classes and functions,
the whole should be named with a leading underscore.
Anything that is not marked as private with a leading underscore
is implicitly part of the public interface and
the programming interface including the syntax
(i.e., the name of a class and its methods, number and types of
argument, etc.)
and the semantics (i.e., how a class, method, or function is used,
function side effects, etc.) must remain backward compatible
as new code is developed.


### Exceptions

Exceptions are the preferred mechanism for dealing with, well,
exceptional conditions.
Code in the FlyScript libraries should raise appropriate exceptions
to callers and should not unnecessarily block exceptions coming
from underlying system libraries.

First, on the topic of raising appropriate exceptions,
the first choice should always be to use system built-in
exception types (e.g., `TypeError`, `IOError`, etc.).
Raising exceptions defined in the standard system libraries
(e.g., `socket.error`) is also appropriate.

For error conditions that are unique to a particular product,
each product should define its own exception type.
For example, code in the `rvbd.shark` package can raise
(subclasses of) `rvbd.shark.SharkException`.
Different error conditions should be distinguished be creating
separate sub-classes of the product-specific exception type.
For example, in the case of Shark, we might have separate
exception types `InvalidExtractorField` and `AuthenticationError`.
By creating separate exception types, a caller that wants to catch
one specific error type can do so easily without catching all
instances of `Exception` or `SharkException` and re-raising
ones it doesn't care about.

As for catching exceptions from system libraries,
FlyScript code should only do this if it is fully prepared to handle
an exception it catches.
A good example is detecting if a process is listening on some
TCP port with code like this:

    try:
        socket.connet((host, port))
    except socket.error, e:
        if e.errno == errno.ECONNREFUSED:
            # do something
        else:
            raise

Note that the except clause is relatively narrow and any exception
that is not specifically handled (i.e., an error other than
"connection refused") is raised to the caller.
In particular, FlyScript code should never have a general `except:`
clause, as that will certainly catch exceptions that should not
be caught (`KeyboardInterrupt` for instance)


Writing documentation
---------------------

There are two levels of documentation available for FlyScript code.
First, there are Python *docstrings* embedded in the source code.
These serve as the primary documentation for classes and methods,
as they are easily accessed by users with the interactive python
`help()` command, or with
[pydoc](http://docs.python.org/library/pydoc.html).
Docstrings should follow the conventions established in
[PEP257](http://www.python.org/dev/peps/pep-0257/).

The more detailed reference documentation is maintained in the
`docs/` directory in the FlyScript source tree,
and is rendered to HTML pages using
[Sphinx](http://sphinx.pocoo.org/) or ridl (XXX explain ridl!)


Other tips
==========

[setuptools](http://pypi.python.org/pypi/setuptools)
has a handy option that installs a symbolic link
to the FlyScript libraries into your system-wide or virtualenv-specific
`site-packages` directory.  From the top level FlyScript directory
simply run::

    $ python setup.py develop

