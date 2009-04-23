
# Copyright (c) 2008 Gareth Latty
# Copyright (c) 2009 Sebastian Bartos
# See COPYING for details

"""
This module contains the GTK+ GUI subsystem of AnimeCollector. It sets up the
user interface and enters the main event loop.

MODULE GLOBALS
==============
They are not nice, but the best in this situation. This file has two globals
defined in the gtkctl class constructor:

 - MODCTL: pointer to the gtkctl class instance.
 - WIDGETS: pointer to the widgets wrapper.
"""

import os, gtk, gtk.glade, gobject, webbrowser
import globs, data


class glade_handlers(object):
	"""
	We put all of our glade gtk signal handlers into this class.
	This lets us bind all of them at once, because their names are in the class
	dict. If you want to know where these signals are assigned, then take a look
	at the data/ui.glade file (glade XML).
	"""

	def gtk_main_quit(event):
		gtk.main_quit()
	def on_button_ac_clicked(event):
		webbrowser.open('http://myanimelist.net/clubs.php?cid=10642', 2)
	def on_button_mal_clicked(event):
		webbroweser.open('http://myanimelist.net', 2)
	def on_button_sync_clicked(event):
		# Syncronize with mal server when sync button is pressed
		MODCTL.anime_data.sync()
		MODCTL.update_form_db_all()
	def on_about(event):
		WIDGETS['aboutdialog'].show_all()
	def on_about_close(widget, event):
		WIDGETS['aboutdialog'].hide_all()
		return True
	def on_menuitem_prefs_activate(event):
		WIDGETS['preferences'].show_all()
	def on_prefs_close(widget=None, event=None):
		WIDGETS['preferences'].hide_all()
		return True

class widget_wrapper(object):
	"""
	Load and set up the glade user interface and connect the signal hanlers.
	Provide a convenient way to access the glade widgets.
	"""

	def __init__(self):
		""" Load user interface and connect signal handlers. """
		self.widgets = \
				gtk.glade.XML(
				os.path.join(globs.ac_package_path, 'data', 'ui.glade'))
		self.widgets.signal_autoconnect(glade_handlers.__dict__)

	def __getitem__(self, key):
		""" Make widgets accessable by name.

		It's simply done by overriding the aquisiton default of the class. Makes
		referencing widgets by name much more convinient:
	
		EXAMPLE
		=======
		To reference a widget by name (based on the glade file) and perform a
		GTK action with it you use:
		   
		   widgets['widget_name'].action()
		"""
		return self.widgets.get_widget(key)


class list_treeview(gtk.TreeView):
	""" This is one of the two more interesting classes in the GUI subsystem.
	
	It is used to create and control the anime list treeview's (the big table in
	the middle that shows anime enries). It also handles manual editing on the
	table via callbacks, which are called when an episode, status or score entry
	is edited (slow double click on one of these enries).
	"""

	def __init__(self, tab_id):
		""" Initialize the treeview.

		Call the parent constructor, store some references, define some class
		constants, add columns to the treeview and glue this together.

		The exciting part is the clomuns schemata setup, which tells the columns
		how they look like and what they should do when edited (connect 
		callbacks).

		ARGUMENTS
		=========
		- tab_id: MAL schema based (data.STATUS) tab id (watching, etc..)

		PROPERTIES
		==========
		- liststore: probably the most interseting property, as it stores the
		  data of the table. It can be accessed by index, like
		  liststore[row][column], both starting with 0.
		- col: reference to the tree view columns the class has. Not really
		  interesting outside init, but may come in handy for plugin
		  development.
		"""

		# Call parrent constructor
		gtk.TreeView.__init__(self)

		# Mal tab type id
		self.tab_id = tab_id
		self.data = {}

		# Some treeview specific constants (column id's)
		( self.NAME, self.EPISODE, self.STATUS, self.SCORE, self.PROGRESS ) = \
				range (5)

		# Add columns to self and store references by name
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
		# Editable spin column that is connected with a callback
		epcell = gtk.CellRendererSpin()
		epcell.set_property("editable", True)
		adjustment = gtk.Adjustment(0, 0, 999, 1)
		epcell.set_property("adjustment", adjustment)
		epcell.connect('edited', self.cell_episode_edited)
		self.col['Episodes'].pack_start(epcell, False)
		self.col['Episodes'].add_attribute(epcell, 'text', 1)

		# Status column schema
		# Combo box column with selectable status
		# The first part contains the choices
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
		# Basically the same as the episodes one.
		scorecell = gtk.CellRendererSpin()
		scorecell.set_property("editable", True)
		adjustment = gtk.Adjustment(0, 0, 10, 1)
		scorecell.set_property("adjustment", adjustment)
		scorecell.connect('edited', self.cell_score_edited)
		self.col['Score'].pack_start(scorecell, False)
		self.col['Score'].add_attribute(scorecell, 'text', 3)

		# Progress column schema
		# Progress bar, nothing fancy
		progresscell = gtk.CellRendererProgress()
		self.col['Progress'].pack_start(progresscell, True)
		self.col['Progress'].add_attribute(progresscell, 'value', 4)


		## Create liststore model (table containing the treeview data) and hook
		# it up to the treeview (self).
		self.liststore = gtk.ListStore(str, str, str, int, int)
		self.set_model(self.liststore)
	
	
	def repopulate(self):
		""" Add data to liststore (data table)
		
		Constructs display data for the tree view for all the values in tv_data.

		INPUT
		=====
		- self.tv_data: the update is performed with this data
		"""
		
		# clear previous data
		self.liststore.clear()

		# comupte and add new data based on self.tv_data
		for anime in self.data.values():
			
			# Extract series title
			name = anime['series_title']
			
			# Extract episodes/max and construct display string
			if anime['series_episodes']:
				max_episodes = anime['series_episodes']
			else:
				max_episodes = '-'
			current_episode = anime['my_watched_episodes']
			epstr = str(current_episode) + ' / ' + str(max_episodes)
		
			# Calculate progress bar
			progress = 0
			if isinstance(max_episodes, int):
				progress = \
						int(float(current_episode) / float(max_episodes) * 100)

			# Extract score
			score = anime['my_score']

			# Construct row list and add it to the liststore
			row = [name, epstr, data.STATUSB[self.tab_id], score, progress]
			self.liststore.append(row)


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
	""" GUI control interface class.
	
	This class starts up and controls the general user interface. Simply
	initialize it with a config and anime_data reference pointer and a shiny GTK
	GUI will pop up in the middle of your screen (if all goes well).
	"""

	def __init__(self, config, anime_data):
		"""
		Load interface and enter main loop.

		ARGUMENTS
		=========
		- config: reference to config.ac_config instance
		- anime_data: reference to myanimelist.anime_data instance
		"""

		# Hook to make the conrol module reachable from all over the
		# file, especially from the autoconnect handlers.
		# Hey, it's still less ugly than loading it on import!
		global MODCTL
		MODCTL = self

		# Store the references to the config and data instances
		self.config = config
		self.anime_data = anime_data

		# Initialize base widgets from XML and connect signal handlers
		# Hook no. 2 to make the widgets wrapper content reachable from all over
		# the file. This is the last ugly global, I promise. 
		# Especially since it wraps the wiget wrapper to a global varable.
		global WIDGETS
		WIDGETS = widget_wrapper()

		# Initialize treeviews
		self.tv = dict()
		for tab_id, name in data.STATUS.items():
			tv = list_treeview(tab_id)
			self.tv[tab_id] = tv
			WIDGETS['scrolledwindow_' + name].add(tv)

		self.update_form_db_all()

		## Show main window, connect the quit signal handler and hide the
		# now_playing statusbar
		WIDGETS['main_window'].show_all()
		WIDGETS['main_window'].connect('delete_event', lambda e,w:
				gtk.main_quit())
		WIDGETS['statusbar_now_playing'].hide()

		# Run main loop
		gtk.main()


	def update_form_db_all(self):
		""" Update all anime tables views form database.

		This is used on initialization and after syncronization.
		"""

		# Separate anime data according to their status
		for key, value in self.anime_data.db.items():
			status = value['my_status']
			self.tv[status].data[key] = value
		
		# Populate tree views
		for tab in self.tv.values():
			tab.repopulate()


