#!/usr/bin/python

from kali.data.datum import Datum
from kali.commands.command import Command
from kali.utilities import config

import os
 
instance_name = Datum("instance_name",
                      help="Name of the Kali project to create.")
                                  
class Init(Command):
    """Initialize a new Kali-backed Drupal environment."""

    uniqueName = "init"
    requiredData = [instance_name]

    def action(self, n):
        """Attempt to create a new Kali environment by creating a directory of
        the name `n.instance_name` and a Kali configuration file within that
        directory."""

        print(n.instance_name)
        print("HEY!")
        newPath = os.path.join(os.getcwd(), n.instance_name)

        try:
            os.mkdir(newPath)
        except OSError:
            return False

        config.createConfig(newPath)

def attach(kali):
    kali.addCommand(Init)

