#!/usr/bin/env python

from distutils.core import setup

setup(name='AnimeCollector',
      version='0.26',
      description='Open source GUI MAL Updater',
      author='Sebastian Bartos',
      author_email='seth.kriticos@googlemail.com',
      url='http://myanimelist.net/clubs.php?cid=10642',
      packages=['AnimeCollector'],
      package_dir={'AnimeCollector': 'src/AnimeCollector'},
      package_data={'AnimeCollector': ['data/*']},
      scripts=['src/animecollector']
      )

