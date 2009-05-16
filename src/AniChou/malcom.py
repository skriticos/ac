#!/opt/local/bin/python2.5
"""
Malcom communicates with MyAnimeList.
"""
# Standard library.
import urllib
import urllib2
import urlparse
import re
import datetime
# Third party.
import BeautifulSoup
# Our own.
import data

class Request(object):
    def __init__(self, url, query, head, data = None):
        """
        Takes one string and three dictionaries.
        """
    	# Make tuple mutable.
    	parts = list(urlparse.urlparse(url))
    	# Set parameters.
    	parts[4] = urllib.urlencode(query)
    	# Dafely modified.
    	url = urlparse.urlunparse(parts)
    	self.request = urllib2.Request(url, headers = head)
    	if data:
            self.request.add_data(urllib.urlencode(data))

    def execute(self, opener):
        """
        Takes OpenDirector.
        
        This does all the work and can take a while.
        """
        self.response = opener.open(self.request)

    def __iter__(self):
        """
        Yield content.
        
        Only after execution!
        
        This should be fast.
        """
        yield self.response.read()

class LoginError(urllib2.URLError):
    pass

class UsernameError(LoginError):
    pass

class PasswordError(LoginError):
    pass

class MAL(Request):
    def __init__(self, url, query, head, data = None):
        default = {"User-Agent": "AniChou"}
        default.update(head)
        Request.__init__(self, url, query, default, data)

    def execute(self, opener):
        Request.execute(self, opener)
        # Super set attribute.
        self.content = self.response.read()
        # Translate 200 OK with human-readable error message.
        if self.content.strip() == "Invalid username":
            raise UsernameError, "called appInfo with non-existant nick"
        match = re.search(
            r'<div.+?class\s*=\s*["\']?badresult.+?>(.+?)</div>', self.content)
        if match:
            result = match.group(1)
            if "Could not find that username" in result:
                raise UsernameError, "tried to log in with non-existant nick"
            elif "Invalid password" in result:
                raise PasswordError, "tried to log in with wrong password"
            elif "You must first login" in result:
                raise LoginError, "not logged in"
            else:
                raise urllib2.URLError, "bad result"

    def __iter__(self):
        yield self.content

class Panel(MAL):
    def __init__(self, anime):
        """
        Takes mal_anime_data_schema.
        """
        url = "http://myanimelist.net/panel.php"
        query = dict(
            keepThis  = "true",
            go        = "edit",
            hidenav   = 1,
            TB_iframe = "false",
            id        = anime["my_id"]
            )
        data = dict(
            submitIt          = 2,
            close_on_update   = "true",
            series_animedb_id = anime["series_animedb_id"],
            series_title      = anime["series_animedb_id"],
            completed_eps     = anime["my_watched_episodes"],
            status            = anime["my_status"],
            score             = anime["my_score"]
            )
        MAL.__init__(self, url, query, {}, data)

class List(MAL):
    def __init__(self, username, typ = "anime"):
        """
        Type may be anime or manga.
        """
        url = "http://myanimelist.net/malappinfo.php"
        query = dict(
            u = username,
            status = "all"
            )
        if typ == "manga":
            query["type"] = typ
        MAL.__init__(self, url, query, {})

    def execute(self, opener):
        # Super sets attribute.
        MAL.execute(self, opener)
        # BeautifulSoup could do the read() and unicode-conversion, if it
        # weren't for the illegal characters, as it internally doesn't
        # use 'replace'.
        fetch_response = unicode(self.content, 'utf-8', 'replace')
        xmldata = BeautifulSoup.BeautifulStoneSoup(fetch_response)
        # For unknown reasons it doesn't work without recursive.
        # Nor does iterating over myanimelist.anime. BS documentation broken?
        self.anime_nodes = xmldata.myanimelist.findAll('anime',
            recursive = True)

    def __iter__(self):
        # We have to manually convert after getting them out of the CDATA.
        entity = lambda m: BeautifulSoup.Tag.XML_ENTITIES_TO_SPECIAL_CHARS[m.group(1)]
        for anime in self.anime_nodes:
            # ac_node builds the output of our function. Everything added to it
            # must either be made independent of the parse tree by calling
            # NavigableString.extract() or, preferrably, be turned into a
            # different type like unicode(). This is a side-effect of using
            # non-mutators like string.strip()
            # Failing to do this will crash cPickle.
            ac_node = dict()
            for node, typ in data.mal_anime_data_schema.iteritems():
                try:
                    value = getattr(anime, node).string.strip()
                    # One would think re.sub directly accepts string subclasses
                    # like NavigableString. Raises a TypeError, though.
                    value = re.sub(r'&(\w+);', entity, value)
                except AttributeError:
                    continue
                if typ is datetime.datetime:
                    # process my_last_updated unix timestamp
                    ac_node[node] = datetime.datetime.fromtimestamp(int(value))
                elif typ is int:
                    # process integer slots
                    ac_node[node] = int(value)
                elif typ is datetime.date and value != '0000-00-00':
                    # proces date slots
                    (y,m,d) = value.split('-')
                    (y,m,d) = int(y), int(m), int(d)
                    if y and m and d:
                        ac_node[node] = datetime.date(y,m,d)
                else:
                    # process string slots
                    ac_node[node] = value

            # series titles are used as anime identifiers
            # the keys for the resulting dictionary are encoded to ASCII, so they
            # can be simply put into shelves
            key = ac_node['series_title'].encode('utf-8')

            # add node entry to the resulting nodelist
            yield key, ac_node

class Search(MAL):
    def __init__(self, query, typ = "anime"):
        typ = ("anime", "manga", "all").index(typ) + 1
        url = "http://myanimelist.net/includes/masearch.inc.php"
        query = dict(
            s = query,
            type = typ
            )
        head = dict(Referer = "http://myanimelist.net/addtolist.php")
        MAL.__init__(self, url, query, head)

class Add(MAL):
    def __init__(self, series_animedb_id, status, completed_eps, score = 0):
        """
        Takes values from mal_anime_data_schema.
        """
        url = "http://myanimelist.net/includes/masearch.inc.php"
        if not completed_eps:
            # How the site does it.
            completed_eps = ""
        query = dict(
            animeid = series_animedb_id,
            status = status,
            score = score,
            eps = completed_eps
            )
        head = dict(Referer = "http://myanimelist.net/addtolist.php")
        MAL.__init__(self, url, query, head)

    def execute(self, opener):
        MAL.execute(self, opener)
        # Super set attribute.
        if self.content.strip() != "maSuccessAdded":
            raise URLError, "couldn't add"

class Login(MAL):
    def __init__(self, username, password):
        url = "http://myanimelist.net/login.php"
        data = dict(
            username = username,
            password = password,
            sublogin = "Login",
            cookie = 1
            )
        MAL.__init__(self, url, {}, {}, data)

class Site(object):
    """
    A factory for requests.
    
    Handles cookie jar, of which there should be one per thread.
    """

    def __init__(self):
        # In-memory only.
        self.cookies = cookielib.CookieJar()
        parser = urllib2.HTTPCookieProcessor(self.cookies)
        # Constructor does not add default handlers.
        self.opener = urllib2.OpenerDirector()
        self.opener.add_handler(parser)
        
    def login(self, username, password):
        pass
