#!/usr/bin/python

from kali.data.datum import Datum
from kali.commands.command import Command
from kali.utilities import config

import os
                                 
class Init(Command):
    """Print available configuration data."""

    uniqueName = "config"
    requiredData = []

    def action(self, n):
        print(self._configurationData)
 
    @property 
    def _configurationData(self):
        """A string containing a formatted representation of the configuration
        data."""

        configStr = ""

        for sectionName, configDict in config.dataBySection.iteritems():
            configStr += "\n  [%s]\n" % sectionName

            for name, val in configDict.iteritems():
                configStr += "    %s: %s\n" % (name, val)

        return configStr
     
def attach(kali):
    kali.addCommand(Init)

