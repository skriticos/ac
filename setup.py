#!/usr/bin/env python

from distutils.core import setup

setup(name='AniChou',
      version='9.1.6-beta',
      description='Open anime/manga updater',
      author='AniChou group - see AUTHORS file',
      url='http://myanimelist.net/clubs.php?cid=10642',
      packages=['AniChou'],
      package_dir={'AniChou': 'src/AniChou'},
      package_data={'AniChou': ['data/*']},
      scripts=['src/anichou.py']
      )

