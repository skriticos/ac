
# Copyright (c) 2008 Gareth Latty
# Copyright (c) 2009 Sebastian Bartos
# See COPYING for details

import ConfigParser, os
import globs

class ac_config(ConfigParser.ConfigParser):
	""" Config parser

	This one is really trivial.
	"""

	def __init__(self):
		""" Start up config parser """

		ConfigParser.ConfigParser.__init__(self)

		# Check if there is a config file already, cerate one if note
		if not os.path.isfile(globs.ac_config_path):
			self.add_section('mal')
			self.add_section('startup')
			self.add_section('search_dir')
			for p in ['username', 'password']:
				self.set('mal', p, '')
			for p in ['sync', 'tracker']:
				self.set('startup', p, 'False')
			self.set('search_dir', 'dir1', os.path.expanduser('~'))
			f = open(globs.ac_config_path, 'wb')
			self.write_file()
			f.close()
		else:
			# Read config file if availible
			self.read(globs.ac_config_path)

	def write_file(self):
		""" Write config file """

		f = open(globs.ac_config_path, 'wb')
		self.write(f)
		f.close()

