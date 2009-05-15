from __future__ import with_statement

import unittest
import urllib2
import test.test_urllib2
import os
import sys
import mimetools

class TestRemote(unittest.TestCase):
    def setUp(self):
        self.rem = AniChou.malcom.Remote()
        self.req = self.rem.request(_url = "http://www.google.com")

    def testUrl(self):
        self.assertRaises(KeyError, lambda: self.rem.url())
        self.assertEqual("http://www.google.com",
            self.rem.url(_url = "http://www.google.com"))
        self.assertEqual("http://www.google.com?q=AniChou", self.rem.url(
            _url = "http://www.google.com",
            q = "AniChou"
            ))

    def testRequest(self):
        self.assertRaises(KeyError, lambda: self.rem.request())
        # Capitalizes.
        self.assert_(self.req.has_header("User-agent"))
        self.assertEqual("http://www.google.com", self.req.get_full_url())

    def testPost(self):
        self.assertRaises(KeyError, lambda: self.rem.post())
        self.req = self.rem.post(_request = self.req)
        self.assert_(self.req.has_data())
        self.assertEqual("POST", self.req.get_method())

class TestList(unittest.TestCase):
    def setUp(self):
        self.rem = AniChou.malcom.List()

    def testUrl(self):
        self.assertRaises(KeyError, lambda: self.rem.url())
        # Dictionaries are unordered.
        self.assert_(self.rem.url(u = "Wile") in (
            "http://myanimelist.net/malappinfo.php?u=Wile&status=all",
            "http://myanimelist.net/malappinfo.php?status=all&u=Wile"
            ))

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
    unittest.main()
