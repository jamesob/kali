#!/usr/bin/python

import logging

def initializeLogger():
    
    logging.getLogger().setLevel(logging.DEBUG)

    # output all INFO-level logs to stdout
    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(message)s')
    ch.setFormatter(formatter)

    logging.getLogger().addHandler(ch)

    logging.debug("Initialized logger.")

