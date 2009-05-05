
""" myanimelist module test file 

Please notify me if I accidentally upload it with login credentials so I change
them.

Notes: this test messes with your live list data at the end to accoplish sync
testing. Use at own risk. Read the description before you use it.

Usage
=====
First you have to EDIT THE USERNAME AND PASSWORD constant that come after the
description and all my lovely warnings. They must be valid myanimelist login
credentials for an account with at least 12 completed and 2 waching enries.

Then you will have to uncomment either stage 1-4 calling exclusive OR stage 5 
calling, as these bug each other. (see the very end of this file).

Then you simply RUN THIS SCRIPT.

You know that the test was successful if
1. The summary of the script sais so AND
2. 2 waching enries in your myanimelist get an inceremented wached episode value
   The summary will also tell you which entries you have to look for.

If you had a local data file already, then it will be renamed to
~/.anichou.dat.bak. You'll have to restore it manually.

Editoral note (you can skip this)
=================================
	I have my love/hate relationship with testcases, but this one is really
	mean, as it performs operations on my live data on the server I have no
	conrol over.
	Anyway, it should give you a good idea of how to work with the myanimelist
	moduel by example and give a nice utility if something breaks.
"""

# ============================================================== GPL v3 stuff ==
#
# Copyright (c) 2009 Sebastian Bartos <seth.kriticos@googlemail.com>
#  
#	  This program is free software: you can redistribute it and/or modify
#	  it under the terms of the GNU General Public License as published by
#	  the Free Software Foundation, either version 3 of the License, or
#	  (at your option) any later version.
#	   
#	  This program is distributed in the hope that it will be useful,
#	  but WITHOUT ANY WARRANTY; without even the implied warranty of
#	  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
#	  GNU General Public License for more details.
#	   
#	  You should have received a copy of the GNU General Public License
#	  along with this program. If not, see <http://www.gnu.org/licenses/>.
# ==============================================================================


## WARNING: THIS TESTCAS MESSES WITH YOUR DATA ON THE MAL SERVER, USE AT OWN
##          RISK!

## TEST CERDENTIAL DATA NEEDED TO COMMUNICATE TO SERVER
## YOU NEED TO SPECIFY THIS TO PASS STAGE 1
## MUST BE VALID MAL LOGIN USERNAME AND PASSWORD WITH ENOUGH ENRIES IN THE 
## ANIME LISTS (AT LEAST 12 COMPLETED AND 2 WACHING ENRIES) AND PUBLIC
username = 'fill me in!'
password = 'me too!'


## TESTLOGIC STARTING HERE

import os, sys
mbasepath = os.path.split(os.path.abspath(__file__))[0]
mbasepath2 = os.path.split(mbasepath)[0]
envpath = os.path.join(mbasepath2, 'src', 'AniChou')
sys.path.append(envpath)

from myanimelist import \
		_login, _fetch_list, _filter_sync_changes, _push_list, anime_data
from os import path, _exit, rename
from cPickle import dump, load
from pprint import pprint
from datetime import datetime


## TEST STAGE FUNCTIONS

def stage1(username):
	"""	Perform a fetch. """

	gd = dict()

	print '----------------'
	print 'starting stage 1'
	print '----------------'

	gd = _fetch_list(username)
	if gd:
		print 'list fetched'
		print 'stage 1 complete'
		return gd
	else:
		print 'FETCHING FAILED'
		_exit(1)

def stage2(gd):
	""" Prepare local and remote testdata. """

	print '----------------'
	print 'starting stage 2'
	print '----------------'

	ld = dict()
	rd = dict()

	g_watching_keys = list()
	g_completed_keys = list()
	
	basedata = dict()
	
	used_watching_keys = list()
	used_compled_keys = list()
	new_keys = list()
	del_keys = list()

	print 'extracting completed and watching keys..'
	for key, value in gd.items():
		if value['my_status'] == 1:
			g_watching_keys.append(key)
		elif value['my_status'] == 2:
			g_completed_keys.append(key)

	print 'number of watching keys: ', len(g_watching_keys)
	print 'number of completed keys: ', len(g_completed_keys)

	print 'adding 10 completed and 2 waching keys to data set..'
	for i in range(10):
		basedata[g_completed_keys[i]] = gd[g_completed_keys[i]]
		used_compled_keys.append(g_completed_keys[i])
	for i in range(10, 12):
		new_keys.append(g_completed_keys[i])
	for i in range(2):
		del_keys.append(g_completed_keys[i])
	for i in range(2):
		basedata[g_watching_keys[i]] = gd[g_watching_keys[i]]
		used_watching_keys.append(g_watching_keys[i])

	print 'used keys: ', (used_compled_keys, used_watching_keys)
	print 'new keys: ', new_keys
	print 'del keys: ', del_keys
	
	# checkpoint 1
	if len(basedata.keys()) == 12 and \
			len(used_compled_keys) + len(used_watching_keys) == 12:
		print '-------------------'
		print 'checkpoint 1 passed'
		print '-------------------'
	else:
		print 'SOMETHING WENT WRONG BEFORE CHECKPOINT 1'
		print 'The following should evaluate to 12, but are:'
		print 'basedata.keys(): ', len(basedata.keys())
		print 'used comleted + wached keys count: ', \
				(len(used_compled_keys) + len(used_watching_keys))
		_exit(1)

	print 'crafting local data set..'
	from copy import deepcopy
	ld = deepcopy(basedata)
	for key in used_watching_keys:
		ld[key]['my_watched_episodes'] += 1
		ld[key]['my_last_updated'] = datetime.now()

	print 'crafted local data keys: ', ld.keys()

	print 'crafting remote data set..'
	rd = deepcopy(basedata)
	for key in del_keys:
		del rd[key]
	for key in new_keys:
		rd[key] = gd[key]
	print 'crafted remote data keys: ', rd.keys()

	print 'stage 2 complete'
	return (ld, rd, new_keys, del_keys, used_watching_keys)


def stage3(local_set, remote_set, new_keys, deleted_keys, waching_mod_keys):
	""" Test and fix _filter_sync_changes """

	print '----------------'
	print 'starting stage 3'
	print '----------------'
	
	print 'calling _filter_sync_changes..'
	(remote_updates, local_updates, deleted_entry_keys) = \
		_filter_sync_changes(remote_set, local_set)

	print 'remote_updates dict keys: ', remote_updates.keys()
	print 'local_updates dict keys: ', local_updates.keys()
	print 'deleted_entry_keys: ', deleted_entry_keys

	if not (remote_updates and local_updates and deleted_entry_keys):
		print 'SOMETHING IN STAGE 3 WENT WRONG!'
		print 'all dicts must have keys,'
		print 'but at least one of the return arrays is empty'
		_exit(1)

	print 'stage 3 completed'
	return local_updates

def stage4(username, password, push_dict):
	""" Test and fix _push_list """

	print '----------------'
	print 'starting stage 4'
	print '----------------'

	print 'atepmting to push 2 changes:', push_dict.keys()
		
	from cookielib import LWPCookieJar
	from urllib2 import build_opener, install_opener, \
		HTTPCookieProcessor

	# setup cookie handler
	opener = build_opener(HTTPCookieProcessor(LWPCookieJar()))
	install_opener(opener)

	if _login(username, password):
		if _push_list(push_dict):
			print 'enries pushed'
			print 'don\'t forget to reset the list ^^'
			print 'stage 4 completed'
		else:
			print 'PUSHING FAILED'
			_exit(1)
	else:
		print 'LOGIN FAILED, CHECK CREDENTIALS!'
		_exit(1)

def stage5(username, password):
	""" Test anime_data fetch and full syncronization """

	print '----------------'
	print 'starting stage 5'
	print '----------------'
	
	# move existing data file to backup (you will have to manually restore it
	db_path = path.join(path.expanduser("~"), ".anichou.dat")
	db_path_bak = path.join(path.expanduser("~"), ".anichou.dat.bak")
	if path.isfile(db_path):
		rename(db_path, db_path_bak)

	instance = anime_data(username, password)
	print 'current db should be empty..'
	print 'current db: ', instance.db

	print 'fetching data..'
	instance.fetch()
	if instance.db:
		# print 'data keys are: ', instance.db.keys()
		print 'data feched..'
	else:
		print 'SOMETHING WENT WRONG WITH THE FETCHING'
		_exit(1)
	
	print 'now we manipulate your watching episodes a bit'
	print '(we will increment one)'
	waching_keys = list()
	for key, value in instance.db.items():
		if instance.db[key]['my_status'] == 1:
			waching_keys.append(key)
	print 'found the following keys: ', (len(waching_keys), waching_keys)
	print 'I will play with this one: ', waching_keys[0]

	instance.db[waching_keys[0]]['my_watched_episodes'] += 1
	instance.db[waching_keys[0]]['my_last_updated'] = datetime.now()

	print 'and finally we perform a sycronization test..'
	(remote_updates, remote_deletes) = \
		instance.sync()

	print 'if you play in the webinterface with the values or delete something'
	print 'then it sould come up here:'
	print 'remote updates: ', remote_updates
	print 'remote_deletes: ', remote_deletes

	print 'stage 5 done'

## RUN TESTCASES

print '================================='
print 'Starting myanimelist test routine'
print '================================='

## NOTE: DO ONLY STAGES 1-4 OR 5 AT ONCE
##       (COMMENT OUT THE OTHER(S))

gd = stage1(username)
(local_set, remote_set, new_keys, deleted_keys, waching_mod_keys) = \
  	stage2(gd)
local_updates = \
  	stage3(local_set, remote_set, new_keys, deleted_keys, waching_mod_keys)
stage4(username, password, local_updates)

# stage5(username, password)

print '======================='
print 'we are done! bye bye :)'
print '======================='


