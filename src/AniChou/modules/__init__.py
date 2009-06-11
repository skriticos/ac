"""
Auto-load one level of modules.

When anything references the package marked by this init, including the
following, it is executed.

import here
import here.sub
from here import sub

Upon execution it will load all modules in its directory (no subdirectories).
It does not check whether something was loaded into the interpreter already,
as init itself will normally only be executed once.

The modules will not appear in any namespace, unless they take action to do
so.

This mechanism will currently fail if a plugin has (platform-specific)
dependencies that are not available. A simple try/except would help.

Explicit loading of a subset of available modules should take place elsewhere.
This code would then have to be removed.
"""
import os
import os.path

# Path is where init lives.
pluginfiles = [fname[:-3] for fname in os.listdir(__path__) if fname.endswith(".py")]
# From http://pytute.blogspot.com/2007/04/python-plugin-system.html
imported_modules = [__import__(fname) for fname in pluginfiles]
