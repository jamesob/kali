#!/usr/bin/python

from kali.data.datum import Datum
from kali.commands.command import Command
from kali.utilities import config

from kali.commands.core.init import instance_name

import os
                   
vhost_name = Datum("vhost_name",
                   help="Name of the vhost file to create.")
                    
site_path = Datum("site_path",
                   help="Path to site.")
                                   
class CreateVhost(Command):
    """Create an Apache vhost file for this Kali environment in Apache's
    `sites-available` directory, then symlink to it in `sites-enabled`."""

    uniqueName = "create-vhost"
    requiredData = [
        "site_path",
        "dev_environ_username",
    ]
    optionalData = [
        vhost_name,
    ]

    def action(self, n):
        tpl_location = os.path.join(self.containing_directory, "vhost.tpl")
        tpl = open(tpl_location, 'r').read()
        vhost = tpl.format(**n.__dict__)

        print vhost
            

def attach(kali):
    kali.addCommand(CreateVhost)
 
