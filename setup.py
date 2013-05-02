
import os
import glob

try:
    from setuptools import setup, find_packages, Command
except ImportError:
    from distutils.core import setup
    from distutils.cmd import Command
    
    def find_packages(path="rvbd"):
        for path, files, dirs in os.walk(path):
            if '__init__.py' in files:
                yield path
    
from contrib.version import get_git_version


class BuildDocRidl(Command):
    description = "Build the documentation in docs/ridl"
    user_options =  [] 
    
    def initialize_options(self): pass
    def finalize_options(self): pass
    def run(self):
        os.system("cd docs/ridl ; python ridl ../flyscript")
        

class BuildDocRESTAPI(Command):
    description = "Build documentation in docs/ridl and docs/rest_apis"
    user_options =  [] 
    
    def initialize_options(self): pass
    def finalize_options(self): pass
    def run(self):

        os.system("mkdir -p docs/html; cd docs/rest_apis ; "
                  "for d in `ls */*/*.json`; do python generate -o ../html -f $d --nopdfoutput --noprintable --nocoverpage; done")
        # create a markdown page with updated references
        apis = [os.path.basename(f) for f in glob.glob('docs/html/*REST_API*[0-9].html')]
        apis.sort()
        api_pairs = [(x.replace('_', ' ').strip('.html'), x) for x in apis]

        # build each reference line
        ref = '- [%s](%s)'
        bullets = [ref % ap for ap in api_pairs]

        toc = "REST API Documentation\n======================\n\n"
        text = toc + '\n'.join(bullets) + '\n'

        with open('docs/flyscript/md/rest_apis.md', 'w') as f:
            f.write(text)

        self.run_command("build_doc_ridl")
        

class BuildPackage(Command):
    description = "Build a new package"
    user_options =  [] 
    
    def initialize_options(self): pass
    def finalize_options(self): pass
            
    def run(self):
        self.run_command("build_doc_restapis")
        self.run_command("sdist")


setup(name="flyscript",
      version=get_git_version(),
      author="Riverbed Technology",
      author_email="cwhite@riverbed.com",
      url="https://splash.riverbed.com/docs/DOC-1464",
      description="Riverbed FlyScript library for interacting with Riverbed devices",
      long_description="""FlyScript
=========

FlyScript is a collection of libraries and scripts in Python and JavaScript for
interacting with Riverbed Technology devices.

For a complete guide to installation, see:

http://pythonhosted.org/flyscript/install.html
      """,
      platforms='',
      license="""Copyright (c) 2013 Riverbed Technology, Inc.

This software is licensed under the terms and conditions of the
MIT License set forth at:

https://github.com/riverbed/flyscript/blob/master/LICENSE ("License").

This software is distributed "AS IS" as set forth in the License.
      """,

      classifiers=['Development Status :: 4 - Beta',
                   'Intended Audience :: Developers',
                   'Intended Audience :: Information Technology',
                   'Intended Audience :: System Administrators',
                   'License :: OSI Approved :: MIT License',
                   'Programming Language :: Python :: 2.6',
                   'Programming Language :: Python :: 2.7',
                   'Topic :: System :: Networking'],
      
      data_files=[('share/doc/flyscript/html', glob.glob('docs/html/*'))],
      packages=find_packages(),
      scripts=[
          'examples/flyscript-about.py',
          'examples/profiler/percentile.py',
          'examples/profiler/top_ports.py',
          'examples/profiler/timeseries.py',
          'examples/profiler/profiler_columns.py',
          'examples/profiler/traffic_flowlist.py',
          'examples/profiler/traffic_summary.py',
          'examples/profiler/traffic_timeseries.py',
          'examples/shark/backup_restore.py',
          'examples/shark/control_job.py',
          'examples/shark/create_job.py',
          'examples/shark/export.py',
          'examples/shark/list_view_fields.py',
          'examples/shark/readview.py',
          'examples/shark/shark_upload_pcap.py',
          'examples/shark/shark_info.py',
        ],

      cmdclass = {
          "build_doc_ridl": BuildDocRidl,
          "build_doc_restapis": BuildDocRESTAPI,
          "build_package": BuildPackage,
      },
      include_package_data=True)
