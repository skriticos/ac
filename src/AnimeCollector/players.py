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

import os, lsof, platform

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
	""" This implementation relies on the lsof.OpenFileList interface. """

	played_files = {}

	# Hard-code one here!
	fs = lsof.OpenFileList()

	# Retrieve files by player.
	lists = fs.by_process(*players)

	for index, files in enumerate(lists):
		for f in filter_paths(search_dirs, files):
			played_files[f] = players[index]
			
	return played_files

# Check if playtracker supports the current platoform, and call the appropriate
# tracker or, print a note if it does not.
this_platform = platform.system()
if this_platform == 'Linux' or this_platform == 'darwin':
	get_playing = globals()['get_playing_linmac']
else:
	print 'Playtracking on your platform %s is currently not supported, sorry.'\
		% this_platform

