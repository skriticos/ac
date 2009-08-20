# Copyright (c) 2009 Andre 'Necrotex' Peiffer
# See COPYING for details

## A complete implementation of the MAL API for animes
## Works for both, anime and manga lists

import httplib2
from urllib import urlencode

class api(object):

    def __init__(self, user, password, type="anime"):
        self.user = user
        self.password = password
        self.type = type
        self.base = "http://myanimelist.net/api/"

    def __type(self, search=False):
        """Method needed for building the URI"""
        if search:
            if self.type == "anime":
                return str("anime/")
            elif self.type == "manga":
                return str("manga/")
        elif self.type == "manga":
            if self.type == "anime":
                return str("animelist/")
            elif self.type == "manga":
                return str("mangalist/")
        else:
            raise NameError("Not known Typename!")

    def add(self, id, data):
        """Adds an Anime to the list"""

        req = httplib2.Http(".cache")
        req.add_credentials(self.user, self.password)
        q = self.base + self.__type() + "add/" + str(id) + ".xml"
        header = {'Content-Type' : 'application/x-www-form-urlencoded'}
        return req.request(q, "POST", headers=header, body=urlencode(data))

    def update(self, id, data):
        """Updates series infos"""

        req = httplib2.Http(".cache")
        req.add_credentials(self.user, self.password)
        q = self.base + self.__type()+ "update/" + str(id) + ".xml"
        header = {'Content-Type' : 'application/x-www-form-urlencoded'}
        return req.request(q, "POST", headers=header, body=urlencode(data))

    def delete(self, id, data):
        """Deletes listentries"""

        req = httplib2.Http(".cache")
        req.add_credentials(self.user, self.password)
        q = self.base + self.__type() + "delete/" + str(id) + ".xml"
        header = {'Content-Type' : 'application/x-www-form-urlencoded'}
        return req.request(q, "DELETE", headers=header, body=urlencode(data))[1]

    def search(self, query):
        """Search method."""

        req = httplib2.Http(".cache")
        req.add_credentials(self.user, self.password)
        q = self.base + self.__type(True) + "search.xml?" + urlencode({'q': query})
        return req.request(q ,"GET")[1]

