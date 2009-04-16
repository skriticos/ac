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
     """
    Prepare the filename for the matching engine. Can later be used for the 
    current playing status and the file rename engine
    """
     def __init__(self, filename):
          self.filename = filename
          self.animeName = str
          self.animeEpisode = int

     def _filter(self):
          """Get rid of hashtags, subgroup, codec and such"""
         
         # Second version of the RegEx. 
         #matches all charactes between "[" and "]"
          reg = re.compile("([[a-zA-Z0-9\-]*])")
          anime_raw = reg.sub("", self.filename)
         
         # get rid of underscores
          anime_raw = anime_raw.replace("_"," ")
         
         # get rid of the file extension, currently just .mkv, .mp4 and .avi
          anime_raw = re.sub("((.mkv)|(.mp4)|(.avi))$","",anime_raw)
          
          return anime_raw.strip()

     def getName(self):
        """getting and returning anime name"""

        # get rid of the Episode 
        self.animeName = re.sub("[0-9\s]{1,}", "", self._filter())

        # get rid of scores
        self.animeName = self.animeName.replace("-","")

        return self.animeName.strip()

     def getEpisode(self):
        """getting and returning anime episode"""
        self.animeEpisode = re.sub("[a-zA-Z\-~\s]{1,}", "", self._filter())
            
        # TODO: Add a RegEx for matching out the Season Number
        
        return self.animeEpisode.strip()
        
     def getSeason(self):
          """
          ckeck if there are more than one and return
          the season of the current watched
          """
          pass
 
   
class engine:
    """Recognizing engine"""

    def __init__(self, filename):

        self.db_path = path.join(path.expanduser("~"), ".animecollector.dat")
        self.filename = filename
        self.current_entry = str
          
        # Read database 
        if path.exists(self.db_path):
            dbhandle = open(self.db_path)
            self.db  = cPickle.load(dbhandle)
            dbhandle.close()

        # Dictonary for matching results and radio
        # Schema: {'anme_name' : ratio}
        self.matching = {}

        # filename_processor object 
        fp = file_processor(self.filename)
        self.anime = fp.getName()
        self.episode = fp.getEpisode()
        self.season = fp.getSeason() 
          
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
        """
        Main method, returns true on success and 
        false and an errormsg on failure
        """
        pass
