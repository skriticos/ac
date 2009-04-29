#!/usr/bin/env python
# =========================================================================== #
# Name:    animecollector.py
# Purpose: AnimeCollecor application starup script
#          Will be installed as executable by the setup script
#          Loads configuration and runs main routine.
#
# Copyright (c) 2009 Sebastian Bartos
# Copyright (c) 2009 Andre 'Necrotex' Peiffer
#
# License: GPL v3, see COPYING file for details
# =========================================================================== #

import os, sys
import AnimeCollector.cmdoptions, \
		AnimeCollector.globs, \
		AnimeCollector.config, \
		AnimeCollector.myanimelist, \
		AnimeCollector.gtkctl

# Unified runtime data dict -- contains all runtime instance references
rundat = {}

## FIRST RUN STUFF

# Check for AnimeCollector home path existence
# Create it if not existient
if not os.path.isdir(AnimeCollector.globs.ac_user_path):
	os.mkdir(AnimeCollector.globs.ac_user_path)


# Run command line option parser
rundat['cmdopts'] = AnimeCollector.cmdoptions.AcOptParse(sys.argv) 

## IMPORT PLUGIN MODULE
# - todo

# Run configuration parser
rundat['config'] = AnimeCollector.config.ac_config()

# Run anime data module
username = rundat['config'].get('mal', 'username')
password = rundat['config'].get('mal', 'password')
rundat['anime_data'] = AnimeCollector.myanimelist.anime_data(username, password)

## RUN THE APPLICATION
# gtkmain.main(config, mal_anime_data)
if rundat['cmdopts'].values.gui:
	gui = AnimeCollector.gtkctl.guictl(rundat)
else:
	print 'no-gui option set'

print 'Shutting down, bye bye..'

