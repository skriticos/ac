"""
============================================================== GPL v3 stuff ==
Copyright (c) 2009 Andre Peiffer <ich@necrotex.de>
 
  This program is free software: you can redistribute it and/or modify
  it under the terms of the GNU General Public License as published by
  the Free Software Foundation, either version 3 of the License, or
  (at your option) any later version.
   
  This program is distributed in the hope that it will be useful,
  but WITHOUT ANY WARRANTY; without even the implied warranty of
  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
  GNU General Public License for more details.
   
  You should have received a copy of the GNU General Public License
  along with this program. If not, see <http://www.gnu.org/licenses/>.
==============================================================================

This is a little testcase script for the recognizing engine. It reads the 
"test_recognizing.txt" file which contains a couple of anime filenames.
----------------------------------------------------------------------------

How to get started:
===================
Fetch some filenames of animes which are in your list and place them in the 
"test_recognizing.txt" file. A new line for each one.

Just start the script and watch the output. If a filename dosn't get 
recognized  drop me a note at the bugtracker or at the forums.

======================================================================
ATTENTION: RUNNING THIS WILL UPDATE YOUR LOCAL DATABASE! USE CAREFULL!
====================================================================== 
"""

import os , sys
import difflib

# taken from test_mal.py
mbasepath = os.path.split(os.path.abspath(__file__))[0]
mbasepath2 = os.path.split(mbasepath)[0]
envpath = os.path.join(mbasepath2, 'src', 'AniChou')
sys.path.append(envpath)

from recognizinig import engine

# Read the text file
fhandle = open("test_recognizing.txt")
flist = fhandle.readlines()
fhandle.close()


for filename in flist:
    e = engine(filename)
    match = e.match()
    
    print "-----------------------------------------------------"
    print "Raw Filename: ", filename
    print "Filterd Name: ", e._getName()
    print "Filterd Episode: ", e._getEpisode()
    
    if match:
        print "DB Key: ", e.match()
        r = difflib.SequenceMatcher(None, e._getName(), match)
        print "Matching Ratio: ", r.ratio()
    else:
        print "Not found in locale db"
    print "-----------------------------------------------------"
    print ""   
    
print "======DONE======"
