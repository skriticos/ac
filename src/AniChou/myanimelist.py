# =========================================================================== #
# Name:    myanimelist.py
# Purpose: Provide an interface to anime data; syncronize with the MyAnimeList
#          server;
#
# Copyright (c) 2008 Gareth Latty
# Copyright (c) 2009 Sebastian Bartos
# Copyright (c) 2009 Daniel Anderson - dankles/evilsage4
#
# License: GPL v3, see COPYING file for details
# =========================================================================== #

import urllib
import urllib2
from cookielib import LWPCookieJar
import socket
from xml.dom.minidom import parseString
from datetime import date, datetime
import os, time

from data import mal_data_schema
from database import db as local_database
from globs import ac_log_path, ac_data_path

class anime_data(object):
    """
    Anime data module. Reads and writes local anime data to disk, fetches and
    syncs with MyanimeList server.

    username: login username
    password: login password
    db_path: path to database
    db: local anime database that is a nested dict and has ASCII-fied series
        titles as keys and and fields form mal_data_schema as dict data.
    """

    def __init__(self, username='', password='',initsync=False):
        """
        Setup credentials, read local data and setup network connection
        environment. Optionally sync with MAL on startup.
        """
        
        # pull the local DB as a dictionary object
        #self.db = {}
        self.local_db = local_database()
        self.db = self.local_db.get_db()
        
        self.username = username
        self.password = password
        
        # setup cookie handler
        opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(LWPCookieJar()))
        urllib2.install_opener(opener)

        socket.setdefaulttimeout(40)
        if initsync:
            self.sync()

    def save(self):
        """ Only saves the current state to disk w/o network activity.
        """
        self.local_db.set_db(self.db)
        
    def sync(self):
        """
        Syncronize local anime database with the MyAnimeList server.
        (fetch -> compare -> push -> update local)

        Return:
        nested dict of remote updates with ASCII-fied series titles as
        keys and a list of keys that got deleted on the MyAnimeList server.
        """
        if _login(self.username,self.password):
            remoteAnime_db = _getAnimeList(self.username)
            if self.db:
                # If local DB is already initialized then filter changes 
                # and push local updates
                (remote_updates, local_updates, deleted_entry_keys) = \
                    _filter_sync_changes(remoteAnime_db, self.db)
                _logchanges(remote_updates, local_updates, deleted_entry_keys)
                _push_list(local_updates)

                # update local anime list with changes
                for key in deleted_entry_keys:
                    del self.db[deleted_entry_keys]
                for key, value in remote_updates.items():
                    self.db[key] = value
                
                # write to local DB
                self.local_db.set_db(self.db)
                
                return (remote_updates, deleted_entry_keys)
            else:
                # initialize local data, as it was empty before 
                self.db = remoteAnime_db
                
                # write to local DB
                self.local_db.set_db(self.db)
                
                return (self.db, {})
        else:
            print 'Login failed..'
            return False
 
        
    def fetch(self):
        """
        Only fetch anime data from MyAnimeList server (overwrites local data,
        if existent). Useful for initializing and resetting local database.

        Returns a copy of the fetched database on success, None on failure.
        """
        if _login(self.username, self.password):
            self.db = _getAnimeList(self.username)
            
            # write to local DB
            self.local_db.set_db(self.db)
            
            return self.db    

def _getAnimeList(username):
    """
    Retrive Anime XML from MyAnimeList server.
    
    return: dictionary object
    """

    fetch_base_url = 'http://myanimelist.net/malappinfo.php'
    fetch_request_data = urllib.urlencode({
        'status': 'all',
        'u': username})
    fetch_url = fetch_base_url + '?' + fetch_request_data

    # read the server xml file and do preliminary spacer sanitation for parsing
    fetch_response = \
          unicode(urllib2.urlopen(fetch_url).read(), 'utf-8', 'replace')
    fetch_response = fetch_response.strip()
    # phrase data and extract anime entry nodes
    xmldata = parseString(fetch_response)
    anime_nodes = xmldata.getElementsByTagName('anime')

    # walk through all the anime nodes and convert the data to a python
    # dictionary
    ac_remote_anime_dict = dict()
    for anime in anime_nodes:
        ac_node = dict()
        for node in anime.childNodes:
            # tags and empty nodes are excluded for the time being
            if not node.childNodes or node.nodeName == u'my_tags':
                node.unlink()
            else:
                # process my_last_updated unix timestamp
                if mal_data_schema[node.nodeName] is datetime:
                    ac_node[node.nodeName] = \
                        datetime.fromtimestamp(int(node.firstChild.nodeValue))
                # process integer slots
                elif mal_data_schema[node.nodeName] is int:
                    ac_node[node.nodeName] = int(node.firstChild.nodeValue)
                # proces date slots
                elif mal_data_schema[node.nodeName] is date:
                    if node.firstChild.nodeValue != '0000-00-00':
                        (y,m,d) = node.firstChild.nodeValue.split('-')
                        (y,m,d) = int(y), int(m), int(d)
                        if y and m and d:
                            ac_node[node.nodeName] = date(y,m,d)
                # process string slots
                else:
                    ac_node[node.nodeName] = node.firstChild.nodeValue

        # series titles are used as anime identifiers
        # the keys for the resulting dictionary are encoded to ASCII, so they
        # can be simply put into shelves
        key = ac_node['series_title'].encode('utf-8')

        # add node entry to the resulting nodelist
        ac_remote_anime_dict[key] = ac_node

    # the resulting dict is like this:
    # {<ASCII-fied key from title>: {<mal_data_schema-fields>: <values>}, ...}
    return ac_remote_anime_dict

def _getMangaList(username):
    """
    UN-USED 
    Retrive Manga XML from MyAnimeList server.
    
    return: Raw XML
    """

    fetch_base_url = 'http://myanimelist.net/malappinfo.php'
    fetch_request_data = urllib.urlencode({
        'status': 'all',
        'u': username,
        'type': 'manga'})
    fetch_url = fetch_base_url + '?' + fetch_request_data

    # read the server xml file and do preliminary spacer sanitation for parsing
    fetch_response = urllib2.urlopen(fetch_url).read()
    fetch_response = fetch_response.replace('\n', '').replace('\t', '')
    return fetch_response

def _logchanges(remote, local, deleted):
    """ Writes changes to logfile.
    """
    f = open(ac_log_path, 'a')
    now = str(int(time.mktime(datetime.now().timetuple())))
    for key, value in remote.items():
        f.write(now + ': Fetching "' + key + 
                '" episode ' + str(value['my_watched_episodes']) + '\n')
    for key, value in local.items():
        f.write(now + ': Pushing "' + key + 
                '" episode ' + str(value['my_watched_episodes']) + '\n')
    for entry in deleted:
        f.write(now + ': Deleted "' + entry + '"\n')
    f.close()
       
def _login(username, password):
    """
    Log in to MyAnimeList server.
    Returns: True on success, False on failure
    """

    # prepare login data
    login_base_url = 'http://myanimelist.net/login.php'

    headers = {
        'User-Agent': 'anichou',
        'Content-Type': 'application/x-www-form-urlencoded'}

    login_data = urllib.urlencode({
            'username': username,
            'password': password,
            'cookie': 1,
            'sublogin': 'Login'})

    # phrase login request (to perform a POST request)
    login_request = urllib2.Request(login_base_url, login_data, headers)

    # try to connect and authenticate with MyAnimeList server
    try:
        login_response = urllib2.urlopen(login_request).read()
    except urllib2.URLError, e:
        if hasattr(e, 'reason'):
            print 'Failed to reach myanimelist.net.'
            print 'Reason: ', e.reason
        elif hasattr(e, 'code'):
            print 'The server couldn\'t fulfill the request.'
            print 'Error code: ', e.code
        return False

    # check if login was successful
    if not login_response.count('<div class="badresult">'):
        return True
    else:
        return False

    
def _filter_sync_changes(ac_remote_anime_dict, ac_local_anime_dict):
    """
    Private Method
    Compares the anime entry my_last_updated in both parameters and returns two
    dictionaries of changed values of both parameters.

    The one for the local dictionary can be used to push changes to the mal
    server while the other can be used to update the local display and database.

    Returns:
        remote_updates: changes that are more up to date on the server
        local_updates: changes that are more up to date locally
        deleted_enry_keys: keys that are in the local database, but not in the
                           remote list.
    """
    remote_updates = dict()
    local_updates = dict()

    # search for entirely new enries and deleted entries
    remote_keys = ac_remote_anime_dict.keys()
    local_keys = ac_local_anime_dict.keys()
    
    deleted_entry_keys = \
        filter(lambda x:x not in remote_keys, local_keys)
    
    new_entry_keys = \
        filter(lambda x:x not in local_keys, remote_keys)
    for key in new_entry_keys:
        remote_updates[key] = ac_remote_anime_dict[key]

    # search in both dictionaries for differing update keys and append to the
    # other's updates depending on which key is newer
    common_keys = filter(lambda x:x in local_keys, remote_keys)

    for key in common_keys:
        
        remote_timestamp = ac_remote_anime_dict[key]['my_last_updated']
        local_timestamp = ac_local_anime_dict[key]['my_last_updated']

        if remote_timestamp > local_timestamp:
            remote_updates[key] = ac_remote_anime_dict[key]
        elif remote_timestamp < local_timestamp:
            local_updates[key] = ac_local_anime_dict[key]

    return (remote_updates, local_updates, deleted_entry_keys)

    
def _push_list(local_updates):
    """
    Private Medoth
    Updates every entry in the local updates dictionary to the mal server.
    Should be called after the local updates are determined with the
    filter_sync_changes function.

    Returns:
        True on success, False on failure
    """

    headers = {
        'User-Agent': 'anichou',
        'Content-Type': 'application/x-www-form-urlencoded'}

    for anime in local_updates.values():

        # construct push request for entry update
        postdata = urllib.urlencode({
            # id entry
            'series_animedb_id': str(anime['series_animedb_id']),
            'series_title': str(anime['series_animedb_id']),
            
            # set interesting values
            'completed_eps': str(anime['my_watched_episodes']),
            'status': str(anime['my_status']),
            'score': str(anime['my_score']),
            
            # protocol stuff
            'close_on_update': 'true',
            'submitIt': 2 })

        push_base_url = \
            'http://myanimelist.net/panel.php?keepThis=true&go=edit&id=' + \
            str(anime['my_id']) + '&hidenav=true&TB_iframe=false'

        push_request = urllib2.Request(push_base_url, postdata, headers)

        # push update request
        try:
            response = urllib2.urlopen(push_request)
            # print response.read() #  -- for testing
        except URLError, e:
            if hasattr(e, 'reason'):
                print 'We failed to reach a server.'
                print 'Reason: ', e.reason
            elif hasattr(e, 'code'):
                print 'The server couldn\'t fulfill the request.'
                print 'Error code: ', e.code
            return False
    return True
        
