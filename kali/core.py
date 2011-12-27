#!/usr/bin/python

import argparse
import os
import inspect
import logging as lg

import data
import commands
import utilities as utils

from kali import config 

class Kali(object):
    """Kali: a horrifying build tool for LAMPD stacks."""

    def __init__(self):
        # Dictionary of available commands
        self.commands = {}

        # Namespace used to hold all data in Kali
        self.data_namespace = argparse.Namespace()

        # Initialize and load configuration data
        self._loadConfigurationData()

        # Initialize logging facilities
        utils.initializeLogger()
        lg.info("Started Kali.")

        if config.location is None:
            lg.debug("Configuration couldn't be loaded.")

        # Initialize the commandline argument parser
        self.parser = argparse.ArgumentParser(
            description=self.__doc__,
            formatter_class = argparse.ArgumentDefaultsHelpFormatter,
            version='2.0',
            prog='kali',
        )

        # Load data and commands into Kali's registry. 
        self._loadCommands()

        # Assemble the parser given the data and commands we've loaded into the
        # registry.
        self._buildParser()


    def go(self):
        self._runParser()

        # call the requested command on Kali's complete namespace
        return_code = self.data_namespace.command(self.data_namespace)

        exit() if return_code is None else exit(return_code)

    def help(self):
        self._runParser(args = ['-h'])

    """
    Configuration loading methods
    """
    def _loadConfigurationData(self):
        """Load in all data from the Kali configuration and populate Kali's
        namespace."""

        for sectionName, configDict in config.dataBySection.iteritems():
            for name, value in configDict.iteritems():
                self.data_namespace.__dict__[name] = value

    """
    Command loading methods
    """
    def _loadCommands(self):
        """Load `Command` objects into the Kali `commands` dict."""

        self._loadBuiltinCommands()
        self._loadPluginCommands()

    def _loadBuiltinCommands(self):
        # for each module in command
        for name, obj in inspect.getmembers(commands):
            if inspect.ismodule(obj) and hasattr(obj, 'attach'):
                if inspect.isfunction(obj.attach):
                    # attach kali to all commands in module
                    obj.attach(self) 
    
    def _loadPluginCommands(self):
        pass

    def addCommand(self, commandClass):
        """Attach a Command to Kali by passing its class, `commandClass`."""

        command = commandClass()
        self.commands[command.uniqueName] = command

    def addCommands(self, *commandClasses):
        """Attach multiple Commands to Kali by passing their classes,
        `commandClasses`."""

        for c in commandClasses:
            self.addCommand(c)


    """
    Commandline parser operations
    """
    def _buildParser(self):
        subparsers = self.parser.add_subparsers(
            title='commands',
            description='Valid commands',
            dest='command_name',
        )

        for name, command in self.commands.iteritems():
            # pass in a namespace so we can provide default values for
            # arguments.
            command.attachToParser(subparsers, self.data_namespace)
     
    def _runParser(self, args=None):
        """Get commandline arguments, merge in configuration data, return
        resulting namespace. Optionally, parse `args`."""

        # get arguments from the commandline
        cmdline_namespace = self.parser.parse_args(args)

        # merge in configuration data
        self._mergeArgumentsAndConfig(cmdline_namespace)
        
                               
    def _mergeArgumentsAndConfig(self, cmdline_namespace):
        """Merge the cmdline arguments, `cmdline_namespace`, into Kali's global
        namespace, `data_namespace`, which currently only contains data loaded
        from the configuration file. 
        
        Log any conflicts."""

        cmdline_dict = cmdline_namespace.__dict__

        for name, value in cmdline_dict.iteritems():
            # if a config value has been overridden by an argument:
            if name in self.data_namespace.__dict__.keys(): 
                lg.debug("Datum '%s' with value '%s' overridden by '%s'." \
                         % (name, self.data_namespace.__dict__[name], value))
                self.data_namespace.__dict__[name] = value
            else:
                lg.debug("Merging in datum '%s' with value '%s'." % (name, value))
                self.data_namespace.__dict__[name] = value
            
if __name__ == '__main__':
    import sys

    s = Kali()

    if len(sys.argv) <= 1:
        s.help()
    else:
        args = s.go()

