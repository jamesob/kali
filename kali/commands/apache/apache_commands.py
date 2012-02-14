#!/usr/bin/python

from kali.data import Datum
from kali.data.common import site_type
from kali.commands.command import Command
from kali import config
from kali.utilities import cautious_cmd

import os
import logging as lg
 
def make_vhost_name(site_type="dev"):
    return "%s.conf" % make_server_name(site_type)

def make_server_name(site_type="dev"):
    """Return a suitable name for a vhost configuration file."""
    g = lambda n: config.get("Environment", n)

    user = g("username")
    name = g("name")
    hostname = g("hostname")
    domain = g("domain")

    return "%s.%s-%s.%s.%s" % (user, name, site_type, hostname, domain)
                           
vhost_name = Datum("vhost_name",
                   default=make_vhost_name(),
                   help="Name of the vhost file to create.")
                    
class CreateVhost(Command):
    """Create an Apache vhost file for this Kali environment in Apache's
    `sites-available` directory, then symlink to it in `sites-enabled`."""

    uniqueName = "create-vhost"

    requiredData = [
        "site_path",
        "username",
    ]

    optionalData = [
        vhost_name,
        site_type,
    ]

    def action(self, n):
        vhost_filename = make_vhost_name(n.site_type)
        config.add(n.site_type, "vhost_filename", vhost_filename)

        fill_args = dict(n.__dict__, server_name=make_server_name(n.site_type))
        vhost = self.fillTemplate("vhost.tpl", fill_args)

        vhost_path, active_path = self._getApachePaths(vhost_filename)

        cautious_cmd("tee", vhost_path, sudo=True, stdin=vhost)
        cautious_cmd("ln", ['-s', vhost_path, active_path], sudo=True, stdin=vhost)

        self.success("Created and activated vhost.")

    def destroy(self, n):
        vhost_names = config.get_all("vhost_filename")

        for filename in vhost_names:
            vhost_path, active_path = self._getApachePaths(filename)
            cautious_cmd("rm", [vhost_path, active_path], sudo=True)

        self.destroy_success("Destroyed vhosts.")
            
    def _getApachePaths(self, filename):
        """Return a tuple containing the paths to the available and active
        Apache vhost paths based on `filename`, in that order."""
        vhosts_dir = config.get("Apache", "apache_sites_available")
        active_dir = config.get("Apache", "apache_sites_enabled")
        vhost_path = os.path.join(vhosts_dir, filename)
        active_path = os.path.join(active_dir, filename)

        return (vhost_path, active_path)
         

def attach(kali):
    kali.addCommand(CreateVhost)

