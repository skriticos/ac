#! /usr/bin/env python

# Copyright (c) 2009 Sebastian Bartos
# See COPYING for details

"""
Creates html documentation pages in the doc dir of the source code using pydoc.

Note: plese don't commit the actual html files, as it leads to merging conflits.

Whishlist: add an index file or migrate to a real documentation generator.
"""

from os import path, system, mkdir

basedir = path.abspath(path.dirname(__file__))
srcdir = path.join(basedir, 'src')
docdir = path.join(basedir, 'doc', 'api')
moduledir = path.join(basedir, 'src', 'AniChou')

if not path.isdir(docdir):
	mkdir(docdir)

import os
os.chdir(docdir)
os.environ['PYTHONPATH'] = moduledir

modules = \
		['gtkctl', 'myanimelist', 'config', 'data', 'players', 'recognizinig',
		'globs', 'database']

for module in modules:
	os.system('pydoc -w ' + path.join(moduledir, module + '.py'))

