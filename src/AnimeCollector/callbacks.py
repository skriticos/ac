
# callbacks.py - GTK+ callback functions for the GUI 
#
# This module contains the callback functions of the animecollector GUI widget
# events.


#========
# Imports
# =======

from sys import exit
from webbrowser import open as webopen


# ==============
# Initialization
# ==============

def cb_init(p_ui_data, p_mal_socket, p_config, p_context):
	"""
	Imports data instance pointers from the main module.
	"""
	global ui_data 
	global mal_socket
	global config
	global context
	ui_data = p_ui_data
	mal_socket = p_mal_socket
	config = p_config
	context = p_context


# ==================
# Callback functions
# ==================

def cb_webopen(widget, event=None):
	"""
	Open mal/ac website in browser.
	"""
	open_in_tab = 2
	if widget is ui_data.get_widget("button_mal"):
		webopen("http://myanimelist.net", open_in_tab)
	if widget is ui_data.get_widget("button_ac"):
		url = "http://myanimelist.net/clubs.php?cid=10642"
		webopen(url, open_in_tab)

def cb_refresh(widget, event=None):
	ui_data.get_widget("statusbar").push(context, "Refreshing MAL list..")
	mal_socket.update()

def cb_show_prefs(widget, event=None):
	ui_data.get_widget("window_preferences").show() 
def cb_hide_prefs(widget, event=None):
	ui_data.get_widget("window_preferences").hide() 

def cb_mal_login(widget=None):
	""" Atempt to login to the myAnimeList server. 
	
	Note: this function has way too much magic (recursion).
	"""
	if ui_data.get_widget("entry_login_password").get_text():
		config.mal['username'] = \
				ui_data.get_widget("entry_login_username").get_text()
		config.mal['password'] = \
				ui_data.get_widget("entry_login_password").get_text()
		ui_data.get_widget("window_login").hide()
	else:
		if not (config.mal['username'] and config.mal['password']):
			ui_data.get_widget("window_login").show()
			return 0

	ui_data.get_widget("statusbar").push(context, 
			"Attempting to log in to MAL...")

	mal_socket.identify(config.mal['username'], config.mal['password'])
#		ui_data.get_widget("statusbar").push(context, "Login successful...")
#	else:
#		ui_data.get_widget("statusbar").push(context, "Login failed...")
	
	if config.mal['login_autorefresh']:
		cb_refresh(None)


def cb_mal_logout(widget=None):
	""" Logout from the myAnimeList server. """

	mal_socket.unidentify()
	ui_data.get_widget("button_mal_login").show()
	ui_data.get_widget("button_mal_logout").hide()
	ui_data.get_widget("button_mal_refresh").set_sensitive(False)
	ui_data.get_widget("statusbar").push(context, "Logged Out.")

def cb_hide_login(widget, event=None):
	ui_data.get_widget("window_login").hide()
	ui_data.get_widget("entry_login_username").set_text("")
	ui_data.get_widget("entry_login_password").set_text("")

def cb_show_about(widget): ui_data.get_widget("aboutdialog").run() 
def cb_hide_about(widget, event=None): ui_data.get_widget("aboutdialog").hide() 
def cb_quit(widget, event=None): exit(0)

