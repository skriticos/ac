# =========================================================================== #
# Name:    cmdoptions.py
# Purpose: Contains command line option parsing logic.
#
# Copyright (c) 2009 Sebastian Bartos
#
# License: GPL v3, see COPYING file for details
# =========================================================================== #

import optparse, sys, globs

class AcOptParse(optparse.OptionParser):
	""" AniChou option parser class 

	Run application with -h flag to get an overview of options.
	"""

	def __init__(self, argv, version='%prog ' + globs.ac_version):
		""" Initialize option parser """

		optparse.OptionParser.__init__(self, version=version)

		# Define availible options
		self.add_option('-c', '--no-gui',
				action='store_false', dest='gui', default=True, 
				help='dissable GUI on startup')
		self.add_option('-t', '--tracker',
				action='store_true', dest='tracker', default=False,
				help='enable play-tracker on startup')

		# Parse input options
		self.parse_args(argv)

