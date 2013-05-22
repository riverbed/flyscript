#!/usr/bin/env python

# Copyright (c) 2013 Riverbed Technology, Inc.
#
# This software is licensed under the terms and conditions of the 
# MIT License set forth at:
#   https://github.com/riverbed/flyscript/blob/master/LICENSE ("License").  
# This software is distributed "AS IS" as set forth in the License.



import unittest
import os
import subprocess
import logging
import sys
import select
import fcntl

here = os.path.abspath(os.path.dirname(__file__))

logger = logging.getLogger()
logging.basicConfig(level=logging.DEBUG,
                    format="%(asctime)s [%(levelname)-5.5s] %(msg)s")

try:
    from testconfig import config
except ImportError:
    config = {}

shark_scripts = {
    'shark_view_fields.py': [],
    'readview.py': [ '-l' ],
    'shark_info.py': []
}

profiler_scripts = {
    'top-ports.py': ['--logfile', '/tmp/test-examples.log']
}

class TestExamples(unittest.TestCase):
    def setUp(self):
        try:
            username = config['username']
        except KeyError:
            username = 'admin'

        try:
            password = config['password']
        except KeyError:
            password = 'admin'

        stdargs = [ '-u', username, '-p', password ]
        try:
            self.shark_args = stdargs + [ config['sharkhost'] ]
        except KeyError:
            self.shark_args = None            

        try:
            self.profiler_args = stdargs + [ config['profilerhost'] ]
        except KeyError:
            self.profiler_args = None

        os.environ['PYTHONPATH'] = os.path.join(here, '..')


    def _run(self, dirname, scripts, args):
        for script in scripts:
            path = os.path.join(here, dirname, script)
            logger.info("Running script: " + path)
            command = [ 'python', path, '--loglevel', 'debug' ]
            command += scripts[script]
            command += args

            proc = subprocess.Popen(command, stdout=subprocess.PIPE,
                                    stderr=subprocess.PIPE)

            fl = fcntl.fcntl(proc.stdout, fcntl.F_GETFL)
            fcntl.fcntl(proc.stdout, fcntl.F_SETFL, fl | os.O_NONBLOCK)

            fl = fcntl.fcntl(proc.stderr, fcntl.F_GETFL)
            fcntl.fcntl(proc.stderr, fcntl.F_SETFL, fl | os.O_NONBLOCK)

            while True:
                if proc.poll() is not None:
                    break
                fds = select.select([proc.stdout, proc.stderr], [], [])
                
                if proc.stdout in fds[0]:
                    data = proc.stdout.read()
                    if len(data) == 0:
                        break

                    for line in data.split('\n'):
                        logger.info('OUT: %s' % line)
                if proc.stderr in fds[0]:
                    data = proc.stderr.read()
                    if len(data) == 0:
                        break

                    for line in data.split('\n'):
                        logger.error('ERR: %s' % line)
            
            if proc.returncode == 0:
                logger.info('exited with status 0')
            else:
                logger.error('exited with status %s' % proc.returncode)
                
    def test_shark_examples(self):
        if self.shark_args is None:
            return

        self._run('shark', shark_scripts, self.shark_args)

    def test_profiler_examples(self):
        if self.profiler_args is None:
            return

        self._run('profiler', profiler_scripts, self.profiler_args)



if __name__ == '__main__':
    import sys

    # pull away arguments so unittest.main() doesn't get confused
    args = sys.argv[1:]
    sys.argv = [ sys.argv[0] ]

    # stash args in config dictionary
    for arg in args:
        L = arg.split('=', 1)
        if len(L) != 2:
            raise ValueError('cannot understand argument %s' % arg)
        config[L[0]] = L[1]

        sys.argv = [ sys.argv[0] ]

    unittest.main()
