#!/usr/bin/python

import ConfigParser
import logging as lg
import os
import re

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

    def configDirName(self, path):
        """Return the path to the Kali config directory based on `path`."""
        return os.path.join(path, self.CONFIG_DIR_NAME) 

    def configFileName(self, path):
        """Return the path to the Kali config file based on `path`."""
        return os.path.join(self.configDirName(path), 
                            self.CONFIG_FILE_NAME) 

    def findConfig(self):
        """Return the path of an existing Kali configuration file in the
        directory tree above. If none exists, return `None`."""
        cwd = os.getcwd()

        configLoc = None

        while configLoc == None and cwd != "/":
            tryThisDir = self.configDirName(cwd)
            tryThisFile = self.configFileName(cwd)

            # is the kali config directory in cwd?
            if os.path.isdir(tryThisDir) and os.path.isfile(tryThisFile):
                configLoc = tryThisFile
            else:
                cwd = os.path.split(cwd)[0]

        return configLoc
                      
    def __init__(self):
        self.parser = ConfigParser.SafeConfigParser()

        self.location = self.findConfig()

        # if we have an existing config file
        if self.location is not None:
            self.path = os.path.split(self.location)[0]
            self.parser.read(self.location) # load config data

    def addSection(self, section):
        """Add a new section to Kali's configuration."""
        return self.parser.add_section(section)
        
    def add(self, section, key, value):
        """Add configuration to Kali."""
        if not self.parser.has_section(section):
            lg.debug("Adding section '%s'." % section)
            self.addSection(section)

        lg.debug("Adding %s:%s to section %s of config." \
            % (key, value, section))
        self.parser.set(section, key, value)

        self.save()

    def get(self, section, key, default=None):
        """Get data from the configuration."""
        val = None

        try: 
            val = self.parser.get(section, key)
        except ConfigParser.NoSectionError:
            pass

        return val

    def get_all(self, key_like):
        """Return all values where `key_like` is in key, independent of
        section."""
        vals = []

        for sect, settings in self.dataBySection.items():
            for key, val in settings.items():
                if key_like in key:
                    vals.append(val)

        return vals

    @property
    def dataBySection(self):
        """Return a dict keyed by section string and valued by a dict containing
        the settings under that section."""

        returnDict = {}
        sections = self.parser.sections()

        for section in sections:
            returnDict[section] = dict(self.parser.items(section))

        return returnDict
    
    def save(self, cfg_filename=None):
        """Writes current state of the ConfigParser out to the Kali config
        file."""
        
        pathToConfig = cfg_filename or self.findConfig()
        assert pathToConfig, "Must be in a Kali directory tree to modify config."

        lg.debug("Saving config to %s." % pathToConfig)

        with open(pathToConfig, 'wb') as cfgFile:
            self.parser.write(cfgFile)

        lg.debug("Configuration file successfully written.")

