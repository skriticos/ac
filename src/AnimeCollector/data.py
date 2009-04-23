
# Copyright (c) 2008 Gareth Latty
# Copyright (c) 2009 Sebastian Bartos
# See COPYING for details

""" data.py -- core data schemas

This module contains the core data schemas used in the applicaiton and in the
communication with the server.
"""

from datetime import date, datetime

## Schema of the xml data the MyAnimeList server sends
mal_data_schema = {
	'series_animedb_id': int,
	'series_title': unicode,
	'series_synonyms': unicode,
	'series_type': int,
	'series_episodes': int,
	'series_status': int,
	'series_start': date,
	'series_end': date,
	'series_image': unicode,
	'my_id': int,
	'my_watched_episodes': int,   # push argument
	'my_start_date': date,
	'my_finish_date': date,
	'my_score': int,   # push argument
	'my_status': int,   # push argument
	'my_rewatching': int,
	'my_rewatching_ep': int,
	'my_last_updated': datetime}   # sync variable

## Here is a sample of the data representation the myanimelist module produces,
## and which is used in the application and is also sent to the persistent data
## file. This example data has 2 entries, one with a unicode character in it to
## demonstarte key encoding. Note: some date keys may be missing in enries, for
## instance the start and end keys if they are 0000-00-00 on the server.
## Note2: if additional keys are added in the XML, they will appear as unicode
## strings in the datastructures.
##
## You can access this data with an anime_data instance db property:
##    adata.db['Macross Frontier']   # gives a dict with all the properites of
##                                     the Macross Frontier anime entry
##    adata.db['Macross Frontier']['my_status']   # gives the current status of
##                                                  the above (2 in this case)
##
## { 'Lucky \xe2\x98\x86 Star': {u'my_id': 12345,
##                             u'my_last_updated': 
##                                   datetime.datetime(2009, 3, 26...),
##                             u'my_rewatching': 0,
##                             u'my_rewatching_ep': 0,
##                             u'my_score': 0,
##                             u'my_start_date': datetime.date(2009, 3, 25),
##                             u'my_status': 1,
##                             u'my_watched_episodes': 8,
##                             u'series_animedb_id': 1887,
##                             u'series_end': datetime.date(2007, 9, 17),
##                             u'series_episodes': 24,
##                             u'series_image':
##                        u'http://cdn.myanimelist.net/images/anime/2/4781.jpg',
##                             u'series_start': datetime.date(2007, 4, 9),
##                             u'series_status': 2,
##                             u'series_synonyms':
##                                 u'Lucky Star; Raki \u2606 Suta',
##                             u'series_title': u'Lucky \u2606 Star',
##                             u'series_type': 1},
## 'Macross Frontier': {u'my_id': 12345,
##                      u'my_last_updated': datetime.datetime(2008, 11, 22...),
##                      u'my_rewatching': 0,
##                      u'my_rewatching_ep': 0,
##                      u'my_score': 9,
##                      u'my_status': 2,
##                      u'my_watched_episodes': 25,
##                      u'series_animedb_id': 3572,
##                      u'series_end': datetime.date(2008, 9, 25),
##                      u'series_episodes': 25,
##                      u'series_image':
##                  u'http://cdn.myanimelist.net/images/anime/10/10549.jpg',
##                      u'series_start': datetime.date(2008, 4, 3),
##                      u'series_status': 2,
##                      u'series_synonyms': u'Macross F',
##                      u'series_title': u'Macross Frontier',
##                      u'series_type': 1}}


## These are the status code mappings the mal server is sending in the XML file
( WATCHING, COMPLETED, ONHOLD, DROPPED, UNKNOWN, PLANTOWATCH ) = range(1, 7)

# Here is the reverse mapping of the above for widget adressing and similar
STATUS = {	
	1: 'watching',
	2: 'completed',
	3: 'onhold',
	4: 'dropped',
	6: 'plantowatch' }

# This is the same as above but with capitals and spaces for display purposes
STATUSB = {
	1: 'Watching',
	2: 'Completed',
	3: 'On Hold',
	4: 'Dropped',
	6: 'Plan To Watch' }

STATUS_REV = {
	'Watching': 1,
	'Completed': 2,
	'On Hold': 3,
	'Dropped': 4,
	'Plan To Watch': 6 }
