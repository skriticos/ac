import os, subprocess

def get_playing(players, search_dirs):
	""" Search for currently played files

	Parameters:
		players: 		list of players to search for
		search_dirs: 	list of directories to be considered for opened files

	Returns:
		Dictionary of played files with players.
		Example: {'/home/foo': 'mplayer', '/home/bar': 'totem'}

	Example:
		files = get_playing(['mplayer', 'totem'], ['/home/foo', '/home/bar'])

	Notes:
		This module relies on the Linux/*nix command line utitities: ps and ls.
		It uses procfs to search for opened file descriptors.
	"""

	played_files = {}

	for player in players:

		# Search for player process
		ps_cmd = ['ps', 'h', '-C', player, '-o', 'pid']
		rp1 = subprocess.Popen(ps_cmd, stdout=subprocess.PIPE)
		raw_play_pids = rp1.stdout.readlines()
		rp1.wait()
		playing_pids = list()
		for pid in raw_play_pids:
			playing_pids.append(pid.strip())

		# Search for opened media files
		if playing_pids:
			for pid in playing_pids:
				ls_cmd = ['ls', '-l', '/proc/'+pid+'/fd']
				rp2 = subprocess.Popen(ls_cmd, stdout=subprocess.PIPE)
				raw_file_listing = rp2.stdout.readlines()
				rp2.wait()
				file_listing = list()
				for line in raw_file_listing:
					file_listing.append(line.strip())
				for file in file_listing:
					for dir in search_dirs:
						if not isinstance(dir, unicode): continue
						file = file.split(' -> ',1)[-1].rstrip()
						if file[:len(dir)] == dir and \
								os.path.isfile(file) and \
								os.path.isdir(file[:len(dir)+1]):
							played_files[file] = player
	return played_files

