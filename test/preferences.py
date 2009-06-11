import unittest
import sys
import os.path

sys.path.append(os.path.abspath("../src"))
from AniChou import preferences
from AniChou.KeyValueCoding import *

class TestStack(unittest.TestCase):
    def setUp(self):
        sys.argv.extend([
            "-preferences", "preferences.plist"
            ])
        self.config = preferences.Defaults()
        
    def testDomain(self):
        # In reality accounts would be an array.
        self.assertEqual("myal", getKeyPath(self.config, "accounts.site"))

    def testAdd(self):
        self.config["hello"] = "world"
        self.assertEqual("world", getKey(self.config, "hello"))

if __name__ == '__main__':

    unittest.main()
