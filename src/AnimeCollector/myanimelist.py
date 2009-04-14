
# Copyright (c) 2008 Gareth Latty
# Copyright (c) 2009 Sebastian Bartos
# See COPYING for details

from cookielib import LWPCookieJar
from datetime import date
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
# ToDo: make sync_mal a class and add data storage/loading to it


# setup cookie handler
cookiejar = LWPCookieJar()
opener = build_opener(HTTPCookieProcessor(cookiejar))
install_opener(opener)

# set connection paramaters
setdefaulttimeout(60)


def sync_mal(username, password, ac_local_anime_dict={}):
	""" MyAnimeList fetch and syncronization function interface.

	This is the module interface function to performe fetching and
	syncronization with the MyAnimeList server. If the ac_local_anime_dict
	argument is obmitted, it just performs a fetch and returns the remote
	database. If the ac_local_anime_dict argument dictionary is passed, it
	also checks for differences and pushes local updates.

	USAGE
	Only fetch list: fetched_list = sync_mal('user', 'passwd')
	Sync with local list:
		(synced, updates, deletes) = sync_mal('user', 'passwd', local_list)

	INPUT
	username -- username for server authentication and list fetching
	password -- password for server authentication
	ac_local_anime_dict -- local anime dictionary that is used for server
		syncronization

	OUTPUT
	False -- on login failure (wrong credentials)
	ac_remote_anime_dict -- if only fetching is performed. This contains the
		remote anime data.
	(synced_anime_dict, remote_updates, deleted_entry_keys) -- if full sync is
		performed. synced_anime_dict is the syncronized version of the local
		and remote anime directories. remote_updates are the anime datasets
		that were changed on the server. deleted_entry_keys are the keys of the
		deleted datasets on the	server
	"""

	if _login(username, password):
		ac_remote_anime_dict = _fetch_list(username)
		if ac_local_anime_dict:
			(remote_updates, local_updates, deleted_entry_keys) = \
				_filter_sync_changes(ac_remote_anime_dict, ac_local_anime_dict)
			_push_list(local_updates)
			# update local anime list with changes
			for key in deleted_entry_keys:
				del ac_local_anime_dict[deleted_entry_keys]
			synced_anime_dict = ac_local_anime_dict
			for key, value in remote_updates.items():
				synced_anime_dict[key] = value
			# complete sync cycle done
			return (synced_anime_dict, remote_updates, deleted_entry_keys)
		# fetching only
		return ac_remote_anime_dict
	else:
		# login failed
		return False


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
	if login_response.count('<div class="goodresult">'):
		return True
	else:
		return False


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
				if node.nodeName == u'my_last_updated':
					try:
						ac_node[node.nodeName] = \
							date.fromtimestamp(node.firstChild.nodeValue)
					except:
						print 'timestamp conversion failed, should not happen'
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
	new_entry_keys = \
		filter(lambda x:x not in remote_keys, local_keys)
	deleted_entry_keys = \
		filter(lambda x:x not in local_keys, remote_keys)
	for key in new_entry_keys:
		remote_updates[key] = ac_remote_anime_dict[key]

	# search in both dictionaries for differing update keys and append to the
	# other's updates depending on which key is newer
	common_keys = filter(lambda x:x in local_keys, remote_keys)
	for key in common_keys:
		if ac_remote_anime_dict[key['my_last_updated']] > \
				ac_local_anime_dict[key['my_last_updated']]:
			remote_updates[key] = ac_remote_anime_dict[key]
		elif ac_remote_anime_dict[key['my_last_updated']] < \
				ac_local_anime_dict[key['my_last_updated']]:
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




#
# """
# 	This is a myanimelist data source module for animecollector.
# """
#
# import Queue
# from twisted.web import client
# from twisted.internet import reactor
# from xml.dom import minidom
# import time
# from datetime import date
# import urllib
#
# class data_source:
#
# 	data = {}
# 	dataList = []  # All of the data and the types of data provided by this source.
# 	status = Queue.Queue()  # Current status.
# 	identified = False  # True if logged in, False if not.
#
# 	_username = None
# 	_password = None
# 	_cookies = None
#
# 	def __init__(self):
# 		""" Initialises all of the data for this source. """
#
# 		self.dataList = [
# 			("series_animedb_id", int),
# 			("series_title", unicode),
# 			("series_synonyms", unicode),
# 			("series_type", int),
# 			("series_episodes", int),
# 			("series_status", int),
# 			("series_start", date),
# 			("series_end", date),
# 			("series_image", str),
# 			("my_id", int),
# 			("my_watched_episodes", int),
# 			("my_start_date", date),
# 			("my_finish_date", date),
# 			("my_score", int),
# 			("my_status", int),
# 			("my_rewatching", int),
# 			("my_rewatching_ep", int),
# 			]
#
# 	def identify(self, username=None, password=None):
# 		""" Authenticates with the mal server. """
#
# 		# move this stuff to the constructor
# 		if username:
# 			self._username = username
# 		if password:
# 			self._password = password
#
# 		# move this to the constant section
# 		uri = "http://myanimelist.net/login.php"
#
# 		logininfo = urllib.urlencode({'username': self._username,
# 				'password': self._password, 'cookie': 1, 'sublogin': "Login"})
#
# 		request = client.HTTPClientFactory(uri, method="POST", postdata=
# 				logininfo, agent="animecollector", cookies=self._cookies,
# 				headers={'Content-Type': 'application/x-www-form-urlencoded'})
# 		(scheme, host, port, path) = client._parse(uri)
#
# 		reactor.connectTCP(host, port, request)
# 		# request.deferred.addCallback(self._deffer_identify, request)
# 		# request.deferred.addErrback(self._deffer_identify, None)
#
# 		if request.count('<div class="goodresult">'):
# 			self._cookies = data.cookies
# 			self.identified = True
# 		else:
# 			self.identified = False
# 		self.status.put((data, success, otherdata))
#
# 		# XXX: this thing must get a return value telling if the login was
# 		#	  successfull
# 		# Note: reseach how well this deferred thing works togeher with gtk
# 		# callbacks. Do some tracing and clean the module.
#
# 	def _deffer_identify(self, request, data):
# 		""" Checks, if the authentication with the mal server was successfull.
# 		(in a deffered way over a few sideways.)
# 		"""
#
# 		if data:
# 			if request.count('<div class="goodresult">'):
# 				self._cookies = data.cookies
# 				self.identified = True
# 			else:
# 				self.identified = False
# 		else:
# 			self.identified = False
# 		self._add_to_queue("identify", self.identified)
#
# 	def unidentify(self):
# 		self._cookies = None
#
# 	def update(self):
# 		""" Updates all of the data from the source into this class. """
#
# 		if self._username:
# 			uri = \
# 				"http://myanimelist.net/malappinfo.php?status=all&u=" + str(self._username)
# 			deffer = self._request(uri, method="GET")
# 			deffer.addBoth(self._deffer_update)
# 		else:
# 			self._add_to_queue("update", False)
#
# 	def commit(self, ident, edits, olddata, data):
# 		""" Commits edits made to the data to the site. """
#
# 		''' ident ('my_animedb_id') (Int), edits ([ ( name, value ) ]) (List) '''
#
# 		if not self.identified:
# 			self._add_to_queue("commit", False)
# 			return 0
#
# 		anime = olddata[ident]
# 		last_watched_eps = anime["episodes_watched"]
# 		last_status = anime["watching_status"]
#
# 		anime = data[ident]
#
# 		postdat = urllib.urlencode({
# 			'series_id': anime["mal_my_id"],
# 			'anime_db_series_id': anime["mal_id"],
# 			"series_title": anime["mal_id"],
# 			'aeps': anime["episodes_total"],
# 			'astatus': anime["airing_status"],
# 			'close_on_update': 'true',
# 			'status': anime["watching_status"],
# 			'rewatch_ep': anime["rewatching_episode"],
# 			'last_status': last_status,
# 			'completed_eps': anime["episodes_watched"],
# 			'last_completed_eps': last_watched_eps,
# 			"score": anime["score"],
# 			'startMonth': self._parse_date(anime["start_airing"],
# 					"month"),
# 			'startDay': self._parse_date(anime["start_airing"], "day"),
# 			'startYeah': self._parse_date(anime["start_airing"], "year"),
# 			'submitIt': 2,
# 			})
# 		uri = \
# 			"http://myanimelist.net/panel.php?keepThis=true&go=edit&id=" + \
# 			str(anime["mal_my_id"]) + "&hidenav=true"
# 		headers = {'Content-Type': 'application/x-www-form-urlencoded'}
# 		data = self._request(uri, method="POST", postdata=postdat,
# 							 headers=headers)
# 		data.addBoth(self._deffer_commit)
#
# 	def return_as_dic(self):
# 		return self.data
#
# 	def _parse_date(self, thedate, back):
# 		date = self._sanitise_date(thedate)
# 		if date:
# 			if back is "month":
# 				return date.month
# 			elif back is "year":
# 				return date.year
# 			elif back is "day":
# 				return date.day
# 			else:
# 				raise ValueError
# 		else:
# 			return 0
#
# 	def _sanitise_date(self, thedate):
# 		if type(thedate) is date:
# 			if thedate:
# 				return thedate
# 			else:
# 				return None
# 		if type(thedate) is str:
# 			if not thedate == "0000-00-00":
# 				year = thedate.split("-")[0]
# 				month = thedate.split("-")[1]
# 				day = thedate.split("-")[2]
# 				if not year == "0000":
# 					if not month == "00":
# 						if not day == "00":
# 							return date.fromtimestamp(time.mktime(time.strptime(thedate,
# 																	"%Y-%m-%d")))
# 						else:
# 							return None
# 					else:
# 						return None
# 				else:
# 					return None
# 			else:
# 				return None
#
# 	def _request(self, uri, method="POST", postdata=None, headers=None):
# 		return client.getPage(uri, method=method, cookies=self._cookies,
# 							  postdata=postdata, agent="animecollector",
# 							  headers=headers)
#
# 	def _deffer_update(self, data):
# 		try:
# 			raw = minidom.parseString(data)
# 		except:
# 			self._add_to_queue("update", False)
# 			return 0
# 		self._parse_update(raw)
#
# 	def _deffer_commit(self, data):
# 		if data.count('<div class="goodresult">'):
# 			self._add_to_queue("commit", True)
# 		else:
# 			self._add_to_queue("commit", False)
#
# 	def _parse_update(self, raw):
# 		if raw:
# 			for anime in raw.getElementsByTagName("anime"):
# 				this = {}
# 				for (name, dtype) in self.dataList:
# 					this[name] = self._get_from_xml(anime, (name, dtype))
# 				(self.data)[self._get_from_xml(anime, (self.dataList)[0])] = \
# 					this
# 			self._add_to_queue("update", True)
# 		else:
# 			self._add_to_queue("update", False)
#
# 	def _get_from_xml(self, tree, (node, dtype)):
# 		endnode = tree.getElementsByTagName(node)
# 		if endnode:
# 			if endnode[0]:
# 				if endnode[0].firstChild:
# 					if endnode[0].firstChild.nodeValue:
# 						if dtype is int:
# 							return int(endnode[0].firstChild.nodeValue)
# 						elif dtype is date:
# 							retdate = self._sanitise_date(endnode[0].firstChild.nodeValue)
# 							if retdate:
# 								return retdate
# 							else:
# 								return None
# 						elif dtype is str:
# 							return str(endnode[0].firstChild.nodeValue)
# 						elif dtype is unicode:
# 							return unicode(endnode[0].firstChild.nodeValue)
# 					else:
# 						return None
# 				else:
# 					return None
# 			else:
# 				return None
# 		else:
# 			return None
#
# 	def _add_to_queue(self, data, success, otherdata=None):
# 		# XXX: seems to magically signal that the login was successfull.
# 		self.status.put((data, success, otherdata))
#
