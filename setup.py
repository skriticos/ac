#!/usr/bin/env python

from distutils.core import setup

setup(name='AnimeCollector',
      version='9.1-unstable',
      description='Open source GUI MAL Updater',
      author='AnimeCollector group - see AUTHORS file',
      url='http://myanimelist.net/clubs.php?cid=10642',
      packages=['AnimeCollector'],
      package_dir={'AnimeCollector': 'src/AnimeCollector'},
      package_data={'AnimeCollector': ['data/*']},
      scripts=['src/animecollector.py']
      )

