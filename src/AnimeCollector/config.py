
# Copyright (c) 2008 Gareth Latty
# Copyright (c) 2009 Sebastian Bartos
# See COPYING for details

# config.py - configuration defaults and phraser
# Contains the default configuration and the configuration handling class.


# =======
# Imports
# =======

from ConfigParser import ConfigParser
from os import path
from globs import ac_config_path


# =========
# Constants
# =========

# Empty configuration that is used to create a blank configuration file if
# there is none.
DEFAULT_CONFIG = """\
[mal]
username =
password =
autologin = False
login_autorefresh = False

[ui]
tray_onclose = True
tray_onstartup = False

[search_dirs]   # Directories where played files are searched for
dir1 = /home
dir2 = /home/foo
"""



# =================
# Class declaration
# =================

class ac_config(ConfigParser):
	"""
	Configuration phraser and data class.
	
	Properties
		mal = {'username': str, 'password': str, 'autologin': boolean}
		ui = {'tray_onclose': boolean, 'tray_onstartup': boolean }
	"""

	def __init__(self):
		"""
		Loads and reads the configuration file.
		"""

		ConfigParser.__init__(self)

		# Create default configuration if it is missing:
		if not path.isfile(ac_config_path):
			x = open(ac_config_path, 'w')
			x.write(DEFAULT_CONFIG)
			x.close()

		self.read_file()

	
	def read_file(self):
		"""
		Read instance properties from configuration file.
		"""
		
		self.read(ac_config_path)

		# myAnimeList login credentials and options
		self.mal = dict()
		self.mal['username'] = self.get('mal', 'username')
		self.mal['password'] = self.get('mal', 'password')
		self.mal['autologin'] = self.getboolean('mal', 'autologin')
		self.mal['login_autorefresh'] = \
				self.getboolean('mal', 'login_autorefresh')

		# User interface options
		self.ui = dict()
		self.ui['tray_onclose'] = self.getboolean('ui', 'tray_onclose')
		self.ui['tray_onstartup'] = self.getboolean('ui', 'tray_onstartup')


	def write_file(self):
		"""
		Write instance properties to configuration file.
		"""

		self.write(ac_config_path)

		self.set('mal', 'username', self.mal['username'])
		self.set('mal', 'password', self.mal['password'])
		self.set('mal', 'autologin', self.mal['autologin'])
		self.set('mal', 'login_autorefresh', self.mal['login_autorefresh'])
		
		self.set('ui', 'tray_onclose', self.ui['tray_onclose'])
		self.set('ui', 'tray_onstartup', self.ui['tray_onstartup'])

