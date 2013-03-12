
import shlex
import re
import os, os.path
import sys
import types
import inspect
import datetime

# XXX types doesn't have a PropertyType?
class foo(object):
    @property
    def bleah(self): pass

PropertyType = type(foo.bleah)

class Tracker(object):
    """
    This class tracks which python modules, functions, classes, and
    methods have and have not been documented.
    """
    def __init__(self, prefix, ignores, processor):
        self.prefix = prefix
        self.ignores = ignores
        self.processor = processor

        self._all_modules = set()
        self._all_classes = set()
        self._all_data = set()
        self._all_functions = set()
        self._all_methods = set()

        self._documented_modules = set()
        self._documented_classes = set()
        self._documented_data = set()
        self._documented_functions = set()
        self._documented_methods = set()

        # initialize the list of all modules to be documented...
        module = self.processor._find_module(self.prefix)
        if module.__file__.endswith('__init__.pyc'):
            self._read_submodules(self.prefix, os.path.dirname(module.__file__))

    def _ignore(self, name):
        return any([ name.startswith(i) for i in self.ignores ])

    def _add_module(self, modname):
        if self._ignore(modname):
            return False
        self._all_modules.add(modname)
        return True
        
    def _read_submodules(self, modname, dirname):
        # we try to do most of our analysis through introspection
        # at run-time, but the only way to discover sub-modules
        # is by reading the filesystem.
        for name in os.listdir(dirname):
            if name.startswith('_'):
                continue

            if name.endswith('.py'):
                self._add_module('%s.%s' % (modname, name[:-3]))
                continue
            
            subdir = os.path.join(dirname, name)
            if os.path.isdir(subdir) \
              and (os.path.exists(os.path.join(subdir, '__init__.py'))
                   or os.path.exists(os.path.join(subdir, '__init__.pyc'))):
                submodule = '%s.%s' % (modname, name)
                if self._add_module(submodule):
                    self._read_submodules(submodule, subdir)

    def _touch_module(self, name):
        components = name.split('.')

        for l in range(len(components)):
            self._documented_modules.add('.'.join(components[:l+1]))

    def enter_module(self, module, name):
        self._touch_module(name)

        if hasattr(module, '__all__'):
            objs = module.__all__
        else:
            objs = dir(module)

        for objname in objs:
            if objname.startswith('_'): continue
            o = getattr(module, objname)

            realmodname = name
            if hasattr(o, '__module__') and o.__module__ != name:
                if self.prefix is not None \
                  and not o.__module__.startswith(self.prefix):
                    msg = 'ignoring %s.%s' % (name, objname)
                    msg += ' since it is really just %s.%s' % (
                        o.__module__, objname)
                    self.processor._logger.debug(msg)
                    continue
                realmodname = o.__module__

            if any([s.startswith('_') for s in realmodname.split('.')]):
                continue

            fullname = '%s.%s' % (realmodname, objname)
            if self._ignore(fullname):
                continue
            
            if isinstance(o, (types.ClassType, types.TypeType)):
                self._all_classes.add(fullname)
            elif isinstance(o, types.FunctionType):
                self._all_functions.add(fullname)
            elif not isinstance(o, types.ModuleType):
                self._all_data.add(fullname)

    def enter_class(self, cls, name):
        self._touch_module(name)
        
        # if this class is ignored, don't try to track all its methods...
        if name not in self._all_classes:
            return
        
        self._documented_classes.add(name)

        for i in dir(cls):
            if i.startswith('_'): continue

            o = getattr(cls, i)
            if isinstance(o, (types.MethodType, PropertyType)):
                self._all_methods.add('%s.%s' % (name, i))
            else:
                self.processor._warn('what is %s.%s ?' % (name, i))

    def enter_method(self, fullname):
        self._documented_methods.add(fullname)

    def enter_function(self, fullname):
        self._documented_functions.add(fullname)
        self._touch_module(fullname)

    def undocumented_modules(self):
        modules = list(self._all_modules.difference(self._documented_modules))
        modules.sort()
        return modules

    def undocumented_classes(self):
        classes = list(self._all_classes.difference(self._documented_classes))
        classes.sort()
        return classes

    def undocumented_data(self):
        data = list(self._all_data.difference(self._documented_data))
        data.sort()
        return data

    def undocumented_functions(self):
        funcs = list(self._all_functions.difference(self._documented_functions))
        funcs.sort()
        return funcs

    def undocumented_methods(self):
        methods = list(self._all_methods.difference(self._documented_methods))
        methods.sort()
        return methods

class Processor(object):
    """
    This class is the main workhorse for ridl.  It processes input
    files and handles the ridl directives described in README.md.
    """
    def __init__(self, logger, module_prefix=None, ignores=None,
                 versioninfo='(unknown)'):
        self._logger = logger
        self._versioninfo = versioninfo
        self._links = []

        self._tracker = Tracker(module_prefix, ignores or [], self)

        self._warning_count = 0
        self._error_count = 0

        self._reset_file()

    def add_autolink(self, pattern, newtext):
        orig = re.compile(pattern)
        new = '[%%s](%s)' % newtext
        self._links.append((orig, new))
        
    def _warn(self, msg):
        self._warning_count += 1
        if self._cur_file_name is not None:
            msg = '(%s:%d): %s' % (self._cur_file_name, self._lineno, msg)
            
        self._logger.warning(msg)

    def _error_continue(self, msg):
        self._error_count += 1
        if self._cur_file_name is not None:
            msg = '(%s:%d): %s' % (self._cur_file_name, self._lineno, msg)

        self._logger.error(msg)

    def _fatal(self, msg):
        self._logger.critical(msg)
        sys.exit(-1)

    def warnings(self): return self._warning_count
    def errors(self): return self._error_count
        
    def _reset_file(self, fname=None):
        self._lineno = 0
        self._cur_file_name = fname
        
        self._cur_module = None
        self._cur_module_name = None

        self._cur_class = None
        self._cur_class_name = None
    
    def _do_autolinks(self, s):
        pos = 0
        while True:
            best = None
            for orig, new in self._links:
                m = orig.search(s, pos)
                if m is None:
                    continue
                if best is None or m.start() < best[0]:
                    best = m.start(), m.group(0), new

            if best is None:
                break

            where = best[0]
            found = best[1]
            oldlen = len(found)
            replace = best[2] % found

            s = s[:where] + replace + s[where+oldlen:]
            pos = where + len(replace)

        return s

    def _lookup_name(self, nm):
        def search(nm, obj, prefix):
            components = nm.split('.')
            for component in components:
                try:
                    obj = getattr(obj, component)
                except AttributeError:
                    return None

            if isinstance(obj, types.MethodType):
                anchor = 'method_%s_' % prefix
                anchor += '_'.join(components)
                return anchor

            return None

        if self._cur_class_name is not None:
            cls_prefix = '%s_%s' % (self._cur_module_name.replace('.', '_'),
                                    self._cur_class_name)
            
            anchor = search(nm, self._cur_class, cls_prefix)
            if anchor is not None:
                return anchor

        return search(nm, self._cur_module, self._cur_module_name)
        
        
    def _do_selflinks(self, s):
        for w in s.split():
            # if it already looks like a link, skip it
            if w.startswith('['):
                continue

            # look for something with parens
            if w.find('(') == -1:
                continue
            
            # try to get a raw name
            nm = w.replace('`', '').replace('(', '').replace(')', '')
            anchor = self._lookup_name(nm)
            if anchor is not None:
                self._logger.debug('(%s:%d): linking to %s' % 
                                   (self._cur_file_name, self._lineno, nm))
                s = s.replace(' %s ' % w, ' [%s](#%s) ' % (w, anchor))

        return s

    def process_one_file(self, infp, outfp, fname):
        self._reset_file(fname)

        pattern = re.compile(r'{[^}]+}')
        for line in infp:
            self._lineno += 1

            while len(line) > 0:
                match = pattern.search(line)
                if match is None:
                    break
                outfp.write(line[:match.start()])
                line = line[match.end():]
                chunk = match.group(0)
                try:
                    out = self._handle_special(chunk)
                    outfp.write(out)
                except NotImplementedError:
                    outfp.write(chunk)

            if len(line) > 0:
                outfp.write(line)
                
                
    def _do_docstring(self, s, wrap_in_div=False):
        ret = ''
        if wrap_in_div:
            ret += '<div class="docstring" markdown="1">\n'
        
        if s is None:
            ret += '<em>(no docstring)</em>'
        else:
            lines = s.expandtabs().splitlines()
            try:
                indent = min([ len(l) - len(l.lstrip())
                               for l in lines[1:] if len(l.strip()) > 0 ] )
                s = '\n'.join([lines[0]] + [ l[indent:].rstrip() for l in lines[1:] ])
            except ValueError:
                # if there is just one line or a one line plus a bunch of
                # blank lines, then the call to min() raises ValueError,
                # in that case we just need the first line.
                s = s.strip()

            s = self._do_autolinks(s)
            s = self._do_selflinks(s)
            ret += s

        if wrap_in_div:
            ret += '\n</div>\n'

        return ret

    def _find_module(self, modname):
        try:
            return sys.modules[modname]
        except KeyError:
            try:
                __import__(modname)
            except ImportError:
                self._fatal('cannot find module %s' % modname)
            return sys.modules[modname]

    def warn_undocumented(self):
        # XXX clear lineno
        self._reset_file()

        for name in self._tracker.undocumented_modules():
            self._warn('module %s not documented!' % name)

        for name in self._tracker.undocumented_classes():
            self._warn('class %s not documented!' % name)

        for name in self._tracker.undocumented_data():
            self._warn('data item %s not documented!' % name)

        for name in self._tracker.undocumented_functions():
            self._warn('function %s not documented!' % name)

        for name in self._tracker.undocumented_methods():
            self._warn('method %s not documented!' % name)


    def _set_module(self, modname):
        self._cur_module = self._find_module(modname)
        self._cur_module_name = modname

        self._tracker.enter_module(self._cur_module, modname)

        return self._cur_module

    @property
    def _cur_full_class(self):
        if hasattr(self._cur_class, '__module__'):
            modname = self._cur_class.__module__
        else:
            modname = self._cur_module_name
        return '%s.%s' % (modname, self._cur_class_name)
        
    def _set_class(self, classname):
        self._cur_class = getattr(self._cur_module, classname)
        self._cur_class_name = classname

        self._tracker.enter_class(self._cur_class, self._cur_full_class)

        return self._cur_class

    def _get_signature(self, f, skip_self=False):
        ''' Extract the signature for a callable f 
        (ie, a function or a method) and return markup that
        describes it.
        If skip_self is True, assume the first argument is self
        so omit it from the signature.
        '''
        argspec = inspect.getargspec(f)

        args = argspec.args
        if skip_self:
            args = args[1:]

        # which is the first arg that has a default?
        firstdef = len(args)
        if argspec.defaults is not None:
            firstdef = len(args) - len(argspec.defaults)

        def mkarg(i):
            nm = args[i].replace('_', '\_')
            if i < firstdef:
                return '<em>%s</em>' % nm
            else:
                d = argspec.defaults[i-firstdef]
                if isinstance(d, basestring):
                    d = '"%s"' % d.replace(' ', '&nbsp;')
                return '<em>%s</em>=%s' % (nm, d)

        arglist = [ mkarg(i) for i in range(len(args)) ]
        if argspec.varargs is not None:
            arglist.append('*args')
        if argspec.keywords is not None:
            arglist.append('**kwargs')

        return ', '.join(arglist)

    def _make_linkable(self, anchorname, content):
        s = '<a name="%s" href="#%s" class="linkable">' % (anchorname, anchorname)
        s += content
        s += '<span class="link-icon"></span>'
        s += '</a>'
        return s

    def _make_class_doc(self, name, c):
        s = ''

        anchor = 'class_%s_%s' % (self._cur_module_name.replace('.', '_'), name)
        s += self._make_linkable(anchor, 'class `%s.%s`' % (self._cur_module_name, name))
        s += '\n\n'
        s += self._do_docstring(c.__doc__)
        s += '\n\n'

        # document the constructor
        ctor = getattr(c, '__init__')
        s += '<strong>%s</strong>(%s)' % (name, self._get_signature(ctor, skip_self=True))
        s += '\n\n'
        s += self._do_docstring(ctor.__doc__, wrap_in_div=True)
        s += '\n\n'
            
        return s
        
        
    def _make_method_doc(self, name, m):
        fullname = '%s.%s' % (self._cur_full_class, name)
        self._tracker.enter_method(fullname)

        anchorname = 'method_%s_%s_%s' \
            % (self._cur_module_name.replace('.', '_'),
               self._cur_class_name, name)

        sig = '<strong>%s</strong>' % name.replace('_', '\_')
        if isinstance(m, types.MethodType):
            sig += '(%s)' % self._get_signature(m, skip_self=True)

        s = self._make_linkable(anchorname, sig)
        s += '\n\n'
        s += self._do_docstring(m.__doc__, wrap_in_div=True)
        s += '\n'

        return s

    def _make_function_doc(self, modname, name, f):
        fullname = '%s.%s' % (modname, name)
        self._tracker.enter_function(fullname)

        anchorname = 'function_%s_%s' % (modname.replace('.', '_'), name)

        sig = '<strong>%s</strong>(%s)' % (name.replace('_', '\_'), self._get_signature(f))

        s = self._make_linkable(anchorname, sig)
        s += '\n\n'
        s += self._do_docstring(f.__doc__, wrap_in_div=True)
        s += '\n'

        return s

    def _handle_special(self, line):
        assert line[0] == '{' and line[-1] == '}'
        
        L = shlex.split(line[1:-1].strip())

        if L[0] == 'anchor':
            assert len(L) >= 2
            anchorname = L[1]

            s = ''
            # XXX special treatment for headers...
            if L[2].startswith('#'):
                s += '%s ' % L[2]
                rest = L[3:]
            else:
                rest = L[2:]

            s += ' '.join(rest)
            s += '{: #%s .linkable}' % anchorname
            return s
            
        if L[0] == 'module':
            mod = self._set_module(L[1])
            if len(L) > 2 and L[2] == 'silent':
                return ''
            return self._do_docstring(mod.__doc__)

        if L[0] == 'class':
            name = L[1]
            classobj = self._set_class(name)
            if len(L) > 2 and L[2] == 'silent':
                return ''

            return self._make_class_doc(name, classobj)

        if L[0] == 'method':
            name = L[1]

            if name == '*':
                names = dir(self._cur_class)
                names.sort()
                
                ret = ''
                for name in names:
                    if name.startswith('_'):
                        continue
                    
                    method = getattr(self._cur_class, name)
                    if not isinstance(method, types.MethodType):
                        continue

                    ret += '\n'
                    ret += self._make_method_doc(name, method)
                return ret
            else:
                try:
                    m = getattr(self._cur_class, name)
                    return self._make_method_doc(name, m)
                except AttributeError, e:
                    msg = str(e)
                    self._error_continue(msg)
                    return '<em>%s</em>' % msg

        if L[0] == 'methodref':
            name = L[1]
            s = '[`%s`](#method_%s_%s)' % (name, self._cur_module_name.replace('.', '_'), name.replace('.', '_'))

            if len(L) > 2:
                s += ' '.join(L[2:])
            return s

        if L[0] == 'function':
            name = L[1]
            try:
                modname = self._cur_module_name
                f = getattr(self._cur_module, name)
            except AttributeError:
                L = name.split('.')
                modname = '.'.join(L[:-1])
                name = L[-1]

                mod = self._find_module(modname)
                try:
                    f = getattr(mod, name)
                except AttributeError:
                    self._error_continue('cannot find function %s, skipping' % name)
                    return ''

            return self._make_function_doc(modname, name, f)
                

        if L[0] == 'version':
            return self._versioninfo

        if L[0] == 'date':
            try:
                fmt = L[1]
            except IndexError:
                fmt = "%b %d, %Y at %I:%m %p"
            return datetime.datetime.now().strftime(fmt)

        else:
            raise NotImplementedError()

if __name__ == '__main__':
    # XXX
    sys.path.append('..')
    
    p = Processor()
    p.read_conf('conf')

    infp = open('shark.md', 'r')
    outfp = open('shark2.md', 'w')
    p.process_one_file(infp, outfp)
    infp.close()
    outfp.close()

