import sys
import urllib2
import unittest
import os

# The library.
sys.path.append(os.path.abspath("../src"))
import AniChou.malcom
from AniChou import fulltext
from AniChou.testing import MockHTTPHandler

class TestSplitting(unittest.TestCase):
    def testHarvest(self):
        t = [
            # Colon.
            ("Mei to Konekobasu", "Mei to Koneko Bus; Mei and the Kitten Bus",
            ["Mei to Koneko Bus", "Mei and the Kitten Bus", "Mei to Konekobasu"]),
            # None.
            ("Hikaru no Go: New Year Special", None,
            ["Hikaru no Go: New Year Special"]),
            # Empty.
            ("Fumoon", "",
            ["Fumoon"]),
            # Single.
            ("Super Kuma-san", "Mr. Super Bear",
            ["Mr. Super Bear", "Super Kuma-san", ]),
            # Trailing.
            ("Tales of Symphonia - Kratos Sensei no Private Lesson", "Professor Kratos's Private Lesson;",
            ["Professor Kratos's Private Lesson", "Tales of Symphonia - Kratos Sensei no Private Lesson"]),
            # No space colon.
            ("Raimuiro Senkitan ~Southern Romance Story~", "Lime Iro Senkitan Nankoku Yume Roman;Lime-iro Senkitan: The South Island Dream Romantic Adventure (OAV)",
            ["Lime Iro Senkitan Nankoku Yume Roman", "Lime-iro Senkitan: The South Island Dream Romantic Adventure (OAV)", "Raimuiro Senkitan ~Southern Romance Story~"]),
            # No space comma
            ("Sakura Strasse", "Sakura Street,Cherry Blossom Street",
            ["Sakura Street", "Cherry Blossom Street", "Sakura Strasse"]),
            # Mixed colon.
            ("Umi no Yami, Tsuki no Kage", "Darkness of the Sea, Shadow of the Moon; Umi-Yami",
            ["Darkness of the Sea, Shadow of the Moon", "Umi-Yami", "Umi no Yami, Tsuki no Kage"]),
            # Mixed impossible.
            ("Clannad: Another World, Kyou Chapter", "Clannad: Another World, Kyou Arc; Clannad: Mo hitotsu no sekai, Kyou-hen, Clannad ~ Kyou Edition, Clannad~ After Story~ DVD Special, Clannad~ After Story~ DVD OVA; Kyou, Another World",
            ["Clannad: Another World, Kyou Arc", "Clannad: Mo hitotsu no sekai, Kyou-hen, Clannad ~ Kyou Edition, Clannad~ After Story~ DVD Special, Clannad~ After Story~ DVD OVA", "Kyou, Another World", "Clannad: Another World, Kyou Chapter"])
            ]
        for title, syn, split in t:
            anime = dict(series_title = title)
            if syn:
                # Don't add empty values.
                # In reality the key isn't there, either.
                anime["series_synonyms"] = syn
            self.assertEqual(split, AniChou.malcom.harvest(anime))
        
class TestIndexing(unittest.TestCase):
    def setUp(self):
        self.director = urllib2.build_opener(MockHTTPHandler("list.xml.gz"))
        self.request = AniChou.malcom.List(username = "crono22")
        self.db = fulltext.Index()

    def testAdd(self):
        self.request.execute(self.director)
        for key, anime in self.request:
            titles = AniChou.malcom.harvest(anime)
            self.db.add(anime["series_animedb_id"], *titles)
        self.db.save()
        self.assertTrue(self.db.has_series(2494))
        self.assertTrue(self.db.has_title("Sakura Street"))

if __name__ == '__main__':

    # Exclude lengthy tests when working on something else.
    unittest.main(
#       defaultTest = "TestSplitting"
        )
