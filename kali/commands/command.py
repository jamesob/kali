#!/usr/bin/python

import argparse
import logging as lg
import inspect
import os

from kali.data.datum import Datum

class Command(object):
    """
    A command within Kali. For each Command, the docstring will serve as the
    help.
    """
    
    uniqueName   = None
    requiredData = None
    optionalData = None

    def __init__(self):
        self.requiredData = self.requiredData or []
        self.optionalData = self.optionalData or []

        if self.uniqueName is None:
            lg.error("Command must have unique name.")
            exit(1)

    def attachToParser(self, argparser, namespace):
        """Attach this command to the ArgumentParser `argparser` using default
        values provided by `namespace`."""

        cmdParser = argparser.add_parser(self.uniqueName, 
                                         description=self.__doc__,
                                         formatter_class=argparse.ArgumentDefaultsHelpFormatter,
                                         help=self.help)

        cmdParser.set_defaults(command=self.execute)

        for d in self.requiredData:
            if isinstance(d, Datum):
                d.attachToParser(cmdParser, namespace, required=True)

        for d in self.optionalData:
            d.attachToParser(cmdParser, namespace)

    def execute(self, namespace):
        """Perform pre/post-action hooks in addition to performing the action
        itself."""
        
                                  
        self._checkPrerequisites(namespace)
        self._preAction(namespace)

        returnCode = self.action(namespace)

        self._postAction(namespace)

        return returnCode

    def _preAction(self, namespace):
        """
        To be performed before `self.action` is called.
        """
        pass

    def _postAction(self, namespace):
        """To be performed after `self.action` is called."""
        pass

    def _checkPrerequisites(self, namespace):
        """Check to see that all required data is in the namespace being acted
        upon."""

        for datum in self.requiredData:
            data_name = str(datum)

            if data_name not in namespace.__dict__.keys():
                lg.error("Datum '%s' required for command '%s'.",
                         data_name, self.uniqueName)
                exit(1)

    def action(self, n):
        """Defines the action that this Command performs. Must be overridden by
        all subclasses. `n` is a namespace which contains all values returned
        from argparse."""

        raise NotImplementedError

    def success(self, msg):
        """Signal the success of an action."""
        print msg

    def fillTemplate(self, template_filename, values):
        """Read in a template, fill it out, and return it as a string.

        :Parameters:
          - `template_filename`: The filename of the template, relative to the
            directory that contains `self`.
          - `values`: A dictionary containing values that will be used in the
            call to `.format()`.
        """
        tpl_location = os.path.join(self.containing_directory, template_filename)
        lg.debug("Attempting to open template at '%s'." % tpl_location)

        with open(tpl_location, 'r') as f:
          tpl = f.read()

        return tpl.format(**values)
         
    @property
    def help(self):
        return self.__doc__

    @property
    def extendedHelp(self):
        return self.help + """Hey foo bat barz."""

    @property
    def containing_directory(self):
        return os.path.dirname(inspect.getfile(self.__class__))




    

