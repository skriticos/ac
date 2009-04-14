
# Copyright (c) 2008 Gareth Latty
# Copyright (c) 2009 Sebastian Bartos
# See COPYING for details

from datetime import date


# Schema of the xml data the MyAnimeList server sends
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
	'my_watched_episodes': int,
	'my_start_date': date,
	'my_finish_date': date,
	'my_score': int,
	'my_status': int,
	'my_rewatching': int,
	'my_rewatching_ep': int,
	'my_last_updated': int}


# These are the status code mappings the mal server is sending in the XML file
mal_anime_status_codes = [
	(1,	'Watching'),
	(2,	'Completed'),
	(3,	'On Hold'),
	(4,	'Unknown'), 			#4 appears to be unused - added in case it is.
	(5,	'Dropped'),
	(6,	'Plan To Watch')]


# from datetime import date
#
# STATUS = {
#     1	:	"Watching",
#     2	:	"Completed",
#     3	:	"On Hold",
#     4	:	"Unknown", 			#4 appears to be unused - added in case it is.
#     5	:	"Dropped",
#     6	:	"Plan To Watch",
# }
#
# # From status to their position in the combo box.
# STATUS_COMBO = {
#     1	:	0,
#     2	:	1,
#     3	:	2,
#     4	:	-1,
#     5	:	3,
#     6	:	4,
# }
#
# COMBO_STATUS = {
#     0	:	1,
#     1	:	2,
#     2	:	3,
#     -1	:	4,
#     3	:	5,
#     4	:	6,
# }
#
# # Status for series.
# SERIES_STATUS = {
#     1	:	"Airing",
#     2	:	"Aired",
#     3	:	"Not Aired",
# }
#
# # Types for series.
# SERIES_TYPE = {
#     1	:	"TV",
#     2	:	"OVA",
#     3	:	"Movie",
#     4	:	"Special",
#     5	:	"ONA",
# }
#
# MAL_DATALIST = [
#     ("series_animedb_id", int),
#     ("series_title", unicode),
#     ("series_synonyms", unicode),
#     ("series_type", int),
#     ("series_episodes", int),
#     ("series_status", int),
#     ("series_start", date),
#     ("series_end", date),
#     ("series_image", str),
#     ("my_id", int),
#     ("my_watched_episodes", int),
#     ("my_start_date", date),
#     ("my_finish_date", date),
#     ("my_score", int),
#     ("my_status", int),
#     ("my_rewatching", int),
#     ("my_rewatching_ep", int),
# ]
