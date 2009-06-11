import os
import urllib2
import cookielib
# Make it easy to switch.
from cPickle import Pickler
from cPickle import Unpickler

from wx.lib.pubsub import Publisher

import service
import fulltext
import malcom
import preferences

class Account(object):
    def __init__(self, config, parent):
        self.site = parent
        # In-memory only.
        self.cookies = cookielib.CookieJar()
        parser = urllib2.HTTPCookieProcessor(self.cookies)
        self.opener = urllib2.build_opener(parser)
        self.config = config
        folder = preferences.path("data", self.site.name)
        # Dangerous filename.
        self.fname = os.path.join(folder, config["username"] + ".anime")
        try:
            f = open(self.fname, 'rb')
            p = Unpickler(f)
            self.model = p.load()
            f.close()
        except IOError:
            # No such file.
            self.model = {}
        Publisher().subscribe(self.save, "save")

    def save(self, message = None):
        f = open(self.fname, 'wb')
        p = Pickler(f)
        p.dump(self.model)
        f.close()

    def pull(self):
        req = malcom.List(username = self.config["username"])
        req.execute(self.opener)
        state = dict(req)
        for stupidkey, anime in state.iteritems():
            self.site.index(anime)
        return state

    def push(self, state):
        for stupidkey, anime in state.iteritems():
            req = malcom.Panel(anime)
            req.execute(self.opener)

    def sync(self, state):
        pass

class MyAnimeList(service.SiteProvider):
    name = "myal"
    
    def __init__(self):
        folder = preferences.path("cache", self.name)
        self.titles = fulltext.Index(os.path.join(folder, "titles"))
        self.opener = urllib2.build_opener()
        
    def account(self, preferences):
        return Account(preferences, self)

    def search(self, title, remote = True):
        key = self.titles.has_title(title)
        if key:
            return [(1.0, title, key)]
        results = self.titles.search(title)
        try:
            if results[0][0] > 0.5:
                return results
        except IndexError:
            pass
        if not remote:
            return []
        for word in fulltext.tokenize(title):
            self.remote_search(word)
        return self.search(title, False)

    def index(self, anime):
        key = anime["series_animedb_id"]
        if not self.titles.has_series(key):
            titles = malcom.harvest(anime)
            self.titles.add(key, *titles)

    def remote_search(self, word):
        # TODO query caching.
        req = malcom.Search(word)
        req.execute(self.opener)
        for anime in req:
            self.index(anime)
        self.titles.save()
