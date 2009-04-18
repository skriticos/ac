
# Copyright (c) 2008 Gareth Latty
# Copyright (c) 2009 Sebastian Bartos
# See COPYING for details

from cookielib import LWPCookieJar
import cPickle
from datetime import date, datetime
from os import path
from urllib import urlencode
from urllib2 import \
		Request, urlopen, \
		build_opener, install_opener, \
		HTTPCookieProcessor, URLError
from socket import setdefaulttimeout
from xml.dom.minidom import parseString

from data import \
	mal_data_schema


# ToDo: debug _filter_sync_changes and _push_update


class anime_data(object):
	"""
	Anime data module. Reads and writes local anime data to disk, fetches and
	syncs with MyanimeList server.

	username: login username
	password: login password
	db_path: path to database
	db: local anime database that is a nested dict and has ASCII-fied series
		titles as keys and and fields form mal_data_schema as dict data.
	"""

	def __init__(self, username='', password='', initsync=False):
		"""
		Setup credentials, read local data and setup network connection
		environment. Optionally sync with MAL on startup.
		"""

		self.db_path = path.join(path.expanduser("~"), ".animecollector.dat")

		self.username = username
		self.password = password

		# setup cookie handler
		opener = build_opener(HTTPCookieProcessor(LWPCookieJar()))
		install_opener(opener)

		# set connection paramaters
		setdefaulttimeout(60)

		# initialize local data (read file if existent)
		self.db = {}
		if path.isfile(self.db_path):
			db_handle = open(self.db_path, 'rb')
			self.db = cPickle.load(db_handle)
			db_handle.close()

		if initsync:
			self.sync()

	def fetch(self):
		"""
		Only fetch anime data from MyAnimeList server (overwrites local data,
		if existent). Useful for initializing and resetting local database.

		Returns a copy of the fetched database on success, None on failure.
		"""
		if _login(self.username, self.password):
			self.db = _fetch_list(self.username)
			db_handle = open(self.db_path, 'wb')
			cPickle.dump(self.db, db_handle)
			db_handle.close()
			return self.db

	def sync(self):
		"""
		Syncronize local anime database with the MyAnimeList server.
		(fetch -> compare -> push -> update local)

		Returs nested dict of remote updates with ASCII-fied series titles as
		keys and a list of keys that got deleted on the MyAnimeList server.
		"""
		if _login(self.username, self.password):
			remote_db = _fetch_list(self.username)
			(remote_updates, local_updates, deleted_entry_keys) = \
				_filter_sync_changes(remote_db, self.db)
			_push_list(local_updates)

			# update local anime list with changes
			for key in deleted_entry_keys:
				del self.db[deleted_entry_keys]
			for key, value in remote_updates.items():
				self.db[key] = value
			db_handle = open(self.db_path, 'wb')
			cPickle.dump(self.db, db_handle)
			db_handle.close()
			return (remote_updates, deleted_entry_keys)


def _login(username, password):
	"""
	Log in to MyAnimeList server.
	Returns: True on success, False on failure
	"""

	# prepare login data
	login_base_url = 'http://myanimelist.net/login.php'

	headers = {
		'User-Agent': 'animecollector',
		'Content-Type': 'application/x-www-form-urlencoded'}

	login_data = urlencode({
		'username': username,
		'password': password,
		'cookie': 1,
		'sublogin': 'Login'})

	# phrase login request (to perform a POST request)
	login_request = Request(login_base_url, login_data, headers)

	# try to connect and authenticate with MyAnimeList server
	try:
		login_response = urlopen(login_request).read()
	except URLError, e:
		if hasattr(e, 'reason'):
			print 'We failed to reach a server.'
			print 'Reason: ', e.reason
		elif hasattr(e, 'code'):
			print 'The server couldn\'t fulfill the request.'
			print 'Error code: ', e.code
		return False

	# check if login was successful
	if login_response.count('<div class="badresult">'):
		return False
	else:
		return True


def _fetch_list(username):
	"""
	Retrive anime data from MyAnimeList server.
	"""

	fetch_base_url = 'http://myanimelist.net/malappinfo.php'
	fetch_request_data = urlencode({
		'status': 'all',
		'u': username})
	fetch_url = fetch_base_url + '?' + fetch_request_data

	# read the server xml file and do preliminary spacer sanitation for parsing
	fetch_response = urlopen(fetch_url).read()
	fetch_response = fetch_response.replace('\n', '').replace('\t', '')

	# phrase data and extract anime entry nodes
	xmldata = parseString(fetch_response)
	anime_nodes = xmldata.getElementsByTagName('anime')

	# walk through all the anime nodes and convert the data to a python
	# dictionary
	ac_remote_anime_dict = dict()
	for anime in anime_nodes:
		ac_node = dict()
		for node in anime.childNodes:
			# tags and empty nodes are excluded for the time being
			if not node.childNodes or node.nodeName == u'my_tags':
				node.unlink()
			else:
				# process my_last_updated unix timestamp
				if mal_data_schema[node.nodeName] is datetime:
					ac_node[node.nodeName] = \
						datetime.fromtimestamp(int(node.firstChild.nodeValue))
				# process integer slots
				elif mal_data_schema[node.nodeName] is int:
					ac_node[node.nodeName] = int(node.firstChild.nodeValue)
				# proces date slots
				elif mal_data_schema[node.nodeName] is date:
					if node.firstChild.nodeValue != '0000-00-00':
						(y,m,d) = node.firstChild.nodeValue.split('-')
						(y,m,d) = int(y), int(m), int(d)
						if y and m and d:
							ac_node[node.nodeName] = date(y,m,d)
				# process string slots
				else:
					ac_node[node.nodeName] = node.firstChild.nodeValue

		# series titles are used as anime identifiers
		# the keys for the resulting dictionary are encoded to ASCII, so they
		# can be simply put into shelves
		key = ac_node['series_title'].encode('utf-8')

		# add node entry to the resulting nodelist
		ac_remote_anime_dict[key] = ac_node

	# the resulting dict is like this:
	# {<ASCII-fied key from title>: {<mal_data_schema-fields>: <values>}, ...}
	return ac_remote_anime_dict


def _filter_sync_changes(ac_remote_anime_dict, ac_local_anime_dict):
	"""
	Compares the anime entry my_last_updated in both parameters and returns two
	dictionaries of changed values of both parameters.

	The one for the local dictionary can be used to push changes to the mal
	server while the other can be used to update the local display and database.

	Returns:
		remote_updates: changes that are more up to date on the server
		local_updates: changes that are more up to date locally
		deleted_enry_keys: keys that are in the local database, but not in the
						   remote list.
	"""
	remote_updates = dict()
	local_updates = dict()

	# search for entirely new enries and deleted entries
	remote_keys = ac_remote_anime_dict.keys()
	local_keys = ac_local_anime_dict.keys()
	
	deleted_entry_keys = \
		filter(lambda x:x not in remote_keys, local_keys)
	
	new_entry_keys = \
		filter(lambda x:x not in local_keys, remote_keys)
	for key in new_entry_keys:
		remote_updates[key] = ac_remote_anime_dict[key]

	# search in both dictionaries for differing update keys and append to the
	# other's updates depending on which key is newer
	common_keys = filter(lambda x:x in local_keys, remote_keys)

	for key in common_keys:
		
		remote_timestamp = ac_remote_anime_dict[key]['my_last_updated']
		local_timestamp = ac_local_anime_dict[key]['my_last_updated']

		if remote_timestamp > local_timestamp:
			remote_updates[key] = ac_remote_anime_dict[key]
		elif remote_timestamp < local_timestamp:
			local_updates[key] = ac_local_anime_dict[key]

	return (remote_updates, local_updates, deleted_entry_keys)


def _push_list(local_updates):
	"""
	Updates every entry in the local updates dictionary to the mal server.
	Should be called after the local updates are determined with the
	filter_sync_changes function.

	Returns:
		True on success, False on failure
	"""

	headers = {
		'User-Agent': 'animecollector',
		'Content-Type': 'application/x-www-form-urlencoded'}

	for anime in local_updates.values():

		# construct push request for entry update
		postdata = urlencode({
			'series_id': anime['mal_my_id'],
			'anime_db_series_id': anime['mal_id'],
			'close_on_update': 'true',
			'status': anime['watching_status'],
			'completed_eps': anime['episodes_watched'],
			'score': anime['score'],
			'submitIt': 2 })
		push_base_url = \
			'http://myanimelist.net/panel.php?keepThis=true&go=edit&id=' + \
			str(anime['mal_my_id']) + '&hidenav=true'

		push_request = Request(push_base_url, postdata, headers)

		# push update request
		try:
			urlopen(push_request)
		except URLError, e:
			if hasattr(e, 'reason'):
				print 'We failed to reach a server.'
				print 'Reason: ', e.reason
			elif hasattr(e, 'code'):
				print 'The server couldn\'t fulfill the request.'
				print 'Error code: ', e.code
			return False
	return True
