#!/usr/bin/python

from kali.data.datum import Datum
from kali.commands.command import Command

from kali.utilities import cmd, cautious_cmd
from kali import config

import os
import logging as lg
                                 
class Destroy(Command):
    """Destroy a Kali site."""

    uniqueName = "destroy"
    requiredData = ["site_path"]

    def action(self, n):
        self.kali.destroy(n)

        lg.shutdown()
        os.chdir(os.path.dirname(n.site_path))
        # can't use lg or cautious_cmd, since it kicks to a file in .kali
        os.system("rm -rf %s" % n.site_path)
        print("Removed Kali site at %s." % n.site_path)

def attach(kali):
    kali.addCommand(Destroy)

