#!/usr/bin/env python

# Copyright (c) 2008-2009 Sebastian Bartos.
# Copyright (c) 2009 Andre 'Necrotex' Peiffer
# See COPYING for details.

""" animecollector -- actual application executable

Will be installed in your PATH directory. It checks for first run stuff 
(like if there is already a user directory) and sets up things that are missing.

Loads configuration if existent.

Checks if plugins are enabled and loads them.

Then it runs the main routine.
"""

from os import path, mkdir
from AnimeCollector.globs import ac_user_path
#from AnimeCollector import gtkmain
from AnimeCollector.config import ac_config
from AnimeCollector.myanimelist import anime_data

from AnimeCollector import gtkctl


## FIRST RUN STUFF

# Check for AnimeCollector home path existence
# Create it if not existient
if not path.isdir(ac_user_path):
	mkdir(ac_user_path)

## IMPORT CONFIG MODULE (READ CONFIGURATION)
# - todo

## IMPORT PLUGIN MODULE
# - todo
	
config = ac_config()
mal_anime_data = anime_data(config.mal['username'], config.mal['password'])

## RUN THE APPLICATION
# gtkmain.main(config, mal_anime_data)
gui = gtkctl.gui(config, mal_anime_data)

