#!/usr/bin/python

from kali.data.datum import Datum
from kali.commands.command import Command
from kali.utilities import config

import socket 
import os
import logging as lg
 
instance_name = Datum("instance_name",
                      help="Name of the Kali project to create.")

TOP_LEVEL_DOMAIN = "fayze2.com"
                                  
class Init(Command):
    """Initialize a new Kali-backed Drupal environment."""

    uniqueName = "init"
    requiredData = [instance_name]


    def action(self, n):
        """Attempt to create a new Kali environment by creating a directory of
        the name `n.instance_name` and a Kali configuration file within that
        directory."""

        newPath = os.path.join(os.getcwd(), n.instance_name)

        lg.info("Trying at %s" % newPath)

        try:
            if not os.access(newPath, os.F_OK):
                os.mkdir(newPath)
        except:
            lg.warn("Couldn't initialize Kali at '%s'." % newPath)
            return False

        lg.debug("Creating config.")
        self.initConfig(newPath)
        self.success("Initialized new Kali instance '%s'." % n.instance_name)
    
    def initConfig(self, directory):
        dot_dir = config.configDirName(directory)

        try:
            os.mkdir(dot_dir)
        except OSError:
            lg.error("Failed to make configuration directory.")
            exit()

        os.chdir(directory)
        config.save(os.path.join(dot_dir, config.CONFIG_FILE_NAME))
 
        opsys = "ubuntu" if "ubuntu" in os.uname()[3].lower() else "not ubuntu"
        apache_dir_name = "apache2" if (opsys == "ubuntu") else "httpd"
        instance_name = os.path.basename(directory)
        user = os.environ['USER']
        hostname = socket.gethostname()
             
        config.addSection("Environment")
        config.add('Environment', 'site_path', directory)
        config.add('Environment', 'name', instance_name)
        config.add('Environment', 'hostname', hostname)
        config.add('Environment', 'domain', TOP_LEVEL_DOMAIN)
        config.add('Environment', 'username', user)
        config.add('Environment', 'operating_system', opsys)

        config.addSection("Apache")
        config.add('Apache', "apache_ctl", "/etc/init.d/%s" % apache_dir_name)
        config.add('Apache', 
                   "apache_sites_available", 
                   "/etc/%s/sites-available" % apache_dir_name)
        config.add('Apache', 
                   "apache_sites_enabled",
                   "/etc/%s/sites-enabled" % apache_dir_name)

def attach(kali):
    kali.addCommand(Init)

