import sys
import os.path
import distutils.dir_util
import platform
# Needs 2.6
# Could just as well use json, but this way *I* have a nice editor ;)
import plistlib

from wx.lib.pubsub import Publisher

from KeyValueCoding import *
from pattern import Borg

def path(domain, *folders):
    d = Defaults()
    # Will raise for unsupported domains.
    domain = dict(
        data    = d["support"],
        # No dedicated subfolder for now.
        sites   = d["support"],
        cache   = d["caches"],
        )[domain]
    domain = os.path.abspath(os.path.expanduser(domain))
    path = os.path.join(domain, *folders)
	# Create missing ancestors.
    distutils.dir_util.mkpath(path)
    return path

def interpret(string):
    """
    Convert a string into a boolean or integer, or return unchanged.
    """
    text = string.lower()
    if text in ("no", "false"):
        return False
    elif text in ("yes", "true"):
        return True
    try:
        return int(text)
    except ValueError:
        return string

class Switches(dict):
    def __init__(self, argv = sys.argv):
        """
        Silently ignores switches without value!
        """
        dict.__init__(self)
        t = iter(argv)
        script = t.next()
        while True:
            try:
                option = t.next()[1:]
                value  = t.next()
            except StopIteration:
                break
            self[option] = interpret(value)

def Registration(system = platform.system()):
    posix = dict(
        preferences = "~/.anichou/config.xml",
        caches      = "~/.anichou/cache",
        support     = "~/.anichou",
        )
    mac = dict(
        preferences = "~/Library/Preferences/com.github.skriticos.anichou.plist",
        caches      = "~/Library/Caches/AniChou",
        support     = "~/Library/Application Support/AniChou",
        )
    all = dict(
        sites       = {},
        accounts    = [],
        )
    sys = dict(
        Darwin      = mac,
        )
    ret = sys.get(system, posix)
    ret.update(all)
    return ret
        

class File(dict):
    def read(self, fname):
        try:
            self.update(plistlib.readPlist(fname))
        except IOError:
            # No such file?
            pass

    def write(self, fname):
        plistlib.writePlist(self, fname)

class Defaults(Borg):
    def __init__(self):
        plist = File()
        self.stack = [Switches(), plist, Registration()]
        plist.read(self.preferences())
        Publisher().subscribe(self.save, "save")

    def save(self, message = None):
        self.stack[1].write(self.preferences())

    def preferences(self):
        return os.path.expanduser(self["preferences"])

    def __getitem__(self, key):
        """
        Changes made to returned items do not always persist.
        Don't forget to explicitly set them!
        """
        for d in self.stack:
            if key in d:
                return d[key]
        raise KeyError

    def __setitem__(self, key, value):
        self.stack[1][key] = value

import unittest

class TestInterpret(unittest.TestCase):
    def testMultiple(self):
        t = dict(
            # Bool.
            True = True,
            true = True,
            yes = True,
            No = False,
            # String.
            hello = "hello"
            )
        # Integer.
        t["2"] = 2
        for arg, value in t.iteritems():
            self.assertEqual(value, interpret(arg))

class TestSwitches(unittest.TestCase):
    def setUp(self):
        self.domain = Switches([None,
            "-config", "file",
            "-track", "yes",
            "-some.path", "5",
            ])
        
    def testDomain(self):
        self.assertEqual("file", getKey(self.domain, "config"))
        self.assertEqual(True, getKey(self.domain, "track"))
        # No actual paths.
        self.assertEqual(5, getKey(self.domain, "some.path"))

    def testError(self):
        self.assertRaises(KeyError, lambda: getKey(self.domain, "foo"))

class TestDefaults(unittest.TestCase):
    def setUp(self):
        self.domain = Registration("Darwin")
        
    def testValue(self):
        self.assertEqual("~/Library/Caches/AniChou",
            getKey(self.domain, "caches"))

    def testFallback(self):
        domain = Registration("Foo")
        self.assertEqual("~/.anichou", getKey(domain, "support"))

if __name__ == '__main__':
    unittest.main()
