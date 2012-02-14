#!/usr/bin/python

import argparse

class Datum(object):
    """Signifies an argument to a Kali Command."""

    uniqueName = None
    
    def __init__(self, name, help,
                             default=None,
                             flags=None, 
                             nargs=None, 
                             type=str):
        """Construct a datum.

        If a deep understanding of this process is really desired, check out
        the argparse docs.

        :Parameters:
          - `name`: The name of the argument.
          - `help`: A help string for the argument.
          - `default`: A default value for the argument.
          - `flags`: Flags that serve as an alias for the argument.
          - `nargs`: The number of arguments.
          - `type`: The type of argument.
        """
        self.name = name
        self.help = help
        self.default = default
        
        if flags is not None:
            self.flags = flags if type(flags) in [list, tuple] else [flags]
        else:
            self.flags = flags

        self.nargs = nargs
        self.type = type

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
        if self.type == bool:
            store_action = 'store_true'

        kwargs = {"action": store_action,
                  "nargs": self.nargs,
                  "help": self.help,
                  "type": self.type,}
 
        
        kwargs["default"] = self.default or namespace.__dict__.get(self.name, None)

        
                                                  
        if required: # we are a positional arg
            parser.add_argument(self.name, **kwargs)
        else: 
            parser.add_argument('--' + self.name,
                                dest=self.name,
                                required=required,
                                **kwargs)
         

