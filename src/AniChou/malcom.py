"""
Malcom communicates with MyAnimeList.
"""

import urllib
import urllib2
import urlparse
import re
from cStringIO import StringIO

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
        """
        self.response = opener.open(self.request)

    def __iter__(self):
        """
        Yield content.
        
        Only after execution!
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
        # Now set.
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

class MALErrorProcessor(urllib2.BaseHandler):
    """
    Translate the site's human-readable error messages into proper HTTP.
    """

    def http_response(self, request, response):
        code, msg, hdrs = response.code, response.msg, response.info()
        if code != 200:
            # We only handle non-obvious errors.
            return response
        html = response.read().strip()
        # People expect that. Only it doesn't work, breaking the whole class.
        # There is a seek_wrapper in
        # http://codespeak.net/svn/wwwsearch/ClientCookie/trunk/ClientCookie/_Util.py
#       response.seek(0)
        if html == "Invalid username":
            # Returned by appInfo.
            return self.parent.error(
                'http', request, response, 404, msg, hdrs)
        match = re.search(
            r'<div.+?class\s*=\s*["\']?badresult.+?>(.+?)</div>', html)
        if not match:
            # All is right.
            return response
        result = match.group(1)
        for error in ("Could not find that username", "Invalid password",
            "You must first login"):
            # Returned by login and panel, respectively.
            if error in result:
                # Let the others guess whether to re-try.
                return self.parent.error(
                    'http', request, response, 401, msg, hdrs)
        # We got *something* bad but don't dare put the message in the error.
        return self.parent.error(
            'http', request, response, 400, msg, hdrs)

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

class Remote(object):
    """
    A client for part of a server.
    
    Most methods use keyword arguments even for required information so that
    subclasses can provide defaults.
    """

    def url(self, **kwargs):
        """
        Return a URL string.
        
        _url    A full URL with scheme and path. Query strings, if present,
                are discarded. Required argument.
        xyz     Everything else is used to build a query string.

        Always returns self._url if set.
        """
        try:
            return self._url
        except AttributeError:
            pass
        # Raises KeyError.
        tmpl = kwargs.pop("_url")
    	# Make tuple mutable.
    	tmpl = list(urlparse.urlparse(tmpl))
    	# New parameters.
    	tmpl[4] = urllib.urlencode(kwargs)
    	# The modified template.
    	return urlparse.urlunparse(tmpl)

    def request(self, **kwargs):
        """
        Return a request object.
        
        _url    A full URL which may contain a query string.
                It won't be touched. Defaults to self.url()
        xyz     Everything else is used as HTTP headers.
                Those are somewhat case-sensitive.
                
        Referer is recommended.

        Always returns self._request if set.
        """
        try:
            return self._request
        except AttributeError:
            pass
        try:
            tmpl = kwargs.pop("_url")
        except KeyError:
            tmpl = self.url()
    	return urllib2.Request(tmpl, headers = kwargs)

    def post(self, **kwargs):
        """
        Return a modified request object.
        
        _request    A request object complete with headers. Required.
        xyz         Everything else is added as form-urlencoded data,
                    turning the request from GET into POST.
        """
        # Raises KeyError.
        req = kwargs.pop("_request")
    	# add_data automatically sets content-type and turns req into POST.
        req.add_data(urllib.urlencode(kwargs))
        return req
        
    def response(self, opener, reget = False):
        """
        Execute request and return result.
        
        Use the given OpenDirector, which should contain a (logged in)
        CookieProcessor, to execute self.request()
        
        Also stores the result and will return it immediatly in the future,
        unless reget is True.
        
        Normally the response can only be read() once, as sockets don't know
        seek(). To get around this we replace it with StringIO. This means
        the whole body takes up memory.
        """
        if reget:
            del self._response
        try:
            return self._response
        except AttributeError:
            pass
        resp = opener.open(self.request())
        # Construct replacement like in AbstractHTTPHandler.
        self._response = urllib.addinfourl(
            # We can use cStringIO because urllib2 doesn't return unicode(),
            # except encoded. Right?
            StringIO(resp.read()),
            resp.headers,
            resp.url
            )
        # Copy attributes. Violates encapsulation.
        self._response.code = resp.code
        self._response.msg = resp.msg
        return self._response

class MAL(Remote):
    def request(self, **kwargs):
        head = {"User-Agent": "AniChou"}
        head.update(kwargs)
        return Remote.request(self, **head)

    def response(self, opener, reget = False):
        resp = Remote.response(self, opener, reget)
        # Code from MALErrorProcessor goes here.

class List(MAL):
    def __init__(self, username, typ = "anime"):
        """
        Type may be anime or manga.
        """
        kwargs = dict(u = username)
        if typ == "manga":
            kwargs["type"] = typ
        self._url = self.url(**kwargs)

    def url(self, **kwargs):
        """
        Return an appInfo URL.
        
        u       Username. Required.
        status  Default 'all'.
        type    May be 'manga'. Otherwise seems to list anime.
        """
        if not "u" in kwargs:
            raise KeyError
        defaults = dict(
            _url = "http://myanimelist.net/malappinfo.php",
            status = "all"
            )
        defaults.update(kwargs)
        return MAL.url(self, **defaults)

class Search(MAL):
    def __init__(self, query, typ = "anime"):
        typ = ("anime", "manga", "all").index(typ) + 1
        self._url = self.url(s = query, type = typ)

    def url(self, **kwargs):
        """
        Return search URL.
        
        s       Search term. Required.
    	type    1 for anime only (default), 2 for manga only, 3 for both.
        """
        if not "s" in kwargs:
            raise KeyError
        defaults = dict(
            _url = "http://myanimelist.net/includes/masearch.inc.php",
            # Need not be string.
            type = 1
            )
        defaults.update(kwargs)
        return MAL.url(self, **defaults)

    def request(self, **kwargs):
        """
        Return a modified request object.
        
        _url    Required argument.
        Referer Default.
        """
        # How it is called on the site.
        defaults = {"Referer": "http://myanimelist.net/addtolist.php"}
        defaults.update(kwargs)
        return MAL.request(self, **defaults)

class Login(MAL):
    def __init__(self, username, password):
        self._request = self.post(username = username, password = password)
        
    def url(self, **kwargs):
        """
        Return a login URL.
        """
        defaults = dict(_url = "http://myanimelist.net/login.php")
        defaults.update(kwargs)
        return MAL.url(self, **defaults)

    def post(self, **kwargs):
        """
        Return a request object.
        
        _request    Not required!
        username    Required.
        password    Required.
        cookie      How to track the session. Should be 1 (default)
        sublogin    The submit button used. Should be 'Login' (default)
        """
        if not "username" in kwargs or not "password" in kwargs:
            raise KeyError
        defaults = dict(
            _request = self.request(_url = self.url()),
            cookie = 1,
            sublogin = "Login"
            )
        defaults.update(kwargs)
        return MAL.post(self, **defaults)

class Panel(MAL):
    def __init__(self, anime):
        """
        Argument must conform to mal_anime_data_schema.
        """
        data = dict(
            _request = self.request(_url = self.url(id = anime["my_id"]))
            )
        # Map post arguments to input fields.
        schema = dict(
            series_animedb_id = "series_animedb_id",
            series_title = "series_animedb_id",
            completed_eps = "my_watched_episodes",
            status = "my_status",
            score = "my_score"
            )
        for to, von in schema.iteritems():
            data[to] = anime[von]
        self._request = self.post(**data)
        
    def url(self, **kwargs):
        """
        Return a panel URL.
        
        keepThis    Should be string 'true' (default)
        go          Which dialog to render. Irrelevant to us. Can be
                    'edit' (default), 'add' or 'addmanga'.
        id          User-relation id of a series. Required.
        hidenav     Whether to render a header. Irrelevant. Defaults to 1.
                    Probably also accepts string 'true'.
        TB_iframe   Whatever. Usually true on the site,
                    but we default to 'false'.
        """
        if not "id" in kwargs:
            raise KeyError
        defaults = dict(
            _url = "http://myanimelist.net/panel.php",
            keepThis = "true",
            go = "edit",
            hidenav = 1,
            TB_iframe = "false"
            )
        defaults.update(kwargs)
        return MAL.url(self, **defaults)

    def post(self, **kwargs):
        """
        Return a request object.
        
        close_on_update Probably sends back JavaScript to remove the panel.
                        Irrelevant, defaults to 'true'.
        submitIt        Which submit button was used. Defaults to 2.

        Arguments from the anime_data structure:
        
        series_animedb_id   Probably required, but we don't.
        series_title        For some reason the site sets this to the same
                            number as series_animedb_id, so if you don't pass
                            it explicitly we do that as well.
        completed_eps       Corresponds to my_watched_episodes.
                            We accept that as well.
        status              my_status. No shortcut yet.
        score               my_score
        """
        defaults = dict(
            submitIt = 2,
            close_on_update = "true"
            )
        if "series_animedb_id" in kwargs:
            defaults["series_title"] = kwargs["series_animedb_id"]
        if "my_watched_episodes" in kwargs:
            # Site doesn't know about our convenience.
            defaults["completed_eps"] = kwargs.pop("my_watched_episodes")
        # Overwrite explicit arguments.
        defaults.update(kwargs)
        return MAL.post(self, **defaults)
