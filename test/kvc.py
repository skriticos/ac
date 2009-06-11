import sys
import os
import unittest

sys.path.append(os.path.abspath("../src"))

from AniChou.KeyValueCoding import *

class Preferences(object):
    first = 1
    second = dict(third = 3, fifth = [])

    def fourth(self):
        return 4

    def getSixth(self):
        return 6

class TestGet(unittest.TestCase):
    def setUp(self):
        self.pref = Preferences()
        
    def testAttribute(self):
        self.assertEqual(1, getKey(self.pref, "first"))
        section = getKey(self.pref, "second")
        self.assert_(isinstance(section, dict))
        self.assertEqual(3, getKey(section, "third"))

    def testCallable(self):
        self.assertEqual(4, getKey(self.pref, "fourth"))

    def testAccessor(self):
        self.assertEqual(6, getKey(self.pref, "sixth"))

    def testPath(self):
        self.assertEqual(3, getKeyPath(self.pref, "second.third"))

class TestSet(unittest.TestCase):
    def setUp(self):
        self.pref = Preferences()
        
    def testPath(self):
        # No setting dict entries.
        self.assertRaises(KeyError, lambda:
            setKeyPath(self.pref, "second.third", "three"))

if __name__ == '__main__':
    unittest.main()
