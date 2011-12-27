#!/usr/bin/python

import subprocess
import logging as lg

def cmd(command, params=None, sudo=False, stdin=None, cwd=None):
    """Execute `command` with parameters `params`, optionally as a superuser if
    `sudo` is True. Return the command'ss response as 
    (stdout, stderr, return-code)."""

    commandList = _buildCmd(command, params, sudo)

    process = subprocess.Popen(commandList, 0, None,
                               stdin=subprocess.PIPE, 
                               stdout=subprocess.PIPE, 
                               stderr=subprocess.PIPE, 
                               cwd=cwd)

    (stdout, stderr) = process.communicate(input=stdin)

    return (stdout, stderr, process.returncode)

def cautious_cmd(command, params=None, sudo=False, stdin=None, cwd=None):
    """Run command; if the return code isn't 0, throw errors and die."""

    (stdout, stderr, retCode) = cmd(command, params=params,
                                             sudo=sudo,
                                             stdin=stdin,
                                             cwd=cwd)       

    if retCode != 0:
        cmdString = ' '.join(_buildCmd(command, params, sudo))
        lg.error("Running command '%s' failed.\n"
                 + "  stdout: %s\n"
                 + "  stderr: %s\n"
                 + "  return code: %s", 
                 cmdString, stdout, stderr, retCode)
        exit(1)

def _buildCmd(command, params, sudo):
    """Build up a list of strings that signifies a command."""
 
    command = [command]

    if params is not None:
        params = [params] if type(params) == str else params
        command += params

    if sudo:
        command = ['sudo'] + command

    return command
               
