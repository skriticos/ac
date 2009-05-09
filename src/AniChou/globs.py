
# Copyright (c) 2009 Sebastian Bartos
# See COPYING for details

""" globs -- global constants

We try to keep global constans as few as possible, but things like path and
user directory sturcture might change, and to make this kind of transitions as
painless as possible we put them in one place. Here.
"""

from os import path

# Current version string
ac_version = '9.1.6-beta'

# Path to the user directory of anichou (where data, config and plugins
# are stored).
ac_user_path = path.join(path.expanduser('~'), '.anichou')

# Path to the configuration file
ac_config_path = path.join(ac_user_path, 'ac.cfg')

# Path to log file
ac_log_path = path.join(ac_user_path, 'ac.log')

# Path to data file
ac_data_path = path.join(ac_user_path, 'ac.dat')

# Plugin path
ac_plugin_path = path.join(ac_user_path, 'plugins')

# Package base path (where the module script files are located)
ac_package_path = path.abspath(path.dirname(__file__))

