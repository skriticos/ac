
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

		self.ac_sections = ['mal', 'startup', 'search_dir']

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
			loaded_sections = self.sections()
			loaded_sections.sort()
			schema_sections = self.ac_sections
			schema_sections.sort()
			if loaded_sections != schema_sections:
				os.remove(globs.ac_config_path)
				print 'Invalid config found, resetting..'
				print 'Please start the application again.'
				os._exit(1)

	def write_file(self):
		""" Write config file """

		f = open(globs.ac_config_path, 'wb')
		self.write(f)
		f.close()

