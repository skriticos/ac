"""
Malcom communicates with MyAnimeList.
"""

import urllib
import urllib2
import urlparse
import re

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
        """
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
                It won't be touched. Required argument.
        xyz     Everything else is used as HTTP headers.
                Those are somewhat case-sensitive.
                
        Defaults include User-Agent. Referer is recommended.
        """
        # Raises KeyError.
        tmpl = kwargs.pop("_url")
        head = {"User-Agent": "AniChou"}
        head.update(kwargs)
    	# BTW has_header is case-sensitive.
    	return urllib2.Request(tmpl, headers = head)

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
        
class List(Remote):
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
        return Remote.url(self, **defaults)

class Search(Remote):
    def url(self, **kwargs):
        """
        Return search URL.
        
    	type    1 for anime only (default), 2 for manga only, 3 for both.
        """
        defaults = dict(
            _url = "http://myanimelist.net/includes/masearch.inc.php",
            # Need not be string.
            type = 1
            )
        defaults.update(kwargs)
        return Remote.url(self, **defaults)

    def request(self, **kwargs):
        """
        Return a modified request object.
        
        _url    Required argument.
        Referer Default.
        """
        # How it is called on the site.
        defaults = {"Referer": "http://myanimelist.net/addtolist.php"}
        defaults.update(kwargs)
        return Remote.request(self, **defaults)

class Login(Remote):
    def url(self, **kwargs):
        """
        Return a login URL.
        """
        defaults = dict(_url = "http://myanimelist.net/login.php")
        defaults.update(kwargs)
        return Remote.url(self, **defaults)

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
        return Remote.post(self, **defaults)

class Panel(Remote):
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
        return Remote.url(self, **defaults)

    def post(self, **kwargs):
        """
        Return a request object.
        
        _request        Not required!
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
            _request = self.request(_url = self.url()),
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
        return Remote.post(self, **defaults)
