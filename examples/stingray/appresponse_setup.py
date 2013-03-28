#!/usr/bin/env python

# Copyright (c) 2013 Riverbed Technology, Inc.
#
# This software is licensed under the terms and conditions of the 
# MIT License set forth at:
#   https://github.com/riverbed/flyscript/blob/master/LICENSE ("License").  
# This software is distributed "AS IS" as set forth in the License.


import optparse

from rvbd.stingray.app import StingrayTrafficManagerApp

class App(StingrayTrafficManagerApp):

    def add_options(self, parser):
        group = optparse.OptionGroup(parser, 'Stingray / AppResponse Setup Options')
        group.add_option('--vserver', dest='vserver',
                         help='Name of the vserver to set up')
        group.add_option('--clientid', dest='clientid',
                         help='Client ID to use for metrics')
        group.add_option('--appid', dest='appid',
                         help='Application ID to use for metrics')
        group.add_option('--host', dest='host', default='all',
                         help='Restrict to a specific host')
        parser.add_option_group(group)
        
    def main(self):
        trafficscript = '''
# A virtual server can manage multiple hosts, each of which you can
# monitor individually by creating a new Application for each host
# in Opnet Appresponse Xpert.
#

# Check that this is an HTML document
$contentType = http.getResponseHeader( "Content-Type" );
if( ! string.startsWith( $contentType, "text/html" ) ) break;    
'''

        if self.options.host != 'all':
            trafficscript += '''
# Check that this matches the hostnames we specified
$host = http.getHeader( "Host" );
if( ! string.startsWith( $host, \"%s\") ) {
    break;
}
''' % self.options.host

        trafficscript += '''
# Capture the body of the HTML document and assign
# the ARX JavaScript snippet to the $script variable
$body = http.getResponseBody();
$script =
"\\n<script type=\\"text/javascript\\">\\n\\
    var OPNET_ARXS={startJS:Number(new Date()),\\n\\
    clientId:\\"%s\\",appId:%s};\\n\\
    (function(){\\n\\
        var w=window,l=w.addEventListener,m=w.attachEvent,\\n\\
        d=document,s='script',t='load',o=OPNET_ARXS,\\n\\
        p=(\\"onpagehide\\" in w),e=p?\\"pageshow\\":t,\\n\\
        j=d.createElement(s),x=d.getElementsByTagName(s)[0],\\n\\
        h=function(y){o.ldJS=new Date();o.per=y.persisted;},\\n\\
        i=function(y){o.ld=1;};j.async=1;j.src=\\n\\
        ((o.https_snippet||'https:'==d.location.protocol)?\\n\\
        'https://c309424.ssl':'http://c309424.r24')+\\n\\
        '.cf1.rackcdn.com/opnet_arx_saas.js';\\n\\
        x.parentNode.insertBefore(j, x);\\n\\
        if(l){l(e,h,false);if(p){l(t,i,false);}}else if(m)\\n\\
        {m(\\"on\\"+e,h);if(p){m(\\"on\\"+t,i);}}\\n\\
    })();\\n\\
</script>\\n";
    
# Insert the JavaScript snippet immediately after the <HEAD> element
if( string.regexmatch( $body, "^(.*?)(<head.*?>)(.*)$", "i" ) ) {
    http.setResponseBody( $1 . $2 . $script . $3 );
} 
''' % (self.options.clientid, self.options.appid)
        
        # Call to the stingray to create the rule
        self.stingray.create_trafficscript_rule (self.options.vserver, trafficscript)


if __name__ == '__main__':
    App().run()
