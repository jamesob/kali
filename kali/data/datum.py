#!/usr/bin/python

import argparse

class Datum(object):
    """Signifies an argument to a Kali Command... Basically a piece of data
    floating around the system."""

    uniqueName = None
    
    def __init__(self, name, help,
                             saveToConfig=False,
                             section=None,
                             flags=None, 
                             nargs=None, 
                             type=str, 
                             boolean=False):
        self.name = name
        self.help = help
        self.saveToConfig = saveToConfig
        self.section = section
        
        # if `flags` is None, we are a positional argument
        if flags is not None:
            self.flags = flags if type(flags) in [list, tuple] else [flags]
        else:
            self.flags = flags

        self.nargs = nargs
        self.boolean = boolean
        self.type = type
        self.default = None

        self.value = None

    def __str__(self):
        return self.name

    def attachToParser(self, parser, namespace, required=False):
        """Attach this piece of Datum to a parser; i.e., make this datum usable
        by a `Commmand` in the system. Optionally, this Datum could be
        `required` for the parser it's attached to. A default value will be
        extracted from `namespace` if one is present, i.e. if a value for this
        was in the config file.
        
        This is called in `Command.attachToParser`.

        :Parameters:
          - `parser` (argparse.Parser): the parser to attach to
          - `namespace` (argparse.Namespace): contains potential default values
            from kali.config.
          - `required` (boolean): is this parameter required?
        """

        store_action = 'store'
        if self.boolean:
            store_action = 'store_true'

        kwargs = {"action": store_action,
                  "nargs": self.nargs,
                  "help": self.help,
                  "type": self.type,}
 
        # if the argument has a default value imported from kali.config, use it
        if self.name in namespace.__dict__.keys():
            kwargs["default"] = namespace.__dict__[self.name]
            print kwargs["default"] + "FOUND"
                                                  
        if required: # we are a positional arg
            parser.add_argument(self.name, **kwargs)
        else: 
            parser.add_argument('--' + self.name,
                                dest=self.name,
                                required=required,
                                **kwargs)
         

