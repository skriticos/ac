#!/opt/local/bin/python2.5
import unittest
import urllib2
import test.test_urllib2
import os
import sys
import mimetools
import gzip

class TestRequest(unittest.TestCase):
    def setUp(self):
        self.req = AniChou.malcom.Request(
            "http://www.google.com",
            dict(q = "AniChou"),
            dict(Referer = "http://myanimelist.net")
            )

    def testAttribute(self):
        req = self.req.request
        self.assertEqual("http://www.google.com?q=AniChou",
            req.get_full_url())
        self.assert_(req.has_header("Referer"))

    def testIter(self):
        self.assertRaises(AttributeError, lambda: list(self.req))

class TestMAL(unittest.TestCase):
    def setUp(self):
        self.req = AniChou.malcom.MAL("http://myanimelist.net", {}, {})

    def testRequest(self):
        # Capitalizes.
        self.assert_(self.req.request.has_header("User-agent"))

class TestList(unittest.TestCase):
    def setUp(self):
        self.req = AniChou.malcom.List(username = "Wile")

    def testUrl(self):
        # Dictionaries are unordered.
        self.assert_(self.req.request.get_full_url() in (
            "http://myanimelist.net/malappinfo.php?u=Wile&status=all",
            "http://myanimelist.net/malappinfo.php?status=all&u=Wile"
            ))

class TestListParsing(unittest.TestCase):
    def setUp(self):
        self.director = urllib2.build_opener(
            MockHTTPHandler("list.xml.gz"))
        self.request = AniChou.malcom.List(username = "crono22")

    def testIter(self):
        # Shouldn't raise. Should take time.
        self.request.execute(self.director)
        # Continue here to avoid new setUp.
        ac_remote_anime_dict = dict(self.request)
        self.assert_(len(ac_remote_anime_dict) > 3000)
        self.assertEqual(52,
            ac_remote_anime_dict["Jungle Emperor (1989)"]["series_episodes"])

class TestErrorAppInfo(unittest.TestCase):
    def setUp(self):
        self.director = urllib2.build_opener(
            MockHTTPHandler("invalid username.txt"))
        self.request = AniChou.malcom.List(username = "nobody")

    def testOpen(self):
        self.assertRaises(AniChou.malcom.UsernameError,
            lambda: self.request.execute(self.director))

class TestErrorLogin(unittest.TestCase):
    def setUp(self):
        self.director = urllib2.build_opener(
            MockHTTPHandler("bad username.txt"))
        self.request = AniChou.malcom.Login(username = "Wile",
            password = "helo")

    def testOpen(self):
        self.assertRaises(AniChou.malcom.UsernameError,
            lambda: self.request.execute(self.director))

class TestMissingLogin(unittest.TestCase):
    def setUp(self):
        self.director = urllib2.build_opener(
            MockHTTPHandler("must first login.txt"))
        self.request = AniChou.malcom.Add(0, 0, 0)

    def testOpen(self):
        self.assertRaises(AniChou.malcom.LoginError,
            lambda: self.request.execute(self.director))

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

if __name__ == '__main__':
    # Python sets cwd to where the module lives.
    sys.path.append(os.path.abspath("../src"))
    # Now we can.
    import AniChou.malcom
    unittest.main()
