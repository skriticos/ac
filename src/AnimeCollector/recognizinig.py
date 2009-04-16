# recognizing.py - Recognizing engine 
# Copyright (c) 2009 Andre 'Necrotex' Peiffer
# See COPYING for details


# Standardlib
import string
import re
import cPickle
import difflib
from os import path

# Mal dataschema
from data import mal_data_schema


class filename_processor:
     """Prepare the filename for the matching engine. Can later be used for the current playing status and the file rename engine"""
     def __init__(self, filename):
          self.filename = filenname

     def __filter(self):
          """Get rid of hashtags, subgroup, codec and such"""
         
         # First version of the RegEx. matches all charactes between "[" and "]"
          reg = re.compile("([[a-zA-Z0-9]*])")
          anime_raw = reg.sub("", self.filename)
         
         # get rid of underscores
          anime_raw = replace("_"," ",anime_raw)
         
         # get rid of the file extension, currently just .mkv, .mp4 and .avi
          anime_raw = re.sub("^.+\.((mkv)|(mp4)|(avi))$","",anime_raw)
          
          return trim(anime_raw)

     def _get_name(self):
          """getting and returning anime name"""
         
         animeName = re.spilit(self.__filter())
         

     def _get_episode(self):
          """getting and returning anime episode"""
          pass

class engine:
     """Recognizing engine"""

     def __init__(self):
          self.db_path = path.join(path.expanduser("~"), ".animecollector.dat")
                    
         # Read database 
          if path.exists(self.db_path):
              dbhandle = open(self.db_path)
              self.db  = cPickle.load(dbhandle)
              dbhandle.close()

          # Dictonary for matching results and radio
          # schema: {'anme_name' : ratio}
          self.matching = {}

          # fileprocessor object 
          fp = file_processor
          self.anime = fp.get_name
          self.episode = fp.get_episode
          
     def __del__(self):
          """ Maybe needed to close a opened file/DB"""
          pass

     def __matching(self):
          """The matching algorythm. Returns self.matching"""
          pass

     def __sort(self):
          """Sort and return self.matching for the highest ratio. """
          pass

     def __update(self):
          """Updates the episode in DB"""
          pass

     def match(self):
          """Main method, returns true on success and false and an errormsg on failure"""
          pass
