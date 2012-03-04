# kali: a horrifying build tool for LAMPD

Inspired by Erik Summerfield's `Shiva`.

## What?

Kali is a tool written in Python that promotes a sane structure for complex
Drupal builds. It tries to automate boilerplate tasks that arise during
development of Drupal sites.

Kali reduces to a nice wrapper around various Python libraries, namely
`argparse`, `logging`, and `subprocess`. Kali's `Command` classes are
subclassed to create new subcommands on an `ArgParser` instance.

## Why?

Drupal, because it is a relatively cluttered and complex CMS framework, has
complicated conventions for how projects should be managed. Unlike other
frameworks, there is no automated way to reduce the complexity and level of
effort for setting up a multi-developer project. 

Boilerplate activities like MySQL and vhost setup are boring, and the details
of their setup can be located and derived from one place.

## Using kali

### As a Drupal developer

After plugins have been specified and added to the necessary directory by a kali
developer, using kali is self-explanatory via `--help` flags:

    $ kali --help
    usage: kali [-h] [-v] {destroy,init,config,create-vhost} ...

    Kali: a horrifying build tool for LAMPD stacks.

    optional arguments:
      -h, --help            show this help message and exit
      -v, --version         show program's version number and exit

    commands:
      Valid commands

      {destroy,init,config,create-vhost}
        destroy             Destroy a Kali site.
        init                Initialize a new Kali-backed Drupal environment.
        config              Print available configuration data.
        create-vhost        Create an Apache vhost file for this Kali environment
                            in Apache's `sites-available` directory, then symlink
                            to it in `sites-enabled`.

Each subclass of `Command` creates a `sub-parser` with its own arguments and help:

    $ kali init --help
    usage: kali init [-h] instance_name

    Initialize a new Kali-backed Drupal environment.

    positional arguments:
      instance_name  Name of the Kali project to create.

    optional arguments:
      -h, --help     show this help message and exit

#### Setting up a new project

Use `init` to initialize a kali-aware project directory:

    $ kali init foobar
    Initialized new Kali instance 'foobar'.

    $ cd foobar/

    $ ls .kali/
    config

    $ kali config

      [Environment]
        site_path: /Users/job/foobar
        username: job
        domain: fayze2.com
        operating_system: not ubuntu
        name: foobar
        hostname: broderick.westell.com

      [Apache]
        apache_sites_available: /etc/httpd/sites-available
        apache_sites_enabled: /etc/httpd/sites-enabled
        apache_ctl: /etc/init.d/httpd

Once in a kali-aware directory, configuration and logging will be located in
`.kali`. Feel free to modify the human-readable `config` file.

### As a kali developer

The most common entry point for someone hacking on kali is going to be the 
`kali.commands` module. The `kali.commands.command.Command` class is the parent
class of any kali command; it offers a Template pattern for adding functionality
to kali.

Let's look at an example that exhibits most of the functionality that kali 
commands offer: `CreateVhost`.
 
First, we do some importing

```python
#!/usr/bin/python

from kali.data import Datum
from kali.data.common import site_type
from kali.commands.command import Command
from kali import config
from kali.utilities import cautious_cmd
```
 
- The `Datum` class is used to attach arguments to a new `Command`; it includes
  a few options for things like attaching help-text and default values.
- The `site_type` import is for a pre-existing `Datum` that may be shared
  between various `Command`s.
- `Command`, intuitively is our base Template class.
- `kali.config` is a wrapper around ConfigParser that allows easy access and
  modification to the `.kali/config` file. It is typically only imported if you
  intend on modifying the config file; existing config parameters are rolled
  into a namespace object you have access to (explanation coming up).
- `cautious_cmd` is a way to execute shell commands with automated logging,
  failing if return code isn't 0.
             
These are simple utility functions used later in the `Command`; their content
isn't that relevant to this walkthrough:
                            
```python
import os
import logging as lg
 
def make_vhost_name(site_type="dev"):
    return "%s.conf" % make_server_name(site_type)

def make_server_name(site_type="dev"):
    """Return a suitable name for a vhost configuration file."""
    g = lambda n: config.get("Environment", n)

    user = g("username")
    name = g("name")
    hostname = g("hostname")
    domain = g("domain")

    return "%s.%s-%s.%s.%s" % (user, name, site_type, hostname, domain)
```
 
Next is the establishment of a `Datum` that dictates what the vhost filename
will be.
    
```python
vhost_name = Datum("vhost_name",
                   default=make_vhost_name(),
                   help="Name of the vhost file to create.")
```

Here is the bulk of the file; the `Command` subclass.
                     
```python
class CreateVhost(Command):
    """Create an Apache vhost file for this Kali environment in Apache's
    `sites-available` directory, then symlink to it in `sites-enabled`."""
```
  
The docstring for a `Command` subclass is used automatically for its argparse
help-text.
 
```python

    uniqueName = "create-vhost"

    requiredData = [
        "site_path",
        "username",
    ]

    optionalData = [
        vhost_name,
        site_type,
    ]
```

- `uniqueName` is a required class-level attribute that uniquely identifies a
  command. It will be the name used to invoke the command on the commandline.
- `requiredData` is an optional list that can be specified. It includes a mix
  of strings and `Datum` object references. Strings are for data that should
  exist in config file, whereas `Datum` references are for arguments that will
  be taken from the commandline.
- `optionalData` expects the same thing as `requiredData`, but all specified
  data is optional.

```python

    def action(self, n):
        vhost_filename = make_vhost_name(n.site_type)
        config.add(n.site_type, "vhost_filename", vhost_filename)

        fill_args = dict(n.__dict__, server_name=make_server_name(n.site_type))
        vhost = self.fillTemplate("vhost.tpl", fill_args)

        vhost_path, active_path = self._getApachePaths(vhost_filename)

        cautious_cmd("tee", vhost_path, sudo=True, stdin=vhost)
        cautious_cmd("ln", ['-s', vhost_path, active_path], sudo=True)

        self.success("Created and activated vhost.")
```

The meat and potatos of an any `Command` subclass is in its `action` method.
This specifies what happens when the command is invoked. It takes one
parameter, which is a namespace object where all data is attached as an
attribute. In other words, if you have a piece of data in config called
"site_name", it will be accessible as `n.site_name`. Likewise with data
specified on the commandline. 

At the end of the action, `self.success` is called with a message indicating
the successful completion of an action.

```python
    def destroy(self, n):
        vhost_names = config.get_all("vhost_filename")

        for filename in vhost_names:
            vhost_path, active_path = self._getApachePaths(filename)
            cautious_cmd("rm", [vhost_path, active_path], sudo=True)

        self.destroy_success("Destroyed vhosts.")
```

Each action can have a method called `destroy`, which again takes a namespace,
and is responsible for disassembling all artifacts that have been created
by this action.

```python
    def _getApachePaths(self, filename):
        """Return a tuple containing the paths to the available and active
        Apache vhost paths based on `filename`, in that order."""
        vhosts_dir = config.get("Apache", "apache_sites_available")
        active_dir = config.get("Apache", "apache_sites_enabled")
        vhost_path = os.path.join(vhosts_dir, filename)
        active_path = os.path.join(active_dir, filename)

        return (vhost_path, active_path)
```

This is just a utility method, called from the action.
         

```python
def attach(kali):
    kali.addCommand(CreateVhost)
```

Finally, the last component of this file is a function called `attach`, 
which is required and takes as its only argument a `Kali` instance. `Kali`
visits each module specified in `kali/commands/__init__.py`, injecting itself
into this function.

We register `CreateVhost` with kali as a command. Any subclass of command
must be imported into `kali/commands/__init__.py` to be visited.

## Fruits

Here's the result of our work:

```python
$ kali create-vhost --help
usage: kali create-vhost [-h] [--vhost_name VHOST_NAME]
                         [--site_type SITE_TYPE]

Create an Apache vhost file for this Kali environment in Apache's `sites-
available` directory, then symlink to it in `sites-enabled`.

optional arguments:
  -h, --help            show this help message and exit
  --vhost_name VHOST_NAME
                        Name of the vhost file to create. (default: job
                        .foobar-dev.broderick.westell.com.fayze2.com.conf)
  --site_type SITE_TYPE
                        The type of site, e.g. dev, int, prod. (default: dev)
```

### Logging

Logging from within a `Command` can easily accessed by importing `lg`:

```python
import logging as lg

lg.info("Hey!") 
lg.debug("Creating config.")
```

All log statements will be added to `.kali/log`, but only `lg.info` calls
and above will be displayed on the commandline.

### Further details

Read the code! It's meant to be friendly. 

## TODO

- TESTS!
- Establish `Command`s for set up of directory structure and actual builds.
- Dry run functionality


