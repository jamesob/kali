#!/usr/bin/python

import logging
import os
from .configuration import KaliConfiguration

config = KaliConfiguration()

def initializeLogger():
    
    logging.getLogger().setLevel(logging.DEBUG)
    appenders = [makeStdoutAppender()]

    if config.exists():
        appenders.append(makeLogfile())

    for a in appenders:
        logging.getLogger().addHandler(a)

    logging.debug("Initialized logger.")

def makeLogfile():
    log_filename = os.path.join(os.path.dirname(config.findConfig()), "log")
    flog = logging.FileHandler(log_filename)
    flog.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s - %(levelname)s: %(message)s')
    flog.setFormatter(formatter)

    return flog

def makeStdoutAppender():
    ch = logging.StreamHandler()
    ch.setLevel(logging.INFO)
    formatter = logging.Formatter('%(message)s')
    ch.setFormatter(formatter)

    return ch
                         
