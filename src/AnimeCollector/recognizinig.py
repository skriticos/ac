# recognizing.py - Recognizing engine 
# Copyright (c) 2009 Andre 'Necrotex' Peiffer
# See COPYING for details


# Standardlib
import re
import cPickle
import difflib
from os import path

# AnimeCollector 
from globs import ac_data_path

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
          Check if there are more than one and return
          the season of the current watched. Future feature. ^^
          """
          pass
 
   
class engine:
    """Recognizing engine"""

    def __init__(self, filename):

        self.filename = filename
        self.current_entry = str
          
        # Read database, if it can't be read return false
        # Read database, if it can't be read return false
        if path.exists(ac_data_path):
            dbhandle = open(ac_data_path, "rb")
            self.db  = cPickle.load(dbhandle)
            dbhandle.close()
        else:
            return False

        # Dictonary for matching results and radio
        # Schema: {'anme_name' : ratio}
        self.matching = dict()

        # filename_processor object 
        fp = filename_processor(self.filename)
        self.anime = fp.getName()
        self.episode = fp.getEpisode()
        self.season = fp.getSeason() 
          
    def __del__(self):
        """ Maybe needed to close a opened file/DB"""
        #TODO: Find a OS undependend way for checking if a file is open.
        pass
        
    def __matching(self):
        """ 
        Evaluates a ratio of probable equally and returns the most likely Anime
        """
        matching = dict()
        # Fill a dict with the 
        for anime in self.db[key]:
            matching[anime].append(0)
        
        # The essence machting algorithm
        for anime in matching[key]:
            ratio = difflib.SequenceMatcher(None, anime, self.anime)
            self.matching[anime] = ratio
        
        # Sorting self.matching and retrun it...
        # Well, this is a bit of a hack since you can't really sort dicts
        # TODO: Should be tested :D
        rLst = self.matching.items()
        rSort = [ [v[1],v[0]] for v in rLst]
        rSort.sort()
        self.matching = [rSort[i][1] for i in range(0,len(rSort))]
        
        return self.matching

    def match(self):
        """
        Main method, returns true on success and 
        false failure. Maybe codes would be better (e.g. 1 = Success,
        2 = Episode allready watched, 3 = no series found).        
        """ 
        
        dictMatch = __matching()
        
        # Check if there is a ratio over 0.8
        if dictMatch[0] < 0.8:
            return False
        
        # Update self.db
        for k in self.db:
            if k == dictMatch[0]:
                self.db[k]['my_watched_episodes'] = self.episode
        
        # Write changes to locale db
        dbhandle = open(ac_data_path, "rb")
        cPickle.dump(self.db, dbhandle)
        dbhandle.close()
        
        return True

