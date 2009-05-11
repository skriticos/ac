#!/usr/bin/env python
# =========================================================================== #
# Name:    anichou.py
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
import AniChou.globs, \
		AniChou.config, \
		AniChou.myanimelist
		

## FIRST RUN STUFF

# Check for AniChou home path existence
# Create it if not existient
if not os.path.isdir(AniChou.globs.ac_user_path):
	os.mkdir(AniChou.globs.ac_user_path)


# Run command line option parser and configuration parser
config = AniChou.config.ac_config()

## IMPORT PLUGIN MODULE
# - todo

# The whole application uses only this single instance of anime_data.
data = AniChou.myanimelist.anime_data(config = config)

## RUN THE APPLICATION
# gtkmain.main(config, mal_anime_data)
if config.get('startup', 'gui'):
    ## ONLY RUN GUI IF CLI OPTION NOT SET ##
    import AniChou.gtkctl
    gui = AniChou.gtkctl.guictl(data, config)
else:
	print 'no-gui option set'

print 'Shutting down, bye bye..'
