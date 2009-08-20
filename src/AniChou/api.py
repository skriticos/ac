# Copyright (c) 2009 Andre 'Necrotex' Peiffer
# See COPYING for details

## A complete implementation of the official MAL API.
## Works for both anime and manga lists

import httplib2
from urllib import urlencode

class api(object):
    """
    Methods expect a numeric global MAL database id and XML data.
    """

    def __init__(self, user, password, type="anime"):
        self.user = user
        self.password = password
        self.type = type
        self.base = "http://myanimelist.net/api/"

    def __type(self, search=False):
        """Build the URI"""
        if self.type not in ('anime', 'manga'):
            raise NameError("Uknown type string")
        infix = '' if search else 'list'
        return self.type + infix + '/'

    def add(self, id, data):
        """Add an anime to the list"""

        req = httplib2.Http(".cache")
        req.add_credentials(self.user, self.password)
        q = self.base + self.__type() + "add/" + str(id) + ".xml"
        header = {'Content-Type' : 'application/x-www-form-urlencoded'}
        return req.request(q, "POST", headers=header, body=urlencode(data))

    def update(self, id, data):
        """Update series info"""

        req = httplib2.Http(".cache")
        req.add_credentials(self.user, self.password)
        q = self.base + self.__type()+ "update/" + str(id) + ".xml"
        header = {'Content-Type' : 'application/x-www-form-urlencoded'}
        return req.request(q, "POST", headers=header, body=urlencode(data))

    def delete(self, id, data):
        """Deletes list entries"""

        req = httplib2.Http(".cache")
        req.add_credentials(self.user, self.password)
        q = self.base + self.__type() + "delete/" + str(id) + ".xml"
        header = {'Content-Type' : 'application/x-www-form-urlencoded'}
        return req.request(q, "DELETE", headers=header, body=urlencode(data))[1]

    def search(self, query):
        """Search for series"""

        req = httplib2.Http(".cache")
        req.add_credentials(self.user, self.password)
        q = self.base + self.__type(True) + "search.xml?" + urlencode({'q': query})
        return req.request(q ,"GET")[1]

