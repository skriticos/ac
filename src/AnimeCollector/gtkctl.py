
# Copyright (c) 2008 Gareth Latty
# Copyright (c) 2009 Sebastian Bartos
# See COPYING for details

"""
---- TODO ----
Create clear data interfaces with the gui.
Eliminate magic and clean up code.
--------------


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

import gtk, pango
from gtk import glade, TreeView, ListStore
import gobject
from os import path
from webbrowser import open as webopen

from config import ac_config
from myanimelist import anime_data
from globs import ac_package_path


class glade_handlers(object):
	"""
	We put almost all of our gtk signal handlers into this class.
	This lets us bind all of them at once, because their names are in the class
	dict. If you want to know where these signals are assigned, then take a look
	at the data/ui.glade file (glade XML).
	"""

	def gtk_main_quit(event):
		gtk.main_quit()
	def on_button_ac_clicked(event):
		webopen('http://myanimelist.net/clubs.php?cid=10642', 2)
	def on_button_mal_clicked(event):
		webopen('http://myanimelist.net', 2)
	def on_about(event):
		widgets['aboutdialog'].show_all()
	def on_about_close(widget, event):
		widgets['aboutdialog'].hide_all()
		return True
	def on_menuitem_prefs_activate(event):
		widgets['preferences'].show_all()
	def on_prefs_close(widget=None, event=None):
		widgets['preferences'].hide_all()
		return True
	def on_playbar_toggled(event):
		if widgets['statusbar_now_playing'].flags() & gtk.VISIBLE:
			widgets['statusbar_now_playing'].hide()
		else:
			widgets['statusbar_now_playing'].show()

class widget_wrapper(object):
	"""
	Load and set up the glade user interface and connect the signal hanlers.
	Provide a convenient way to access the glade widgets.

	To set up the class call: widgets = widget_wrapper()
	To access widgets by name call: widgets['widget_name'].action()
	"""

	def __init__(self):
		# load user interface
		self.widgets = \
			glade.XML(path.join(ac_package_path, 'data', 'ui.glade'))
		self.widgets.signal_autoconnect(glade_handlers.__dict__)

	def __getitem__(self, key): return self.widgets.get_widget(key)


def populate_tree_view(widgets, anime_data):
	""" Populate the GTK TreeView interface widget from the anime_data.

	The TreeView uses the gtk.ListStore interface model to display the
	anime lists. It populates all 4 tabs.

	Input:
	  widgets -- widget wrapper reference to access the TreeView
      anime_data -- anime_data instance (myanimelist module)
	"""

	# note: works on a display basis
	# needs to get data fed

	liststore = ListStore(str, str, int, int, int)
	
	column_schema = []

	column_schema.append((gtk.TreeViewColumn('Title'), "text"))
	column_schema.append((gtk.TreeViewColumn('Status'), "text"))
	column_schema.append((gtk.TreeViewColumn('Score'), "spin"))
	column_schema.append((gtk.TreeViewColumn('Episodes'), "spin"))
	column_schema.append((gtk.TreeViewColumn('Progress'), "progress"))


	value_index = 0
	for column, type in column_schema:
		if type == 'text':
			# set it to expand
			cell = gtk.CellRendererText()
			# cell.set_property("expand", True)
			column.pack_start(cell, True)
			column.add_attribute(cell, 'text', value_index)
		elif type == 'spin':
			# set the right values from data
			cell = gtk.CellRendererSpin()
			adjustment = gtk.Adjustment(0, 0, 10, 1)
			cell.set_property("adjustment", adjustment)
			cell.set_property("editable", True)
			column.pack_start(cell, True)
			column.add_attribute(cell, 'text', value_index)
		elif type == "progress":
			cell = gtk.CellRendererProgress()
			column.pack_start(cell, True)
			column.add_attribute(cell, 'value', value_index)

		widgets['treeview_watching'].append_column(column)
		value_index += 1

	# add data feeding
	liststore.append(['title', 'status', 5, 5, 50])
	liststore.append(['title', 'status', 5, 5, 50])
	liststore.append(['title', 'status', 5, 5, 50])
	liststore.append(['title', 'status', 5, 5, 50])
	liststore.append(['title', 'status', 5, 5, 50])
	liststore.append(['uoa ut', 'status', 5, 5, 50])

	widgets['treeview_watching'].set_model(liststore)


class gui(object):
	"""
	Main GUI class and interface.
	"""

	def __init__(self, config, anime_data):
		"""
		Load interface and enter main loop.
		"""

		# Store the references to the config and data instances
		self.config = config
		self.anime_data = anime_data

		# Initialize base widgets from XML and connect signal handlers
		self.widgets = widget_wrapper()

		global widgets
		widgets = self.widgets

		self.widgets['main_window'].show_all()
		self.widgets['main_window'].connect('delete_event', lambda e,w:
				gtk.main_quit())
		widgets['statusbar_now_playing'].hide()

		# Display anime data in interface
		populate_tree_view(self.widgets, self.anime_data)

		# Run main loop
		gtk.main()

