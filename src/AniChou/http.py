import urllib
import urllib2
import urlparse
import os

import preferences

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

class File(object):
    # Not subclassing Request because we do urlparse anyway.
    def __init__(self, url, folder = None):
        """
        Takes absolute path to an existing folder in which the file will be
        placed.
        Defaults to a cache structure read from preferences. Don't use that
        form as a general library function!
        """
        # We assume a lot. Strange addresses spell a horrible death.
        part = urlparse.urlparse(url)
        # If the following algorithm changes, the cache should be deleted.
        host = part.hostname
        # Some attributes default to None, others to the empty string.
        port = part.port or "80"
        # Remove leading slash.
        path = urllib.url2pathname(part.path[1:])
        path, name = os.path.split(path)
        if folder is None:
            # Don't pass a filename.
            folder = preferences.path("cache", host, port, path)
        # Now we have a nice local path.
    	self.target = os.path.join(folder, name)
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

# Convenience.
def download(url):
    r = File(url)
    # AniChou uses a wild mix of User-Agents...
    r.execute(urllib2.build_opener())
    for f in r:
        return f
