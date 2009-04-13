
# Copyright (c) 2008 Gareth Latty
# Copyright (c) 2009 Sebastian Bartos
# See COPYING for details

"""
This file contains the classes and methods for setting up the AnimeCollector
application. I does the following things:
   - Load the configuration file
   - Load the stored data file
   - Set up the user interface and connect the signal handlers and enter the 
     main loop
   
This module also has important global class instances:
    - config: ac_config instance (configuration file)
    - widgets: widget_wrapper for the interfoce
"""

import gtk
from gtk import glade
from os import path
from webbrowser import open as webopen

from config import ac_config
from myanimelist import sync_mal


# ====================================
# Classes to set up the user interface
# ====================================

class glade_handlers(object):
    """
    We put almost all of our gtk signal handlers into this class.
    This lets us bind all of them at once, because their names are in the class 
    dict. If you want to know where these signals are assigned, then take a look
    at the data/ui.glade file (glade XML).
    """

    def gtk_main_quit(event): gtk.main_quit()
    def on_button_ac_clicked(event):
        webopen('http://myanimelist.net/clubs.php?cid=10642', 2)
    def on_button_mal_clicked(event):
        webopen('http://myanimelist.net', 2)
    def on_button_sync_clicked(event):
        # TODO:
        # sync_mal(config.mal['username'], config.mal['password'], LOCAL_USER_DATA)
        # update local list (including the database)
        # call list display actualization afterwards
        pass
       

class widget_wrapper(object):
    """
    Load and set up the glade user interface and connect the signal hanlers.
    Provide a convenient way to access the glade widgets.
    
    To set up the class call: widgets = widget_wrapper()
    To access widgets by name call: widgets['widget_name'].action()
    """

    def __init__(self):
        # load user interface
        self.widgets = glade.XML(path.join('data', 'ui.glade'))
        self.widgets.signal_autoconnect(glade_handlers.__dict__)

    def __getitem__(self, key): return self.widgets.get_widget(key)
        

def switch_main_visible(event):
    """
    This is the callback for the trayicon, which swiches the interface
    visibility. It's a bit special because it is not defined in the glade file 
    and therefore located here.
    """
    if widgets['main_window'].flags() & gtk.VISIBLE:
        widgets['main_window'].hide()
    else:
        widgets['main_window'].show()


def init_gui():
    """
    Call widget wrapper to load the glade interface, then add a systray and run
    the main event loop.
    """
    global widgets
    widgets = widget_wrapper()

    # display main user interface
    widgets['main_window'].show_all()

    # load and display systray icon and connect it to the handler
    trayicon = gtk.StatusIcon()
    trayicon.set_from_file(path.join('data', 'ac.ico'))
    trayicon.connect('activate', switch_main_visible)
    
    # ready.. steady.. go!
    gtk.main()


# =========================
# Core AnimeCollector class
# =========================

def core():
    global config
    config = ac_config()
    init_gui()

core()
