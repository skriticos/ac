"""
Malcom communicates with MyAnimeList.
"""

class Request(object):
    """
    A client for part of a server.
    
    Most methods use keyword arguments even for required information so that
    subclasses can provide defaults.
    """

    # In-memory only.
    cj = cookielib.CookieJar()
    parser = urllib2.HTTPCookieProcessor(cj)
    net = urllib2.OpenerDirector()
    net.add_handler(parse)
    # Use net.open instead of urlopen.
    urllib2.install_opener(net)

    def url(self, **kwargs):
        """
        Return a URL string.
        
        _url    A full URL with scheme and path. Query strings, if present,
                are discarded. Required argument.
        xyz     Everything else is used to build a query string.
        """
        pass

    def request(self, **kwargs):
        """
        Return a request object.
        
        _url    A full URL which may contain a query string.
                It won't be touched. Required argument.
        xyz     Everything else is used as HTTP headers.
                Those are somewhat case-sensitive.
        """
        pass
        
    def post(self, **kwargs):
        """
        Return a modified request object.
        
        _request    A request object complete with headers.
        xyz         Everything else is added as form-urlencoded data,
                    turning the request from GET into POST.
        """
        pass
        
    def open(self, _request):
        """
        Execute a request (object).
        
        This is essentially urlopen().
        """
        pass