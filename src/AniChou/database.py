# =========================================================================== #
# Name:     database.py
# Purpose:  Read and write to the local database
#  
# Copyright (c) 2009 Daniel Anderson - dankles/evilsage4
#
# License: GPL v3, see COPYING file for details
# =========================================================================== #

import cPickle
from os import path
from globs import ac_data_path

class db(object):
    """
    Database module. Reads and writes to local database.
    
    """
    def __init__(self):
        self.local_db = {}
        if path.isfile(ac_data_path):
            db_handle = open(ac_data_path, 'rb')
            self.local_db = cPickle.load(db_handle)
            db_handle.close()
            
    def set_db(self, data):
        """ takes a dictionary object to store into the DB
        """
        db_handle = open(ac_data_path, 'wb')
        cPickle.dump(data, db_handle)
        db_handle.close()
        
        
    def get_db(self):
        return self.local_db