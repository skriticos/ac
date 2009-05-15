from __future__ import with_statement

import unittest
import urllib2
import test.test_urllib2
import os
import sys
import mimetools

class MockHTTPHandler(urllib2.BaseHandler):
    """
    Has 'server' return contents of local file.
    """

    def __init__(self, path):
        """
        Accepts about any file system path format.
        """
        # Get rid of tilde.
        path = os.path.expanduser(path)
        # Definetly have it start in slash.
        self.path = os.path.abspath(path)

    def http_open(self, req):
        with open(self.path, "r") as f:
            msg = mimetools.Message(f)
            body = f.read()
        return test.test_urllib2.MockResponse(200, body, msg, "",
            req.get_full_url())

if __name__ == '__main__':
    # Python sets cwd to where the module lives.
    sys.path.append(os.path.abspath("../src"))
    # Now we can.
    import AniChou.malcom
    # Constant.
    TESTS = []
    # HTTP dumps.
    for f in ["bad username.txt", "must first login.txt",
        "invalid username.txt"]:
        TESTS.append(os.path.abspath(f))
