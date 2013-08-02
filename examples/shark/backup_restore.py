#!/usr/bin/env python

# Copyright (c) 2013 Riverbed Technology, Inc.
#
# This software is licensed under the terms and conditions of the 
# MIT License set forth at:
#   https://github.com/riverbed/flyscript/blob/master/LICENSE ("License").  
# This software is distributed "AS IS" as set forth in the License.


"""
This script performs backup and restores of configuration
to a Shark appliance.
"""

import sys
import json
import getpass
from rvbd.common.utils import DictObject
from rvbd.shark.app import SharkApp


class BackupApp(SharkApp):
    config_types = ['basic', 'auth', 'jobs', 'profiler_export', 'audit', 'protocols', 'users']

    def add_options(self, parser):
        parser.add_option('-f', '--filename',
                          help='Filename to use for backup/restore')
        parser.add_option('-b', '--backup', action='store_true',
                          help='Backup mode: store configuration to the specified file')
        parser.add_option('-r', '--restore', action='store_true',
                          help='Restore mode: apply configuration from the specified file')
        parser.add_option('-t', '--types',
                          help='Optional comma-separate list to limit the configuration '
                               'type(s) to backup/restore (options are %s).' %
                               (', '.join(self.config_types)))

    def main(self):
        if self.options.types is None:
            self.types = self.config_types
        else:
            self.types = self.options.types.split(',')
            for t in self.types:
                if not t in self.config_types:
                    raise ValueError("Invalid configuration type %s" % t)

        if self.options.filename is None:
            raise ValueError("Must specify backup/restore file")

        if self.options.backup:
            self.backup()
        elif self.options.restore:
            self.restore()
        else:
            raise RuntimeError("either backup mode (-b) or restore mode (-r) "
                               "must be specified")

    def backup(self):
        # First see if the file is there and if it has anything in it
        # already, parse it
        self.config = {}
        try:
            f = open(self.options.filename)
            self.config = json.load(f, object_hook=DictObject.create_from_dict)
            f.close()
        except Exception, e:
            print e, e.__class__

        print "Starting backup..."
        f = open(self.options.filename, 'w')

        for t in self.types:
            if t == 'basic':
                print "Backing up basic configuration..."
                self.config['basic'] = self.shark.api.settings.get_basic()

            elif t == 'auth':
                print "Backing up authentication settings..."
                self.config['auth'] = self.shark.api.settings.get_auth()

            elif t == 'audit':
                print "Backing up audit settings..."
                self.config['audit'] = self.shark.api.settings.get_audit()

            elif t == 'profiler_export':
                print "Backing up profiler export settings..."
                self.config['profiler_export'] = self.shark.api.settings.get_profiler_export()

            elif t == 'protocols':
                print "Backing up protocol names / protocol groups..."
                self.config['protocol_groups'] = self.shark.api.settings.get_protocol_groups()
                self.config['protocol_names'] = self.shark.api.settings.get_protocol_names()

            elif t == 'jobs':
                print "Backing up jobs..."
                self.config['jobs'] = [j.config for j in self.shark.api.jobs.get_all()]

            elif t == 'users':
                print "Backing up users and groups..."
                self.config['users'] = self.shark.api.auth.users.get_all()
                self.config['groups'] = self.shark.api.auth.groups.get_all()

        json.dump(self.config, f, indent=4)
        print "Backup complete."

    def restore(self):
        print 'This operation will overwrite any existing configuration on your '
        print 'Shark appliance.  Please verify that you want to continue.'
        result = raw_input('Continue?  [y/N] > ')
        if result not in ('Y', 'y'):
            print 'Okay, exiting.'
            sys.exit()

        f = open(self.options.filename)
        self.config = json.load(f, object_hook=DictObject.create_from_dict)
        f.close()

        print "Starting restore..."

        for t in self.types:
            if t == 'basic':
                print "Restoring basic configuration..."
                # XXX/demmer we may not want to do this since this
                # could change the IP address
                self.shark.api.settings.update_basic(self.config['basic'])

            elif t == 'auth':
                print "Restoring authentication settings..."
                self.shark.api.settings.update_auth(self.config['auth'])

                print "Restoring (reconnecting to shark...)"
                self.connect()

            elif t == 'audit':
                print "Restoring audit settings..."
                self.shark.api.settings.update_audit(self.config['audit'])

            elif t == 'profiler_export':
                print "Restoring profiler export settings..."
                self.shark.api.settings.update_profiler_export(self.config['profiler_export'])

            elif t == 'protocols':
                print "Restoring protocol names / protocol groups..."
                self.shark.api.settings.update_protocol_names(self.config['protocol_names'])
                self.shark.api.settings.update_protocol_groups(self.config['protocol_groups'])

            elif t == 'jobs':
                print "Restoring jobs..."

                # Don't blow away existing jobs with the same configuration
                job_config = self.shark.api.jobs.get_all()

                config_by_name = {}
                for j in job_config:
                    config_by_name[j.config.name] = j.config

                for new_job in self.config['jobs']:
                    if new_job.name in config_by_name:
                        if new_job == config_by_name[new_job.name]:
                            print "%s (skipped since already configured)..." % new_job.name
                        else:
                            print ("%s (ERROR: job exists with different configuration)..."
                                   % new_job.name)
                        continue

                    print "%s (configured)..." % new_job.name
                    self.shark.api.jobs.add(new_job)

            elif t == 'users':
                print "Restoring groups..."
                # Don't blow away existing groups with the same configuration
                group_config = self.shark.api.auth.groups.get_all()

                config_by_name = {}
                for g in group_config:
                    config_by_name[g.name] = g

                for new_group in self.config['groups']:
                    if new_group.name in config_by_name:
                        if new_group == config_by_name[new_group.name]:
                            print "%s (skipped since already configured)..." % new_group.name
                        else:
                            print ("%s (ERROR: group exists with different configuration)..."
                                   % new_group.name)
                        continue

                    print "%s..." % new_group.name
                    self.shark.api.auth.groups.add(new_group)

                print "Restoring users..."
                user_config = self.shark.api.auth.users.get_all()

                config_by_name = {}
                for u in user_config:
                    config_by_name[u.name] = u

                for new_user in self.config['users']:
                    if new_user.name in config_by_name:
                        if new_user == config_by_name[new_user.name]:
                            print "%s (skipped since already configured)..." % new_user.name
                        else:
                            print ("%s (ERROR: user exists with different configuration)..."
                                   % new_user.name)
                        continue

                    print "%s..." % new_user.name

                    # Need to coerce the structure for a new user
                    del new_user['is_admin']
                    del new_user['is_locked']

                    while True:
                        passwd = getpass.getpass("Enter password: ")
                        passwd2 = getpass.getpass("Enter password (again): ")

                        if passwd != passwd2:
                            print "ERROR: passwords do not match"
                            continue

                        new_user['password'] = passwd
                        break

                    self.shark.api.auth.users.add(new_user)

        print "Restore complete."


if __name__ == '__main__':
    BackupApp().run()
