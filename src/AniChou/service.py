import plugin

class SiteProvider(object):
    __metaclass__ = plugin.Mount

    # Used in entry groups, preferences, and the file system.
    name = ""
    
    def __init__(self, preferences, folder):
        pass
        
    def setup_panel(self):
        """
        Return GUI element to configure new and existing accounts.
        """
        pass
        
    def account_factory(self, preferences):
        """
        Return instance for account described by preferences.
        """
        pass
        
    def clean_caches(self):
        """
        Delete all caches we know about.
        """
        pass
        
    def search(self, title):
        """
        Like fulltext.Index.search
        """
        pass

class AccountProvider(object):
    """
    Not a plugin, nor used for anything except to document the interface.
    
    This is essentially the ArrayController for a local copy of the site.
    """
    
    def pull(self):
        """
        Download and return remote state. The format is up to each class.
        """
        pass
        
    def push(self, state):
        """
        Update (overwrite) server with given data.
        
        This should not access the local data, so we can run it in background
        while the user is already free again to manipulate the local data.
        """
        pass
        
    def sync(self, state, remote_master = False):
        """
        Compare local with given data. Immediatley apply local changes,
        return remote changes to be pushed later.
        
        When entries are added, changed or deleted, messages have to be sent.

        For sites without per-entry mtime, when the remote copy is the master,
        overwrite local data. Otherwise discard possible server-side changes.
        In the former case it is unwise to sync multiple sites at once.

        The user will be blocked (from changing local data) while this runs.

        When syncing among multiple sites this will be called twice for each
        account, with the same state. The changes returned by the first call
        will be discarded.
        """
        pass
        
    def list(self):
        """
        DEPRECATED
        
        Return proxy objects for the whole of our local data.
        
        These have to conform to the TODO interface.
        
        They have to be notified when the corresponding local data changes or
        is deleted.
        """
        pass