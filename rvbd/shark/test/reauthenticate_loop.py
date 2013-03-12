# Copyright (c) 2013 Riverbed Technology, Inc.
#
# This software is licensed under the terms and conditions of the 
# MIT License set forth at:
#   https://github.com/riverbed/flyscript/blob/master/LICENSE ("License").  
# This software is distributed "AS IS" as set forth in the License.


from rvbd.shark import *
from rvbd.shark.app import SharkApp
import time
import logging

logging.basicConfig(level=logging.DEBUG,
                    format="%(asctime)s [%(levelname)-5.5s] %(msg)s")

def test(app):
    t = 60
    while True:
        info = app.shark.get_serverinfo()
        print "%s Success... (sleeping for %s seconds)" % (time.ctime(time.time()), t)
        time.sleep(t)
        t = t * 2
    
app = SharkApp(main_fn = test)
app.run()
