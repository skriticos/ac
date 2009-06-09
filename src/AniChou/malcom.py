"""
Malcom communicates with MyAnimeList.
"""
# Standard library.
import urllib
import urllib2
import urlparse
import re
import datetime
import os
import distutils.dir_util
from xml.etree.cElementTree import XMLTreeBuilder
# Third party.
import BeautifulSoup
# Our own.
import data
import tidy

# TODO move out of *mal*com.
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
            raise UsernameError, "called appInfo with non-existent nick"
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
        self.content = tidy.xml(self.content)
        parser = XMLTreeBuilder()
        parser.feed(self.content)
        self.tree = parser.close()

    def __iter__(self):
        # We have to manually convert after getting them out of the CDATA.
        entity = lambda m: BeautifulSoup.Tag.XML_ENTITIES_TO_SPECIAL_CHARS[m.group(1)]
        for anime in self.tree.getiterator("anime"):
            # ac_node builds the output of our function. Everything added to it
            # must either be made independent of the parse tree.
            # Failing to do this will crash cPickle.
            ac_node = dict()
            for child in anime:
                node = child.tag
                try:
                    typ = data.mal_anime_data_schema[node]
                except KeyError:
                    continue
                value = child.text.strip()
                value = re.sub(r'&(\w+);', entity, value)
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

def harvest(anime):
    """
    Return synonyms and title of anime_data_schema.
    """
    try:
        string = anime["series_synonyms"]
        syn = string.split(";")
        if len(syn) == 1:
            # MAL uses various delimiters.
            syn = string.split(",")
        # Get red of empty elements from leading or trailing delimiters.
        titles = filter(None, syn)
    except KeyError:
        titles = []
    titles.append(anime["series_title"])
    # Delimiter sometimes followed by space.
    return [t.strip() for t in titles]

class Search(MAL):
    def __init__(self, query, typ = "anime"):
        typ = ["anime", "manga", "all"].index(typ) + 1
        url = "http://myanimelist.net/includes/masearch.inc.php"
        query = dict(
            s = query,
            type = typ
            )
        head = dict(Referer = "http://myanimelist.net/addtolist.php")
        MAL.__init__(self, url, query, head)

    def execute(self, opener):
        # Super sets attribute.
        MAL.execute(self, opener)
        soup = BeautifulSoup.BeautifulSoup(self.content)
        self.div_nodes = soup.findAll("div", id = True, recursive = True)

    def __iter__(self):
        """
        Yield incomplete mal_anime_data_schema structures.
        
        Unfortunately series_image is not even in the HTML.
        """
        for div in self.div_nodes:
            m = re.match(r'arow(\d+)', div["id"])
            if not m:
                continue
            ac_node = dict(
                series_animedb_id = int(m.group(1)),
                series_title = div.find("strong").string
                )
            # TODO scrape episode total to compare with other sites.
            span = div.find("span", title = "Synonyms", recursive = True)
            if span:
                ac_node["series_synonyms"] = span.nextSibling.string
            yield ac_node

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
            raise urllib2.URLError, "couldn't add"

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

class Image(object):
    # Not subclassing MAL because it reads the data.
    # We could copy the User-Agent code, but who cares.
    # Not subclassing Request because we do urlparse anyway.
    def __init__(self, url, cache):
        """
        The first argument can be a URL string or a mal_anime_data_schema.
        This convenience might be removed if the class goes into a global
        module.
        
        Takes the path of a local folder. It should be absolute without ~ or
        variables. It need not exist.
        """
        try: url = url["series_image"]
        except TypeError: pass
        # We assume a lot. Strange addresses spell a horrible death.
    	part = urlparse.urlparse(url)
    	# If the following algorithm changes, the cache should be deleted.
    	host = part.hostname
    	# Some attributes default to None, others to the empty string.
    	port = part.port or "80"
    	# Could use urllib.url2pathname(part.path) to make relative.
    	path = part.path[1:]
    	locl = os.path.join(cache, host, port, path)
    	# Create missing ancestors.
    	distutils.dir_util.mkpath(os.path.dirname(locl))
    	self.target = locl
    	self.request = urllib2.Request(url)

    def execute(self, opener):
        """
        Takes OpenDirector.
        
        Once an image is in the cache, it will never be updated.
        
        We do not copy any meta-data (like mtime) from headers
        onto the file.
        """
        if os.path.exists(self.target):
            return
        # Inspired by urllib.retrieve
        resp = opener.open(self.request)
        locl = open(self.target, 'wb')
        # Does not check Content-length.
        locl.write(resp.read())
        locl.close()
        resp.close()
        # We could catch any exceptions and simply pretend 404.

    def __iter__(self):
        """
        Yield local filename, or None.
        """
        yield self.target
