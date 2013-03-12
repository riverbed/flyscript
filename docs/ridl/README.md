

This directory contains an initial version of ridl, a tool for
documenting python code.  Ridl is a replacement for Sphinx.  It is
similar to Sphinx in that uses Python introspection to automatically
extract signatures and docstrings for functions/methods.  But it
addresses some of the problems that made Sphinx a pain to use.

The next section explains a bit more about what ridl is and how it
differs from sphinx, if you want to skip it and just run it, jump
down to "running ridl" below.


About ridl
==========

Ridl addresses several things that make sphinx inconvenient to use,
at least for our purposes with flyscript.  First, Sphinx uses a text
markup scheme called restructured text, which is awkward and clunky.
Ridl uses [markdown](http://daringfireball.net/projects/markdown/syntax)
instead.  At a high level, markdown and restructured text are similar
but markdown has gained a lot more traction, mostly because its syntax
is simpler and less cumbersome.

Another difference between sphinx and ridl is in the handling of
automatic documentation of python code.  Sphinx is relatively rigid.
You can either ask it to document everything in a module or class or
you can write directives to enumerate individual functions, methods,
etc.  In the first case you get no control over the order that items
are presented and no opporunity to insert additional text into the
documentation.  Sphinx also includes the class name in the documentation
so there is no way to document the interface to a class without
exposing the name of the class, even if the class name isn't meant
to be public to your users.  As an example to make this last point
concrete, suppose file objects were implemented in python and you
wanted to automatically document them.  Since users only get file
objects as the return value from functions like `open()`, the full
module name should not be part of the object documentation, but
Sphinx always embeds the full name.

So, to get flexibilty we end up writing our own documentation
container with embedded directives to document individual methods.
But Sphinx has poor tools for tracking what has been documented and
warning if any classes/methods/functions/etc are undocumented.
Ridl uses the same structure but it tracks exactly what has and has
not been documented and it emits a full list of all undocumented
components after each run.

Finally, Sphinx treats python docstrings as literal markup.  To
create links in the generated documentation, we have to put
restructured text markup into docstrings which compromises readability
in an interactive python session (or with any other tool that reads
docstrings such as eclipse or other IDEs).  Ridl has several features
for automatically creating links within docstrings, these features
are described in detail below.  But this approach lets us create
links for things like common glossary terms, function names, etc.
without polluting docstrings with markup.


Running ridl
============

To run ridl, you need to have the
[python-markdown](https://github.com/waylan/Python-Markdown)
library installed.  If you're impatient, `pip install python-markdown`
should be enough.

Ridl takes a single mandatory command-line argument: the path to a
directory that holds the source files to be processed.  The format
of these source files is described in the next section.  This
directory must also contain a file called `conf` where a number of
options and parameters are specified.  The format of this configuration
file is described later in this document.

XXX create a simple example to refer to here


Docstring processing
====================

As described above, a major goal of ridl is for python
docstrings to be written in plain text, free of any markup
but also to still have useful hyperlinks in the rendered
html output.  To do this, ridl provides two schemes for
automatically inserting hyperlinks into python docstrings.
These schemes are completely controlled by parameters specified
at configuration time so you can use them as aggressively or as
conservatively as you like.

### Self-links

Ridl treats any words inside docstrings that end with a pair
of parentheses (`()`) as a potential reference to another function
or method.  When such a string is encountered, the ridl processor
extracts the string before the parentheses (e.g., from `foo()`
the string `foo` is extracted) and looks up that string as a symbol
first in the python class being currently documented, and then in
the python module currently being documented.  If this string does
refer to a python function or method, the original word automatically
becomes a link to the documentation for that function or method.

### Auto-links

The `autolink` directive in the ridl configuration file can be used
to force specific words or terms to automatically be turned into
hyperlinks.  A typical use is for terms in a glossary.  Take care
with auto-links, as using them for common words can easily lead to
links being created more frequently than you might intend...


Ridl markup
===========

The actual source files to be processed by ridl are written in
markdown with a few additional directives available.  For each
source file, the directives described in this section are processed
and then the resulting contents are fed directly into a markdown
formatter.

Ridl directives are enclosed in curly braces (e.g.,  `{foo}`).
The following directives are recognized:

## {version}

Insert the version string declared in the ridl configuration file
(see the configuration file `version` directive below).

## {date}

Insert the date and time at which the documentation was formatted.

## {anchor}

Create an "anchor" that can be the target of hyperlinks.
This directive is followed by the name of the anchor, and then
arbitrary markdown for the contents of the anchor.
For example, the following directive:

   `{anchor intro ## Introduction}`

logically translates into the following html:

   `<h2 id="intro">Introduction</h2>`

(this is done by translating the original directive into the following
fragment of markdown):

   `## Introduction{: #intro}`

Note that in practice, additional markup is added for styling, etc.

## {module}

Set the current python module being documented.
This directive must be followed by the name of a python module,
the given module will be immediately imported so it must be
present somewhere in the python interpreter's path.  Since ridl
itself is a python script, it is not enough to spawn ridl from
a directory that holds the python code you are documenting, if
your code is not installed into the global system python path,
you will probably need to set the PYTHONPATH environment variable.

After this directive, subsequent `{class}` and `{function}`
directives will refer to classes and functions within the named
module.  In addition, while processing this directive, the module's
docstring will be emitted.  The `silent` keyword can be added to
the directive to suppress printing the docstring.

Example:

   `{module mymodule.submodule}`

## {function}

Document the given function.
This will print the signature for the function as well as its
docstring.

## {class}

Set the current python class being documented.
This directive must be preceded by a `{module}` directive to
set the current python module.

This directive establishes the python class referred to by subsequent
`{method}` directives.  It also emits some documentation for the
class:
   * The full class name (as a linkable anchor as described above)
   * The docstring for the class itself
   * The signature and docstring for the class constructor (`__init__()`)

As with the `{module}` directive, this directive can be followed by
the `silent` keyword to suppress printing the information above.
Suppressing the information above is useful for documenting classes
that have a public interface but that are never instantiated directly
by users of your library (in the standard python library,
file objects and regular expression match objects are examples of
classes that are not instantiated directly by users but that have
a set of documented methods).

## {method}

Document the given method.
This directive must be preceded by a `{class}` directive to set
the current python class.

This directive documents the given method by printing
the signature for the method and its docstring.  The method
signature is also a linkable anchor that can be referenced using
the `{methodref}` directive.

If instead of a method name, this directive appears as

   `{method *}`

then this directive will look up the names of all *public* methods
in the current class (i.e., those that do not begin with an underscore)
and document each of them.

## {methodref}

Create a link to the given method.
XXX example


Configuration file format
=========================

The behavior of ridl is controlled by a simple configuration file.
In the configuration file, blank lines and lines that begin with a
pound sign (`#`) are ignored.  Valid directives for the
remaining lines are:

## `outdir`, `tempdir` 

These directives each are followed by a directory path and
are mandatory.  `outdir` specifies the output directory where
the rendered html files plus other support files will be created.
`tempdir` specifies a directory where intermediate files can be
stored during processing (XXX this will be become optional at some point).
For both of these directives, if the given path begins with a `/`
it is an absolute path, otherwise it is relative to the input directory.

## `header`, `footer`

These directives are optional.  If present, each should be followed
by the name of a file (in the `md/` subdirectory of the input directory)
to be prepended/appended to each file.  This is useful for creating
a standard page layout.  Note that these files are processed by ridl
and markdown so you can use the directives described here and other
markdown directives in your headers and footers.

XXX describe .md vs .html extension

## `markdown_extension`

This optional directive loads the named extension for
[python-markdown](https://github.com/waylan/Python-Markdown).
Configuration options for the extension may be specified as a
series of additional arguments with the format `name=value`.

## `file`

This directive lists the input files that ridl should process.
It may appear multiple times if the list of input files doesn't
fit neatly on a single line.  Note that these files should be in
the `md/` subdirectory of the input directory.

## `static-file`

This directive enumerates files that should be simply copied from
the input directory to the output directory.  It is useful for
custom images, style sheets, etc.  The directive may appear multiple
times if the list of static files does not feat neatly on one line.

## `title`

This directive sets the string that will appear in the <title>
tag in each rendered html page.

## `version`

This directive sets the string that will be substituted for any
`{version}` directives in source files.  If the contents of this
directive looks like a file path, that contents of that file will be
read and used.

## `autolink`

This directive sets up auto-linking as described above.  It may
appear multiple times to create multiple auto-link rules.
Each directive is followed by a regular expression (using the
[Python regular expression syntax](http://docs.python.org/2/library/re.html#regular-expression-syntax)
and the relative url to link to.

## `module-prefix`

This optional directive specifies the top-level python module
to be documented.  At the end of a run, ridl will only warn about
undocumented objects with names that begin with this prefix.

## `undocumented`

This optional directive suppresses the ridl warning if the given
python object (module, class, function, or method) is not documented.
It may appear multiple times.

