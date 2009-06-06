import sqlite3
import os.path
import re
import difflib
import operator

def tokenize(string):
    """
    Return array of words extracted from string.
    """
    return re.sub(r'\W', ' ', string.lower()).split()

def _add_title(cursor, series, title):
    """
    Does not check for duplicates!
    """
    cursor.execute(
        "INSERT INTO title(series, string) VALUES(?, ?)",
        (series, title))
    tid = cursor.lastrowid
    for pos, word in enumerate(tokenize(title)):
        _add_word(cursor, tid, pos, word)

def _add_word(cursor, title, position, word):
    """
    Takes a title id and a word string.
    Inserts word if not already present.

    Does not check whether title already has word in this position!
    """
    try:
        cursor.execute("SELECT id FROM word WHERE string=?", (word,))
        wid = cursor.fetchone()[0]
    except TypeError:
        cursor.execute("INSERT INTO word(string) VALUES(?)", (word,))
        wid = cursor.lastrowid
    cursor.execute("INSERT INTO contains(title, position, word)\
        VALUES(?, ?, ?)", (title, position, wid))

class Index(object):
    def __init__(self, fname = ":memory:"):
        """
        Takes a file name. Will be created if necessary.
        """
        self.db = sqlite3.connect(fname)
        # No foreign key clauses as we don't delete anyway.
        # No indexes as unique should create one.
        self.db.executescript("""
        CREATE TABLE IF NOT EXISTS title (
            id INTEGER PRIMARY KEY,
            string TEXT,
            series INTEGER
        );
        CREATE TABLE IF NOT EXISTS word (
            id INTEGER PRIMARY KEY,
            string TEXT UNIQUE
        );
        CREATE TABLE IF NOT EXISTS contains (
            title INTEGER,
            position INTEGER,
            word INTEGER
        );
        """)

    def add(self, series, *titles):
        """
        Assign titles to a series id.
        
        Does not check for duplicates!
        
        Titles will be inserted literally, so strip beforehand.
        
        Does not commit because file access takes time. Remember to call save.
        """
        for title in titles:
            _add_title(self.db.cursor(), series, title)
        
    def save(self):
        self.db.commit()

    def has_series(self, series):
        """
        None if nothing added yet. Otherwise some true value.
        """
        return self.db.execute("SELECT id FROM title WHERE series=?",
            (series,)).fetchone()

    def has_entry(self, series, title):
        return self.db.execute(
            "SELECT id FROM title WHERE series=? AND string=?",
            (series, title)).fetchone()

    def has_title(self, title):
        """
        Return False or id of one series with exactly this title.

        Which one is not defined. Titles are not unique!
        """
        c = self.db.execute("SELECT series FROM title WHERE string=?",
            (title,)
            )
        try:
            return c.fetchone()[0]
        except TypeError:
            return False

    def search(self, title):
        """
        Returns a list of possible matches.
        
        The first element of each is match quality as float 0 to 1 (best).
        Followed by matching title string and series id.
        
        Does not take shortcuts, so try has_title first.
        """
        words = tokenize(title)
        # Bad last comma.
        place = "?," * len(words)
        # Joooin.
        # TODO pass c threshold relative to len.
        query = """
            SELECT count(DISTINCT r.word) AS c, t.string, t.series \
            FROM title AS t, contains AS r, word AS w \
            WHERE t.id = r.title AND r.word = w.id AND w.string IN (%s) \
            GROUP BY r.title ORDER BY c DESC;
            """  % place[:-1]
        results = []
        for row in self.db.execute(query, words):
            # row is a tuple!
            try:
                # Only process the best matches.
                if row[0] != group:
                    break
            except NameError:
                group = row[0]
            # Better measurement.
            ratio = difflib.SequenceMatcher(None, title, row[1]).ratio()
            results.append((ratio,) + row[1:])
        results.sort(key = operator.itemgetter(0), reverse = True)
        return results

import unittest
import tempfile
import os

class TestTokenize(unittest.TestCase):
    def testMany(self):
        t = [
            # Empty.
            ("", []),
            # Words.
            ("Mazinger Z", ["mazinger", "z"]),
            # Whitespace.
            ("  A  B  ", ["a", "b"]),
            # Dash.
            ("Sazae-san", ["sazae", "san"]),
            # Under.
            ("dot_Hack", ["dot_hack"]),
            # Junk.
            (".hack/liminality", ["hack", "liminality"])
            ]
        for title, words in t:
            self.assertEqual(words, tokenize(title))

def _add(self):
    t = [
        "Mazinger Z",
        "Majinga Z",
        "Mazinga Z",
        "Mazinger Zed",
        "Shin Mazinga"
        ]
    self.i.add(1, t[0])
    self.i.add(1, t[1], t[2])
    self.i.add(1, *t[3:5])

class TestSearch(unittest.TestCase):
    def setUp(self):
        # Evil hack.
        self.i = Index()
        _add(self)
        
    def testRetrieve(self):
        self.assertEqual(1, len(self.i.search("Shin Mazinger Z")))

    def testShortcut(self):
        self.assertFalse(self.i.has_title("Bobobo"))
        self.assertEqual(1, self.i.has_title("Mazinger Zed"))

class TestCreate(unittest.TestCase):
    def setUp(self):
        handle = tempfile.NamedTemporaryFile(delete = False)
        handle.close()
        self.file = handle.name
        self.i = Index(self.file)

    def testEmpty(self):
        self.assertFalse(self.i.has_series(1))

    def testAdd(self):
        _add(self)
        self.assertTrue(self.i.has_series(1))

    def testStore(self):
        self.assertFalse(self.i.has_series(1))
        self.i.add(1, "Dangaioh")
        self.assertTrue(self.i.has_series(1))
        self.i.save()
        j = Index(self.file)
        self.assertTrue(j.has_series(1))

    def tearDown(self):
        os.remove(self.file)

if __name__ == '__main__':
    unittest.main()
