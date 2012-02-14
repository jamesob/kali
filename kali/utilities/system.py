#!/usr/bin/python

import subprocess
import logging as lg

def cmd(command, params=None, sudo=False, stdin=None, cwd=None, dieIfFail=False):
    """
    Execute `command` with parameters `params`, optionally as a superuser if
    `sudo` is True. 
    
    Return the command's response as (stdout, stderr, return-code).
    """

    commandList = _buildCmd(command, params, sudo)
    commandStr = ' '.join(commandList)

    lg.debug("Executing command:\n  %s" % commandStr)

    if sudo:
        lg.info("Requesting sudo to run this:\n  %s" % commandStr)

    process = subprocess.Popen(commandList, 0, None,
                               stdin=subprocess.PIPE, 
                               stdout=subprocess.PIPE, 
                               stderr=subprocess.PIPE, 
                               cwd=cwd)

    (stdout, stderr) = process.communicate(input=stdin)
    retcode = process.returncode

    if retcode != 0:
        lg.error("Running command '%s' failed.\n"
                 + "  stdout: %s\n"
                 + "  stderr: %s\n"
                 + "  return code: %s", 
                 commandStr, stdout, stderr, retcode)

        if dieIfFail:
            exit(1)
     
    return (stdout, stderr, retcode)

def cautious_cmd(*args, **kwargs):
    """Run command; if the return code isn't 0, throw errors and die."""

    kwargs["dieIfFail"] = True
    return cmd(*args, **kwargs)

def _buildCmd(command, params, sudo):
    """Build up a list of strings that signifies a command."""
 
    command = [command]

    if params is not None:
        params = [params] if type(params) == str else params
        command += params

    if sudo:
        command = ['sudo'] + command

    return command
               
