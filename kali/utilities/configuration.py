#!/usr/bin/python

import ConfigParser
import logging as lg
import os
import re
import socket 

TOP_LEVEL_DOMAIN = "fayze2.com"

class KaliConfiguration(object):
    """Responsible for managing all Kali configuration data, which is created
    on `kali init [instance_name]`. This is a singleton class."""

    CONFIG_DIR_NAME  = ".kali"
    CONFIG_FILE_NAME = "config"


    """Singleton stuff"""
    _instance = None
    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(KaliConfiguration, cls).__new__(cls, *args,
                    **kwargs)

        return cls._instance

    @staticmethod
    def configDirName(path):
        """Return the path to the Kali config directory based on `path`."""
        return os.path.join(path, KaliConfiguration.CONFIG_DIR_NAME) 

    @staticmethod
    def configFileName(path):
        """Return the path to the Kali config file based on `path`."""
        return os.path.join(KaliConfiguration.configDirName(path), 
                            KaliConfiguration.CONFIG_FILE_NAME) 

    @staticmethod
    def findConfig(cwd):
        """Return the path of an existing Kali configuration file in the
        directory tree above. If none exists, return `None`."""
        cwd = os.getcwd()

        configLoc = None

        while configLoc == None and cwd != "/":
            tryThisDir = KaliConfiguration.configDirName(cwd)
            tryThisFile = KaliConfiguration.configFileName(cwd)

            # is the kali config directory in cwd?
            if os.path.isdir(tryThisDir) and os.path.isfile(tryThisFile):
                configLoc = tryThisFile
            else:
                cwd = os.path.split(cwd)[0]

        return configLoc
                      
    def __init__(self):
        self.parser = ConfigParser.SafeConfigParser()

        self.location = KaliConfiguration.findConfig(os.getcwd())

        # if we have an existing config file
        if self.location is not None:
            self.path = os.path.split(self.location)[0]
            self.parser.read(self.location) # load config data

    def addData(self, section, key, value):
        self.parser.set(section, key, value)

        self._writeConfig()


    @property
    def dataBySection(self):
        """Return a dict keyed by section string and valued by a dict containing
        the settings under that section."""

        returnDict = {}
        sections = self.parser.sections()

        for section in sections:
            returnDict[section] = dict(self.parser.items(section))

        return returnDict


    def createConfig(self, directory):
        """Create a Kali configuration directory within `directory`."""

        # establish OS
        opsys = "ubuntu" if "ubuntu" in os.uname()[3].lower() else "not ubuntu"

        apache_dir_name = "apache2" if (opsys == "ubuntu") else "httpd"

        try:
            os.mkdir(KaliConfiguration.configDirName(directory))
        except OSError:
            lg.error("Failed to make configuration directory.")
            exit()

        instance_name = os.path.basename(directory)
        user = os.environ['USER']
        hostname = socket.gethostname()
        server_name = '%s.%s.%s.%s' \
                % (user, instance_name, hostname, TOP_LEVEL_DOMAIN)
             
        self.parser.add_section("Environment")

        self.parser.set('Environment', 'site_path', directory)
        self.parser.set('Environment', 'server_name', server_name)
        self.parser.set('Environment', 'system_username', user)
        self.parser.set('Environment', 'dev_environ_username',
                                       self._getDevUsername())
        self.parser.set('Environment', 'operating_system', opsys)

        self.parser.add_section("Apache")

        self.parser.set('Apache', "apache_ctl", 
                                  "/etc/init.d/%s" % apache_dir_name)
        self.parser.set('Apache', "apache_sites_available",
                                  "/etc/%s/sites-available" % apache_dir_name)
        self.parser.set('Apache', "apache_sites_enabled",
                                  "/etc/%s/sites-enabled" % apache_dir_name)

        self._writeConfig(pathToConfig=KaliConfiguration.configFileName(directory))

    def _getDevUsername(self):
        """Return the username that owns the current development
        environment. If we're not in a subdir of /opt/development, return None."""

        dev_environ_path = re.match(r'/opt/development/(\w+)', os.getcwd())

        dev_environ_username = ''

        if dev_environ_path is not None:
            dev_environ_username = dev_environ_path.group(1)
        else:
            lg.warn("I noticed you're not in an /opt/development/ subdirectory. "
                    + "That's weird.")

        return dev_environ_username
                              
    def _writeConfig(self, pathToConfig=None):
        """Writes current state of the ConfigParser out to the Kali config
        file."""

        if pathToConfig is None:
            pathToConfig = KaliConfiguration.findConfig(os.cwd())
        
        with open(pathToConfig, 'wb') as cfgFile:
            self.parser.write(cfgFile)

        lg.debug("Configuration file successfully written.")

