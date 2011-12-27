#!/usr/bin/python

from kali.data.datum import Datum
from kali.commands.command import Command

from kali.utilities import cmd, cautious_cmd

import os
import logging as lg
                                 
class Destroy(Command):
    """Destroy a Kali site."""

    uniqueName   = "destroy"
    requiredData = ["site_path"]

    def action(self, n):
        cautious_cmd("rm", ["-r", "-f", n.site_path])
        lg.info("Removed Kali site at %s." % n.site_path)

def attach(kali):
    kali.addCommand(Destroy)

