#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
	This is a myanimelist data source module for animecollector.
"""

import Queue
from twisted.web import client
from twisted.internet import reactor
from xml.dom import minidom
import time
from datetime import date
import urllib

class data_source:

	data = {}
	dataList = []  # All of the data and the types of data provided by this source.
	status = Queue.Queue()  # Current status.
	identified = False  # True if logged in, False if not.

	_username = None
	_password = None
	_cookies = None

	def __init__(self):
		""" Initialises all of the data for this source. """

		self.dataList = [
			("series_animedb_id", int),
			("series_title", unicode),
			("series_synonyms", unicode),
			("series_type", int),
			("series_episodes", int),
			("series_status", int),
			("series_start", date),
			("series_end", date),
			("series_image", str),
			("my_id", int),
			("my_watched_episodes", int),
			("my_start_date", date),
			("my_finish_date", date),
			("my_score", int),
			("my_status", int),
			("my_rewatching", int),
			("my_rewatching_ep", int),
			]

	def identify(self, username=None, password=None):
		""" Authenticates with the mal server. """

		# move this stuff to the constructor
		if username:
			self._username = username
		if password:
			self._password = password

		# move this to the constant section
		uri = "http://myanimelist.net/login.php"

		logininfo = urllib.urlencode({'username': self._username,
				'password': self._password, 'cookie': 1, 'sublogin': "Login"})

		request = client.HTTPClientFactory(uri, method="POST", postdata=
				logininfo, agent="animecollector", cookies=self._cookies,
				headers={'Content-Type': 'application/x-www-form-urlencoded'})
		(scheme, host, port, path) = client._parse(uri)

		reactor.connectTCP(host, port, request)
		request.deferred.addCallback(self._deffer_identify, request)
		request.deferred.addErrback(self._deffer_identify, None)

	def unidentify(self):
		self._cookies = None

	def update(self):
		""" Updates all of the data from the source into this class. """

		if self._username:
			uri = \
				"http://myanimelist.net/malappinfo.php?status=all&u=" + str(self._username)
			deffer = self._request(uri, method="GET")
			deffer.addBoth(self._deffer_update)
		else:
			self._add_to_queue("update", False)

	def commit(self, ident, edits, olddata, data):
		""" Commits edits made to the data to the site. """

		''' ident ('my_animedb_id') (Int), edits ([ ( name, value ) ]) (List) '''

		if not self.identified:
			self._add_to_queue("commit", False)
			return 0

		anime = olddata[ident]
		last_watched_eps = anime["episodes_watched"]
		last_status = anime["watching_status"]

		anime = data[ident]

		postdat = urllib.urlencode({
			'series_id': anime["mal_my_id"],
			'anime_db_series_id': anime["mal_id"],
			"series_title": anime["mal_id"],
			'aeps': anime["episodes_total"],
			'astatus': anime["airing_status"],
			'close_on_update': 'true',
			'status': anime["watching_status"],
			'rewatch_ep': anime["rewatching_episode"],
			'last_status': last_status,
			'completed_eps': anime["episodes_watched"],
			'last_completed_eps': last_watched_eps,
			"score": anime["score"],
			'startMonth': self._parse_date(anime["start_airing"],
					"month"),
			'startDay': self._parse_date(anime["start_airing"], "day"),
			'startYeah': self._parse_date(anime["start_airing"], "year"),
			'submitIt': 2,
			})
		uri = \
			"http://myanimelist.net/panel.php?keepThis=true&go=edit&id=" + \
			str(anime["mal_my_id"]) + "&hidenav=true"
		headers = {'Content-Type': 'application/x-www-form-urlencoded'}
		data = self._request(uri, method="POST", postdata=postdat,
							 headers=headers)
		data.addBoth(self._deffer_commit)

	def return_as_dic(self):
		return self.data

	def _parse_date(self, thedate, back):
		date = self._sanitise_date(thedate)
		if date:
			if back is "month":
				return date.month
			elif back is "year":
				return date.year
			elif back is "day":
				return date.day
			else:
				raise ValueError
		else:
			return 0

	def _sanitise_date(self, thedate):
		if type(thedate) is date:
			if thedate:
				return thedate
			else:
				return None
		if type(thedate) is str:
			if not thedate == "0000-00-00":
				year = thedate.split("-")[0]
				month = thedate.split("-")[1]
				day = thedate.split("-")[2]
				if not year == "0000":
					if not month == "00":
						if not day == "00":
							return date.fromtimestamp(time.mktime(time.strptime(thedate,
																	"%Y-%m-%d")))
						else:
							return None
					else:
						return None
				else:
					return None
			else:
				return None

	def _request(self, uri, method="POST", postdata=None, headers=None):
		return client.getPage(uri, method=method, cookies=self._cookies,
							  postdata=postdata, agent="animecollector",
							  headers=headers)

	def _deffer_update(self, data):
		try:
			raw = minidom.parseString(data)
		except:
			self._add_to_queue("update", False)
			return 0
		self._parse_update(raw)

	def _deffer_identify(self, request, data):
		""" Checks, if the authentication with the mal server was successfull. 
		"""

		if data:
			if request.count('<div class="goodresult">'):
				self._cookies = data.cookies
				self.identified = True
			else:
				self.identified = False
		else:
			self.identified = False
		self._add_to_queue("identify", self.identified)

	def _deffer_commit(self, data):
		if data.count('<div class="goodresult">'):
			self._add_to_queue("commit", True)
		else:
			self._add_to_queue("commit", False)

	def _parse_update(self, raw):
		if raw:
			for anime in raw.getElementsByTagName("anime"):
				this = {}
				for (name, dtype) in self.dataList:
					this[name] = self._get_from_xml(anime, (name, dtype))
				(self.data)[self._get_from_xml(anime, (self.dataList)[0])] = \
					this
			self._add_to_queue("update", True)
		else:
			self._add_to_queue("update", False)

	def _get_from_xml(self, tree, (node, dtype)):
		endnode = tree.getElementsByTagName(node)
		if endnode:
			if endnode[0]:
				if endnode[0].firstChild:
					if endnode[0].firstChild.nodeValue:
						if dtype is int:
							return int(endnode[0].firstChild.nodeValue)
						elif dtype is date:
							retdate = self._sanitise_date(endnode[0].firstChild.nodeValue)
							if retdate:
								return retdate
							else:
								return None
						elif dtype is str:
							return str(endnode[0].firstChild.nodeValue)
						elif dtype is unicode:
							return unicode(endnode[0].firstChild.nodeValue)
					else:
						return None
				else:
					return None
			else:
				return None
		else:
			return None

	def _add_to_queue(self, data, success, otherdata=None):
		self.status.put((data, success, otherdata))

