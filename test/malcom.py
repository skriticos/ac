import unittest
import urllib2
import os
import sys
import datetime
import tempfile
import shutil
# Python sets cwd to where the module lives.
sys.path.append(os.path.abspath("../src"))
# Now we can.
import AniChou.malcom
from AniChou.testing import MockHTTPHandler

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

class TestSearchBadchar(unittest.TestCase):
    def setUp(self):
        self.director = urllib2.build_opener(
            MockHTTPHandler("search result jungle.txt"))
        self.request = AniChou.malcom.Search("Jungle")

    def testIter(self):
        self.request.execute(self.director)
        kimba = filter(lambda n: n["series_animedb_id"] == 2556,
            self.request)
        self.assertEqual(1, len(kimba))
        self.assert_("series_synonyms" in kimba[0])

class TestSearchUnicode(unittest.TestCase):
    def setUp(self):
        self.director = urllib2.build_opener(
            MockHTTPHandler("search result holic.txt"))
        self.request = AniChou.malcom.Search("Holic")

    def testIter(self):
        self.request.execute(self.director)
        found = filter(lambda n: n["series_animedb_id"] == 5030,
            self.request)
        self.assertEqual(1, len(found))
        self.assertEqual(u'Maria\u2020Holic', found[0]["series_title"])

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
        self.assertEqual("Maria+Holic; Maria Holic; MariaHolic",
            # unicode().encode('utf-8').__repr__()
            ac_remote_anime_dict['Maria\xe2\x80\xa0Holic']["series_synonyms"])
        self.assertEqual(datetime.date(2008, 10, 18),
            ac_remote_anime_dict["Hell's Angels"]["series_start"])
            
class TestErrorAppInfo(unittest.TestCase):
    def setUp(self):
        self.director = urllib2.build_opener(
            MockHTTPHandler("invalid username.txt"))
        self.request = AniChou.malcom.List(username = ">.<")

    def testOpen(self):
        self.assertRaises(AniChou.malcom.UsernameError,
            lambda: self.request.execute(self.director))

class TestErrorLogin(unittest.TestCase):
    def setUp(self):
        self.director = urllib2.build_opener(
            MockHTTPHandler("bad username.txt"))
        self.request = AniChou.malcom.Login(username = ">.<",
            password = "helo")

    def testOpen(self):
        self.assertRaises(AniChou.malcom.UsernameError,
            lambda: self.request.execute(self.director))

class TestMissingLogin(unittest.TestCase):
    def setUp(self):
        self.director = urllib2.build_opener(
            MockHTTPHandler("must first login.txt"))
        anime = dict(
            my_id = 0,
            series_animedb_id = 0,
            my_watched_episodes = 0,
            my_status = 0,
            my_score = 0
            )
        self.request = AniChou.malcom.Panel(anime)

    def testOpen(self):
        self.assertRaises(AniChou.malcom.LoginError,
            lambda: self.request.execute(self.director))

class TestImage(unittest.TestCase):
    def setUp(self):
        self.cache = tempfile.mkdtemp()
        self.url = "http://cdn.myanimelist.net/images/anime/12/3335.jpg"
        self.director = urllib2.build_opener(
            MockHTTPHandler("image.bin"))
        self.request = AniChou.malcom.Image(self.url, self.cache)

    def testDouble(self):
        self.request.execute(self.director)
        locl = iter(self.request).next()
        self.assertEqual(os.path.getsize(locl), 28159)
        # From cache.
        req = AniChou.malcom.Image(self.url, self.cache)
        # Opener shouldn't be used anyway.
        req.execute(None)
        self.assertEqual(iter(req).next(), locl)

    def tearDown(self):
        shutil.rmtree(self.cache)

# Comment this in to override the mock setup and test against the live site.
#class MockHTTPHandler(urllib2.HTTPHandler):
#    pass

if __name__ == '__main__':
    # Exclude lengthy tests when working on something else.
    unittest.main(
#       defaultTest = "TestImage"
        )
