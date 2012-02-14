#!/usr/bin/python

from kali.data.datum import Datum
from kali.commands.command import Command

from kali.utilities import cmd, cautious_cmd

import os
import logging as lg
                                 
class Destroy(Command):
    """Destroy a Kali site."""

    uniqueName = "destroy"
    requiredData = ["site_path"]

    # destroy is the one command that needs a back-reference to Kali
    # for her index of commands
    kali = None

    def action(self, n):
        self.kali.destroy(n)

        os.chdir(os.path.dirname(n.site_path))
        cautious_cmd("rm", ["-r", "-f", n.site_path])
        lg.info("Removed Kali site at %s." % n.site_path)

def attach(kali):
    kali.addCommand(Destroy)
    Destroy.kali = kali

