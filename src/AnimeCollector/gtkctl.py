
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
import data


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


class list_treeview(gtk.TreeView):
	def __init__(self, guictl, tab_id):

		gtk.TreeView.__init__(self)

		# Pointer to guictl
		self.guictlptr = guictl

		# Mal tab type id
		self.tab_id = tab_id

		# Some treeview specific constants (column id's)
		( self.NAME, self.EPISODE, self.STATUS, self.SCORE, self.PROGRESS ) = \
				range (5)

		# Add columns to treeview
		self.col = dict()
		for colname in ['Title', 'Episodes', 'Status', 'Score', 'Progress']:
			self.col[colname] = gtk.TreeViewColumn(colname)
			self.append_column(self.col[colname])


		## Set up the column schemata
		
		# Title column schema
		titlecell = gtk.CellRendererText()
		self.col['Title'].pack_start(titlecell, True)
		self.col['Title'].add_attribute(titlecell, 'text', 0)

		# Episode column schema
		epcell = gtk.CellRendererSpin()
		epcell.set_property("editable", True)
		adjustment = gtk.Adjustment(0, 0, 999, 1)
		epcell.set_property("adjustment", adjustment)
		epcell.connect('edited', self.cell_episode_edited)
		self.col['Episodes'].pack_start(epcell, False)
		self.col['Episodes'].add_attribute(epcell, 'text', 1)

		# Status column schema
		combomodel = gtk.ListStore(str)
		combomodel.append(['Watching'])
		combomodel.append(['On Hold'])
		combomodel.append(['Completed'])
		combomodel.append(['Plan to Watch'])
		combomodel.append(['Dropped'])

		statuscell = gtk.CellRendererCombo()
		statuscell.set_property('model', combomodel)
		statuscell.set_property('has-entry', False)
		statuscell.set_property('editable', True)
		statuscell.set_property('text-column', 0)
		statuscell.connect('edited', self.cell_status_edited)
		self.col['Status'].pack_start(statuscell, False)
		self.col['Status'].add_attribute(statuscell, 'text', 2)

		# Score column schema
		scorecell = gtk.CellRendererSpin()
		scorecell.set_property("editable", True)
		adjustment = gtk.Adjustment(0, 0, 10, 1)
		scorecell.set_property("adjustment", adjustment)
		scorecell.connect('edited', self.cell_score_edited)
		self.col['Score'].pack_start(scorecell, False)
		self.col['Score'].add_attribute(scorecell, 'text', 3)

		# Progress column schema
		progresscell = gtk.CellRendererProgress()
		self.col['Progress'].pack_start(progresscell, True)
		self.col['Progress'].add_attribute(progresscell, 'value', 4)

		
		## Pulg the model in the treeview
		self.liststore = gtk.ListStore(str, str, str, int, int)
		self.set_model(self.liststore)
	

	def cell_score_edited(self, *args):
		""" Handles editing / change of score cells.

		Not too much here, only database update.
		"""
		print args
		pass


	def cell_status_edited(self, *args):
		""" Handles selection of status combo cells.
		
		Pushes the entry in other categories and eventually updates the episode
		number (from non-complete to complete -> maximize my_episodes)
		"""

		##
		## XXX: todo: add combo switch logic
		##

		pass
	

	def cell_episode_edited(self, spinr, row, value):
		""" Handles the modification of the episode number spin button.

		If all a valid new value is entered, the row is updated and parrent
		update function is called to update the local database.
		"""
		
		# Prepare data set
		oldstr = self.liststore[row][self.EPISODE]
		(old, max) = oldstr.split(' / ')
		oldvalue = int(old)
		maxvalue = int(max)
		newvalue = int(value)
		
		# Determine if action is required
		if newvalue != oldvalue and newvalue <= maxvalue:

			if newvalue < maxvalue:

				##
				## XXX: check if we were completed before, push to watching if
				##      not

				# Update row episode data
				newstr = str(newvalue) + ' / ' + str(maxvalue)
				self.liststore[row][self.EPISODE] = newstr

				# Update progress bar
				if newvalue < maxvalue:
					self.liststore[row][self.PROGRESS] = \
							int(float(newvalue) / float(maxvalue) * 100)

			
			#
			# XXX: insert data update routine using guictlptk.anime_data
			#
			
			# Did we reach treashhold and was not completed?
			if self.tab_id != data.COMPLETED and newvalue == maxvalue:
				del self.liststore[row]


class guictl(object):
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

		self.tv = dict()
		# Initialize anime data display treeviews
		for tab_id, name in data.STATUS.items():
			tv = list_treeview(self, tab_id)
			self.tv[tab_id] = tv
			widgets['scrolledwindow_' + name].add(tv)

		## XXX: testdata
		self.tv[data.WATCHING].liststore.append(
				['Anime title foo', '12 / 24', 'Watching', 5, 80])
		self.tv[data.WATCHING].liststore.append(
				['Anime title bar', '2 / 17', 'On Hold', 7, 50])

		# Tune initial view
		self.widgets['main_window'].show_all()
		self.widgets['main_window'].connect('delete_event', lambda e,w:
				gtk.main_quit())
		widgets['statusbar_now_playing'].hide()

		# Run main loop
		gtk.main()

