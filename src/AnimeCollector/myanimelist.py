
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


# =======================================================
# Global connection settings (because of inherited magic)
# =======================================================

# setup cookie handler
cookiejar = LWPCookieJar()
opener = build_opener(HTTPCookieProcessor(cookiejar))
install_opener(opener)

# set connection paramaters
setdefaulttimeout(60)


# ================
# Helper functions 
# ================

def login(username, password):
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


def fetch_list(username):
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
	ac_anime_dict = dict()
	for anime in anime_nodes:
		ac_node = dict()
		for node in anime.childNodes:
			# tags and empty nodes are excluded for the time being
			if not node.childNodes or node.nodeName == u'my_tags':
				node.unlink()
			else:
				# process integer slots
				if mal_data_schema[node.nodeName] is int:
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
		ac_anime_dict[key] = ac_node
	
	# the resulting dict is like this:
	# {<ASCII-fied key from title>: {<mal_data_schema-fields>: <values>}, ...}
	return ac_anime_dict


# ================================
# Interface functions (module api)
# ================================

def sync_mal(username, password, ac_local_anime_dict=None):
	"""
	Does a complete sync cycle.
	Takes the username, password and optionally the local anime data,
	logs in to the mal server, fetches mal data, diffs data, commits local
	changes and returns a syncronized dictionary.
	"""
	if login(username, password):
		ac_anime_dict = fetch_list(username)
		if ac_local_anime_dict:
			# TODO: add ac_anime_dict - ac_local_anime_dict diff and server 
			#       commit
			# TODO: add ac_anime_dict - ac_local_anime_dict data syncronization
			#       and return the sycronized dictionary
			pass
			return ac_local_anime_dict
		return ac_anime_dict
	else:
		return False


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
# 		#      successfull
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
