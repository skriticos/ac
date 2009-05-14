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
from lib.beautifulsoup import BeautifulSoup
import re
import urlparse
from datetime import date, datetime
import os, time

from data import mal_anime_data_schema
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
        titles as keys and and fields form mal_anime_data_schema as dict data.
    """

    def __init__(self, **kw):
        """
        Setup credentials, read local data and setup network connection
        environment. Optionally sync with MAL on startup.
        
        Does not take positional arguments. Keyword arguments can either be
        given individually (username, password, initsync) or as an
        ac_config() instance. This will not be retained.
        
        In the latter form we support some additional command line options.
        """
        # When the architecture stabilizes, switch to config as the sole
        # positional argument, and retain it instead of copying parts.
        # That would also enable reconfiguration at runtime.
        self.username = kw.get('username', kw['config'].get('mal', 'username'))
        self.password = kw.get('password', kw['config'].get('mal', 'password'))
        initsync      = kw.get('initsync', kw['config'].get('startup', 'sync'))
        try:
            self.login = kw['config'].get('mal', 'login')
        except KeyError:
            # We need a default even if arguments were given individually.
            self.login = True
        try:
            self.mirror = kw['config'].get('mal', 'mirror')
        except KeyError:
            self.mirror = None
            
        # pull the local DB as a dictionary object
        #self.db = {}
        self.local_db = local_database()
        self.db = self.local_db.get_db()
        
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
        # Three way switch: login (un)successfull or don't even try.
        login = _login(self.username,self.password) if self.login else None

        if login is False:
            print 'Login failed..'
            return False

        remoteAnime_db = _getAnimeList(self.username, self.mirror)
        if self.db:
            # If local DB is already initialized then filter changes 
            # and push local updates
            (remote_updates, local_updates, deleted_entry_keys) = \
                _filter_sync_changes(remoteAnime_db, self.db)
            _logchanges(remote_updates, local_updates, deleted_entry_keys)
            if login:
                _push_list(local_updates)
            else:
                print 'Warning! Your local data goes ouf of sync'

            # update local anime list with changes
            for key in deleted_entry_keys:
                del self.db[key]
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
        
    def fetch(self):
        """
        UNUSED
        Only fetch anime data from MyAnimeList server (overwrites local data,
        if existent). Useful for initializing and resetting local database.

        Returns a copy of the fetched database on success, None on failure.
        """
        self.db = _getAnimeList(self.username)

        # write to local DB
        self.local_db.set_db(self.db)

        return self.db

def _appInfoURL(user, status = 'all', typ = None):
    """
    Safely generate a URL to get XML.
    
    Type may be 'manga'.
    """
    # Example taken from the site.
    template = 'http://myanimelist.net/malappinfo.php?u=Wile&status=all&type=manga'
    # Make tuple mutable.
    parts = list(urlparse.urlparse(template))
    # New parameters.
    query = {'u': user}
    if status:
        query['status'] = status
    if typ:
        query['type'] = typ
    # urlencode would literally output 'None'.
    parts[4] = urllib.urlencode(query)
    return urlparse.urlunparse(parts)

def _getAnimeList(username, mirror):
    """
    Retrieve Anime XML from MyAnimeList server.
    
    Returns: dictionary object.

    Ways in which the ouput of malAppInfo is *not* XML:
    
    Declared as UTF-8 but contains illegal byte sequences (characters)
    
    Uses entities inside CDATA, which is exactly the wrong way round.
    
    It further disagrees with the Expat C extension behind minidom:
    
    Contains tabs and newlines outside of tags.
    """
    # This function should be broken up and partly refactored into
    # the class to be better configurable. 
    fetch_url = _appInfoURL(username)
    try:
        fetch_response = open(mirror, 'rb')
    except:
        # TODO whatever error open(None) raises.
        fetch_response = urllib2.urlopen(fetch_url)
    # BeautifulSoup could do the read() and unicode-conversion, if it
    # weren't for the illegal characters, as it internally doesn't
    # use 'replace'.
    fetch_response = unicode(fetch_response.read(), 'utf-8', 'replace')
    xmldata = BeautifulSoup.BeautifulStoneSoup(fetch_response)
    # For unknown reasons it doesn't work without recursive.
    # Nor does iterating over myanimelist.anime. BS documentation broken?
    anime_nodes = xmldata.myanimelist.findAll('anime', recursive = True)
    # We have to manually convert after getting them out of the CDATA.
    entity = lambda m: BeautifulSoup.Tag.XML_ENTITIES_TO_SPECIAL_CHARS[m.group(1)]
    # Walk through all the anime nodes and convert the data to a python
    # dictionary.
    ac_remote_anime_dict = dict()
    for anime in anime_nodes:
        # ac_node builds the output of our function. Everything added to it
        # must either be made independent of the parse tree by calling
        # NavigableString.extract() or, preferrably, be turned into a
        # different type like unicode(). This is a side-effect of using
        # non-mutators like string.strip()
        # Failing to do this will crash cPickle.
        ac_node = dict()
        for node, typ in mal_anime_data_schema.iteritems():
            try:
                value = getattr(anime, node).string.strip()
                # One would think re.sub directly accepts string subclasses
                # like NavigableString. Raises a TypeError, though.
                value = re.sub(r'&(\w+);', entity, value)
            except AttributeError:
                continue
            if typ is datetime:
                # process my_last_updated unix timestamp
                ac_node[node] = datetime.fromtimestamp(int(value))
            elif typ is int:
                # process integer slots
                ac_node[node] = int(value)
            elif typ is date and value != '0000-00-00':
                # proces date slots
                (y,m,d) = value.split('-')
                (y,m,d) = int(y), int(m), int(d)
                if y and m and d:
                    ac_node[node] = date(y,m,d)
            else:
                # process string slots
                ac_node[node] = value

        # series titles are used as anime identifiers
        # the keys for the resulting dictionary are encoded to ASCII, so they
        # can be simply put into shelves
        key = ac_node['series_title'].encode('utf-8')

        # add node entry to the resulting nodelist
        ac_remote_anime_dict[key] = ac_node

    # the resulting dict is like this:
    # {<ASCII-fied key from title>: {<mal_anime_data_schema-fields>: <values>}, ...}
    return ac_remote_anime_dict

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
        if login_response == "Couldn't open s-database. Please contact Xinil.":
            return False
        
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
