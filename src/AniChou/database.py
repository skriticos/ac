# =========================================================================== #
# Name:     database.py
# Purpose:  Read and write to the local database
#  
# Copyright (c) 2009 Daniel Anderson - dankles/evilsage4
#
# License: GPL v3, see COPYING file for details
# =========================================================================== #

from os import path

from sqlalchemy import *

from globs import ac_data_path

class db(object):
    """
    Database module. Reads and writes to local database.
    
    """
    def __init__(self):
        if not path.isfile(ac_data_path):
            _create_table()


    def set_db(self, d):
        """ takes a dictionary object to store into the DB
        """
        _drop_table()
        _create_table()
        dbstring = create_engine('sqlite:///' + ac_data_path)
        metadata = MetaData(dbstring)
        table_mal = Table('myanimelist', metadata, autoload=True)
        
        i = table_mal.insert()
        for x in d.keys():
            i.execute(d[x])
        
        
    def get_db(self):
        """ Returns a Dictionary Object of the local DB
        """
        dbstring = create_engine('sqlite:///' + ac_data_path)
        metadata = MetaData(dbstring)
        table_mal = Table('myanimelist', metadata, autoload=True)
        s = table_mal.select()
        rs = s.execute()
        d = {}
        for row in rs:
            test_dict = dict(row)
            d[row['series_title']] = test_dict
        
        
        return d

def _create_table():
    """ setup the table
    """
    dbstring = create_engine('sqlite:///' + ac_data_path)
    metadata = MetaData(dbstring)
    table_mal = Table('myanimelist', metadata,
                       Column('series_animedb_id', Integer),
                       Column(u'series_title', Unicode),
                       Column(u'series_synonyms', Unicode),
                       Column('series_type', Integer),
                       Column('series_episodes', Integer),
                       Column('series_status', Integer),
                       Column(u'series_start', Date),
                       Column(u'series_end', Date),
                       Column(u'series_image', Unicode),
                       Column('my_id', Integer),
                       Column('my_watched_episodes', Integer),
                       Column(u'my_start_date', Date),
                       Column(u'my_finish_date', Date),
                       Column('my_score', Integer),
                       Column('my_status', Integer),
                       Column('my_rewatching', Integer),
                       Column('my_rewatching_ep', Integer),
                       Column(u'my_last_updated', DateTime),
                     )
    table_mal.create()

def _drop_table():
    """ Drop the table
    """
    dbstring = create_engine('sqlite:///' + ac_data_path)
    metadata = MetaData(dbstring)
    table_mal = Table('myanimelist', metadata, autoload=True)
    table_mal.drop()

