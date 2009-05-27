# =========================================================================== #
# Name:    players.py
# Purpose: detect played files given a set of players and serch paths
#
# Copyright (c) 2009 Sebastian Bartos
#
# Attribution: 'Wile' (nick) contributed to the code for usage with the 
#                            project license
#
# License: GPL v3, see COPYING file for details
# =========================================================================== #

import os, platform, subprocess

class OpenFileListLinMac(object):
	""" Interface to the Un*x 'lsof' command.
	
	Public attribute sets is a list of dictionaries with one-character keys
	and string values. Only if the key is 'f' the value will be a similar
	list of dict, but not nested further.
	
	Some interesting keys:
	
	c	process command name
	n	file name
	p	pid
	s	file size
	t	file type
	u	process user id

	The closest equivalent on Windows (for future porting) seems to be Handle
	http://technet.microsoft.com/en-us/sysinternals/bb896655.aspx
	but that requires administrator privileges to run, does not ship with
	Windows, and has a license explicitly forbidding distribution.
	"""
	
	def __init__(self):
		"""Constructor.
		
		Currently fills sets using options optimized for speed.
		"""

		self.sets = []

		# Current user.
		mine = '-u' + str(os.getuid())

		for line in self.lsof('-lnP', '-F0ncupf', '-M', '-S2', mine):

			# Identifier.
			first = line[0][0]
			whole = dict(line)

			if first == 'p':
				proc = whole
				self.sets.append(proc)
			elif first == 'f':
				proc.setdefault('f', []).append(whole)

	def by_process(self, *filters):
		"""Return file lists for specified processes.
		
		PARAMETERS
		==========
		filters --  tuple of strings. Either command names (mplayer), binary
		            paths (/bin/cp) or ids ('123').
		
		This makes it impossible to select processes with a numeric name!
		
		Returns a list with as many items as filters, and in the same order,
		consisting of lists of unique file names.
		"""
		
		result = []

		for test in filters:

			files = []

			# Several processes may match. We unify their open files.
			for proc in self.sets:

				if test.isdigit():
					take = test == proc['p']
				elif '/' in test:
					take = os.path.basename(test) == os.path.basename(proc['c'])
				else:
					take = test == proc['c']

				if take:
					for f in proc['f']:
						# Several instances of one program may have the same
						# file open. We list it only once.
						# Keep the pid then fd sorting in the result!
						try:
							old = files.index(f['n'])
							files.remove(old)
						except ValueError:
							pass
						files.append(f['n'])

			result.append(files)

		return result

	@staticmethod
	def lsof(*options):
		"""Call lsof with the specified arguments and return a list of tuples.
		
		The arguments must contain -F0, or parsing will break!
		
		From the man page:
		
		-l	don't convert uid to login name
		-n	don't convert network numbers to hose names
		-P	don't convert port numbers to port names
		-M	disable reporting of portmapper registrations
		-S	time-out in seconds for kernel functions, minimum two
		-u	only list processes with this uid
		-F	select which fields to output

		lsof not only lists explicitly opened local file descriptors but also
		dynamically linked libraries!
		"""

		command_line = ('lsof',) + options
		
		ipc = subprocess.Popen(command_line, stdout = subprocess.PIPE)
		out = ipc.communicate()[0]
		# communicate() searches PATH

		if ipc.returncode < 0:
			raise EnvironmentError('lsof failed')
			
		sets = []

		for line in out.splitlines():
			current = []
			for field in line.split("\0"):
				# Last line is empty.
				if field:
					current.append((field[0], field[1:]))
			sets.append(current)
				
		return sets

## A list if lowercase filename extensions without the leading dot. If it is 
## empty, all types are accepted.
wanted_extensions = []

def filter_paths(prefixes, files):
	"""Filter list of files.

	PARAMETERS
	==========
	prefixes --  a list of paths that need not end in slash. If it is empty,
		         all prefixes are allowed.

	Returns the items in files that match.
	
	Currently checks if prefix and files exist in the file system. Should
	probably be done by whoever calls us.
	"""
	
	result = []

	for f in files:
		for p in prefixes:
			if f[:len(p)] == p and os.path.isdir(p):
				found_p = True
				break
		else:
			found_p = not prefixes

		root, e = os.path.splitext(f)
		if e.lstrip('.').lower() in wanted_extensions:
			found_e = True
		else:
			found_e = not wanted_extensions

		if found_p and found_e and os.path.isfile(f):
			result.append(f)
			
	return result

def get_playing_linmac(players, search_dirs):
	""" This implementation relies on the OpenFileListLinMac interface. """

	played_files = {}

	# Hard-code one here!
	fs = OpenFileListLinMac()

	# Retrieve files by player.
	lists = fs.by_process(*players)

	for index, files in enumerate(lists):
		for f in filter_paths(search_dirs, files):
			played_files[f] = players[index]
			
	return played_files

# Check if playtracker supports the current platoform, and call the appropriate
# tracker or, print a note if it does not.
this_platform = platform.system()
if this_platform == 'Linux' or this_platform == 'Darwin':
	get_playing = globals()['get_playing_linmac']
else:
	print 'Playtracking on your platform %s is currently not supported, sorry.'\
		% this_platform

