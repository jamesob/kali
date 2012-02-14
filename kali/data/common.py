from .datum import Datum

"""This file contains arguments that are commonly used in Kali and are likely to
appear across multiple commands.
"""

site_type = Datum("site_type",
                  default="dev",
                  help="The type of site, e.g. dev, int, prod.")
     
