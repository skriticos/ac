
# config.py - configuration defaults and phraser
#
# Contents
# --------
#
# DEFAULT_CONFIG
#		Empty configuration that is used to create a blank configuration file if
#		there is none.
#
# ac_config
#		Class that phrases the configuration file.


							 ### Import section ###

import os
from ConfigParser import ConfigParser


							   ### Constants ###

DEFAULT_CONFIG = """\
[mal]
username =
password =
autologin = False
login_autorefresh = False

[ui]
tray_onclose = True
tray_onstartup = False
startup_bars = list,edit

[search_dirs]   # Directories where played files are searched for
dir1 = /home
dir2 = /home/foo
"""

config_path = os.path.join(os.path.expanduser("~"), ".animecollector.cfg")


						   ### Class declarations ###

class ac_config(ConfigParser):
	""" Configuration phraser and data class.
	
	Properties
		mal = {'username': str, 'password': str, 'autologin': boolean}
		ui = {'tray_onclose': boolean, 'tray_onstartup': boolean,
			  'startup_bars': list }
	"""

	def __init__(self):
		""" Loads and reads the configuration file.  """

		ConfigParser.__init__(self)

		# Create default configuration if it is missing:
		if not os.path.isfile(config_path):
			x = open(config_path, 'w')
			x.write(DEFAULT_CONFIG)
			x.close()

		self.read_file()

	
	def read_file(self):
		""" Read instance properties from configuration file. """
		
		self.read(config_path)

		# myAnimeList login credentials and options
		self.mal = dict()
		self.mal['username'] = self.get('mal', 'username')
		self.mal['password'] = self.get('mal', 'password')
		self.mal['autologin'] = self.getboolean('mal', 'autologin')
		self.mal['autorefresh'] = self.getboolean('mal', 'login_autorefresh')

		# User interface options
		self.ui = dict()
		self.ui['tray_onclose'] = self.getboolean('ui', 'tray_onclose')
		self.ui['tray_onstartup'] = self.getboolean('ui', 'tray_onstartup')
		self.ui['startup_bars'] = self.get('ui', 'startup_bars').split(',')


	def write_file(self):
		""" Write instance properties to configuration file. """

		self.write(config_path)

		self.set('mal', 'username', self.mal['username'])
		self.set('mal', 'password', self.mal['password'])
		self.set('mal', 'autologin', self.mal['autologin'])
		self.set('mal', 'login_autorefresh', self.mal['login_autorefresh'])
		
		self.set('ui', 'tray_onclose', self.ui['tray_onclose'])
		self.set('ui', 'tray_onstartup', self.ui['tray_onstartup'])
		str_starup_bars = str()
		for x in self.ui['startup_bars']:
			str_starup_bars += x + ','
		self.set('ui', 'startup_bars', str_starup_bars.rstrip(','))




