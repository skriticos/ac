import gzip
import urllib2
import test.test_urllib2
import os.path
import mimetools

class MockHTTPHandler(urllib2.HTTPHandler):
    """
    Has 'server' return contents of local file.
    
    These should be full protocol dumps, e.g. created with `curl -i`.
    """

    def __init__(self, path):
        # Get rid of tilde.
        path = os.path.expanduser(path)
        # Definitely have it start in slash.
        self.path = os.path.abspath(path)

    def http_open(self, req):
        # Too lazy for os.path.
        if self.path[-3:] == ".gz":
            f = gzip.open(self.path)
        else:
            f = open(self.path)
        # Discard first line.
        http = f.readline()
        # Parse header.
        msg = mimetools.Message(f)
        # Retain content.
        body = f.read()
        f.close()
        return test.test_urllib2.MockResponse(200, "OK", msg, body,
            req.get_full_url())
