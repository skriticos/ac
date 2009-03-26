#!/usr/bin/env python


							  ## Import section ##

from __future__ import with_statement

import os, sys, Queue, pickle, webbrowser, \
		pygtk, gtk, gtk.glade, gobject, time

from twisted.internet import gtk2reactor
gtk2reactor.install()

from twisted.internet import reactor
from twisted.web import client

import modules.myanimelist
from modules.players import get_playing

from config import ac_config
from data import *

								### Unsorted ###

PATH = os.getcwd()
ADD = True # ??
REMOVE = False # ??

# XXX: remove this
class debugger:

	def __init__(self, verbosity):
		self.debug = verbosity

	def out(self, msg=None, level=1):
		if self.debug >= level:
			print level, ": ", msg

preference_groups = [] # ??


						   ### Class declarations ###

class leeroyjenkins(object):

	wTree = None
	config = None
	context = None
	worklist = []
	current = None
	bars = []
	stati = []
	username = None
	password = None
	data = {}
	quitting = False

	def __init__(self):
		self.config = ac_config()



		self.preference_groups = []
		
		# turning in circles here
		for groups in self.config.option_groups:
			if groups[2]:
				self.preference_groups.append(groups)

		self.debug = debugger(int((self.config.options)["debug"]["verbosity"]))

		self.stati = ["current", "completed", "onHold", "planToWatch"]

		self.bars = (self.config.options)["ui"]["bars"].split(",")

		self.initgui()

		self.mal = modules.myanimelist.dataSource(self.debug)

		# self.players = modules.players.detectPlayers(self.debug)

		self.fillPrefs()

		self.context = self.wTree.get_widget("statusbar").get_context_id("animecollector")
		gobject.timeout_add(100, self.update)
		# gobject.timeout_add(5000, self.players.check)

		if (self.config.connection)["mallogin"]["autologin"].upper() == \
		   "TRUE":
			self.mal_login()
   
		if os.path.isfile('mal.pkl') and os.path.getsize('mal.pkl') > 0:
			with open('mal.pkl') as f:
				self.data_mal = pickle.load(f)
		else:
			open('mal.pkl', 'w')
			self.data_mal = {}

		if (self.config.list)["refresh"]["autorefresh"].upper() == "TRUE":
			self.refresh(None)

		if (self.config.ui)["tray"]["onStartup"].upper() == "TRUE":
			self.getWidget("window_main").hide()

		if (self.config.ui)["tray"]["onClose"].upper() == "TRUE":
			self.getWidget("window_main").connect("delete-event", self.toggleMain)
		else:
			self.getWidget("window_main").connect("delete-event", self.quit)

		if (self.config.ui)["window"]["maximiseOnStartup"].upper() == "TRUE":
			self.getWidget("window_main").maximize()

		self.populateTreeViews()
		
		if (self.config.options)["other"]["runBefore"].upper() == "FALSE":
			self.getWidget("window_wizard").show()

		reactor.run()

	def initgui(self):

		self.debug.out("Initiating GUI...")

		self.wTree = gtk.glade.XML("main.glade")

		for bar in self.bars:
			self.getWidget("togglebutton_" + bar).show()
			self.getWidget("togglebutton_" + bar).connect("toggled",
														  self.switchBar)
			self.getWidget("menuitem_bars_" + bar).show()
			self.getWidget("menuitem_bars_" + bar).connect("toggled",
														   self.switchBar)

		for bar in (self.config.options)["ui"]["barsVisible"].split(","):
			self.getWidget(bar + "Bar").show()
			self.getWidget("togglebutton_" + bar).set_active(True)

		for tree in self.stati:
			self.getWidget("treeview_" + tree).connect("cursor_changed",
													   self.updateEditBar)
			self.getWidget("treeview_" + tree).connect("button_press_event",
													   self.popup)

		self.trayicon = gtk.StatusIcon()
		self.trayicon.set_from_file("ac.ico")
		self.trayicon.connect("activate", self.toggleMain)

		self.fillStatusCombo()

		dic = {
			"on_menuitem_file_quit_activate": self.quit,
			"on_menuitem_edit_preferences_activate": self.showPrefs,
			"on_button_preferences_clicked": self.showPrefs,
			"on_button_prefs_cancel_clicked": self.hidePrefs,
			"on_button_prefs_apply_clicked": self.applyPrefs,
			"on_button_mal_refresh_clicked": self.refresh,
			"on_button_edit_clicked": self.edit,
			"on_button_mal_login_clicked": self.mal_login,
			"on_button_anidb_login_clicked": self.anidb_login,
			"on_button_anidb_logout_clicked": self.anidb_logout,
			"on_button_mal_logout_clicked": self.mal_logout,
			"on_button_login_cancel_clicked": self.hideLogin,
			"on_button_login_ok_clicked": self.mal_login,
			"on_menuitem_help_about_activate": self.runAbout,
			"on_aboutdialog_response": self.hideAbout,
			"on_button_mal_clicked": self.web,
			"on_button_anidb_clicked": self.web,
			"on_button_ac_clicked": self.web,
			"on_menuitem_tree_play_activate": self.to_implement,
			"on_menuitem_tree_edit_activate": self.showEdit,
			"on_button_full_edit_cancel_clicked": self.hideEdit,
			"on_button_wizard_skip_clicked": self.wizardInteract,
			"on_button_wizard_previous_clicked": self.wizardInteract,
			"on_button_wizard_next_clicked": self.wizardInteract,
			"on_button_wizard_ok_clicked": self.wizardInteract,
		}

		self.wTree.signal_autoconnect(dic)

		self.trayicon.set_visible(True)

	def wizardInteract(self, widget, event=None):
		if widget == self.getWidget("button_wizard_skip"):
			self.debug.out("User skipped wizard...", 2)
			self.getWidget("window_wizard").hide()
			self.config.options["other"]["runBefore"] = True
			self.config.update()
			self.config.write()
			self.config.read()
		elif widget == self.getWidget("button_wizard_previous"):
			self.debug.out("User went back a page on wizard...", 3)
			if self.getWidget("wizard_page_2").flags() & gtk.VISIBLE:
				self.getWidget("wizard_page_1").show()
				self.getWidget("wizard_page_2").hide()
				self.getWidget("button_wizard_ok").hide()
				self.getWidget("button_wizard_next").show()
				self.getWidget("button_wizard_previous").set_sensitive(False)
		elif widget == self.getWidget("button_wizard_next"):
			self.debug.out("User went forwards a page on wizard...", 3)
			if self.getWidget("wizard_page_1").flags() & gtk.VISIBLE:
				self.getWidget("wizard_page_1").hide()
				self.getWidget("wizard_page_2").show()
				self.getWidget("button_wizard_next").hide()
				self.getWidget("button_wizard_ok").show() 
				self.getWidget("button_wizard_previous").set_sensitive(True)
		elif widget == self.getWidget("button_wizard_ok"):
			self.debug.out("User finished wizard...", 2)
			self.getWidget("window_wizard").hide()
			prefs = [self.config.connection, "connection", True]
			for (name, group) in prefs[0].iteritems():
				for (item, value) in group.iteritems():
					pref = self.setPref("wizard_" + prefs[1] + "_" + name + "_" + item)
					if pref:
						prefs[0][name][item] = pref
			self.config.options["other"]["runBefore"] = True
			self.config.update()
			self.config.write()
			self.config.read()

	def toggleMain(self, widget, event=None):
		self.debug.out("Toggle main window...", 2)
		window = self.getWidget("window_main")
		if window.flags() & gtk.VISIBLE:
			window.hide()
		else:
			window.show()
		return True

	def to_implement(self, widget=None, event=None):
		self.debug.out("To be implemented...")

	def showEdit(self, widget, event=None):
		self.debug.out("Show edit window...", 2)
		self.getWidget("window_edit").show()

	def hideEdit(self, widget, event=None):
		self.debug.out("Hiding edit window...", 2)
		self.getWidget("window_edit").hide()

	def popup(self, widget, event=None):
		if event.button == 3:
			x = int(event.x)
			y = int(event.y)
			time = event.time
			pthinfo = widget.get_path_at_pos(x, y)
			if pthinfo is not None:
				self.debug.out("Treelist right-click...", 2)
				(path, col, cellx, celly) = pthinfo
				widget.grab_focus()
				widget.set_cursor(path, col, 0)
				self.getWidget("menu_tree").popup(None, None, None,
												  event.button, time, (widget, pthinfo))

	def update(self):
		self.debug.out("Regular call to update from module queues...", 4)
		if len(self.worklist):
			self.wTree.get_widget("progressbar").pulse()

		if not self.mal.status.empty():
			try:
				value = self.mal.status.get_nowait()
			except Queue.Empty:
				value = None
			if value:
				(task, success, data) = value
				if task == "identify":
					if success:
						self.statusMessage("Logged In to MAL.")
						self.getWidget("button_mal_login").hide()
						self.getWidget("button_mal_logout").show()
						self.getWidget("button_mal_refresh").set_sensitive(True)
					else:
						self.statusMessage("MAL Log in failed.")
					self.working("mallogin", REMOVE)
				elif task == "update":
					self.mal_updated(success)
				elif task == "commit":
					self.working("edit", REMOVE)
					if success:
						self.statusMessage("MAL update successful.")
					else:
						self.statusMessage("MAL update failed.")
					self.populateTreeViews()
		return True

	def runAbout(self, widget):
		self.debug.out("Showing about dialog...", 2)
		self.getWidget("aboutdialog").run()

	def hideAbout(self, widget, event=None):
		self.debug.out("Hiding about dialog...", 2)
		self.getWidget("aboutdialog").hide()

	def setPrefs(self):
		self.debug.out("Setting preferences...", 2)
		for prefs in self.preference_groups:
			for (name, group) in prefs[0].iteritems():
				for (item, value) in group.iteritems():
					prefs[0][name][item] = self.setPref("prefs_" + prefs[1] +
														"_" + name + "_" + item)
		self.config.update()
		self.config.write()
		self.config.read()

	def setPref(self, widgetName):
		self.debug.out("Set preference...", 3)
		widget = self.getWidget(widgetName)
		widgetType = type(widget)
		if widgetType is gtk.Entry:
			pref = widget.get_text()
		elif widgetType is gtk.CheckButton:
			pref = widget.get_active()
		elif widgetType is gtk.SpinButton:
			pref = int(widget.get_value())
		else:
			self.debug.out("Unable to get value from widget (" + widgetName + ") of type: " + str(widgetType))
			return None
		return str(pref)

	def fillPrefs(self):
		self.debug.out("Filling preferences...", 2)
		for prefs in self.preference_groups:
			for (name, group) in prefs[0].iteritems():
				for (item, value) in group.iteritems():
					self.fillPref("prefs_" + prefs[1] + "_" + name + "_" +
								  item, prefs[0][name][item])

	def fillPref(self, widgetName, value):
		self.debug.out("Fill preference...", 3)
		widget = self.getWidget(widgetName)
		widgetType = type(widget)
		if widgetType is gtk.Entry:
			widget.set_text(str(value))
		elif widgetType is gtk.CheckButton:
			if value.upper() == "TRUE":
				widget.set_active(True)
			else:
				widget.set_active(False)
		elif widgetType is gtk.SpinButton:
			widget.set_value(int(value))
		else:
			self.debug.out("Unable to set widget (" + widgetName + ") of type: " + str(widgetType) + " to value: " + str(value))

	def mal_logout(self, widget=None):
		self.debug.out("Logging out of MAL...", 2)
		self.mal.unidentify()
		self.getWidget("button_mal_login").show()
		self.getWidget("button_mal_logout").hide()
		self.getWidget("button_mal_refresh").set_sensitive(False)
		self.statusMessage("Logged Out.")

	def anidb_logout(self, widget=None):
		self.debug.out("Logging out of AniDB...", 2)
		self.working("anidbLogout", ADD)
		self.anidb.unidentify()

	def mal_login(self, widget=None):
		if self.getWidget("entry_login_password").get_text():
			self.username = self.getWidget("entry_login_username").get_text()
			self.password = self.getWidget("entry_login_password").get_text()
			#self.username = self.getWidget("entry_login_username").set_text("")
			# self.password = self.getWidget("entry_login_password").set_text("")
			self.getWidget("window_login").hide()
		else:
			if (self.config.connection)["mallogin"]["password"]:
				self.username = (self.config.connection)["mallogin"]["username"]
				self.password = (self.config.connection)["mallogin"]["password"]
			else:
				if (self.config.connection)["mallogin"]["username"]:
					self.getWidget("entry_login_username").set_text((self.config.connection)["mallogin"]["username"])
				self.getWidget("window_login").show()
				return 0

		self.statusMessage("Attempting to log in to MAL...")
		self.working("mallogin", ADD)

		self.mal.identify(self.username, self.password)

	def anidb_login(self, widget=None):
		self.debug.out("Logging in to AniDB...", 2)
		if self.getWidget("entry_login_password").get_text():
			self.username = self.getWidget("entry_login_username").get_text()
			self.password = self.getWidget("entry_login_password").get_text()
			self.username = self.getWidget("entry_login_username").set_text("")
			self.password = self.getWidget("entry_login_password").set_text("")
			self.getWidget("window_login").hide()
		else:
			if (self.config.connection)["anidbLogin"]["password"]:
				self.username = (self.config.connection)["anidbLogin"]["username"]
				self.password = (self.config.connection)["anidbLogin"]["password"]
			else:
				if (self.config.connection)["anidbLogin"]["username"]:
					self.getWidget("entry_login_username").set_text((self.config.connection)["anidbLogin"]["username"])
				self.getWidget("window_login").show()
				return 0

		self.statusMessage("Attempting to log in to AniDB...")
		self.working("anidbLogin", ADD)

		self.anidb.identify(self.username, self.password)

	def mal_updated(self, success):
		self.debug.out("Updated from MAL...", 2)
		if success:
			self.data_mal.update(self.mal.return_as_dic())
			mal_list_pickle = file('mal.pkl', 'w')
			pickle.dump(self.data_mal, mal_list_pickle)
			self.statusMessage("List retrieved.")
		else:
			self.statusMessage("Failed to retrive list.")
		self.working("malUpdate", REMOVE)
		self.populateTreeViews()

	def fillStatusCombo(self):

		self.debug.out("Filling status combo box...", 2)

		combo = self.getWidget("combobox_status")
		cell = gtk.CellRendererText()

		slist = gtk.ListStore(str, int)

		combo.pack_start(cell, True)
		combo.add_attribute(cell, "text", 0)

		slist.append(["Watching", 1])
		slist.append(["Completed", 2])
		slist.append(["On Hold", 3])
		slist.append(["Dropped", 5])
		slist.append(["Plan To Watch", 6])

		combo.set_model(slist)

	def sanDate(self, thedate):

		self.debug.out("Sanitising a date...", 3)

		if type(thedate) is date:
			if thedate:
				return thedate
			else:
				return None
		if type(thedate) is str:
			if not thedate == "0000-00-00":
				year = thedate.split("-")[0]
				month = thedate.split("-")[1]
				day = thedate.split("-")[2]
				if not year == "0000":
					if not month == "00":
						if not day == "00":
							return date.fromtimestamp(time.mktime(time.strptime(thedate,
																	"%Y-%m-%d")))
						else:
							return None
					else:
						return None
				else:
					return None
			else:
				return None

	def sanUnicode(self, thestring):
		self.debug.out("Sanitising a unicode...", 3)
		if thestring:
			return unicode(thestring)
		else:
			return None

	def getValue(self, tree, node):
		self.debug.out("Getting a value from XML...", 3)
		endnode = tree.getElementsByTagName(node)
		if endnode:
			if endnode[0]:
				if endnode[0].firstChild:
					if endnode[0].firstChild.nodeValue:
						return endnode[0].firstChild.nodeValue
					else:
						return None
				else:
					return None
			else:
				return None
		else:
			return None

	def populateTreeViews(self):
		self.debug.out("Populating tree views...")
		for tree in self.stati:
			self.populateTreeView(self.getWidget("treeview_" + tree))

	def populateTreeView(self, tree):

		status = self.treeviewToStatus(tree)

		self.debug.out("Populating tree view (" + STATUS[status] +
					   ")...", 2)

		for column in tree.get_columns():
			tree.remove_column(column)

		self.columns = []

		self.columns.append((gtk.TreeViewColumn('Title'), "text"))
		self.columns.append((gtk.TreeViewColumn('Status'), "text"))
		self.columns.append((gtk.TreeViewColumn('Type'), "text"))
		self.columns.append((gtk.TreeViewColumn('Score'), "text"))
		self.columns.append((gtk.TreeViewColumn('Episodes'), "text"))
		self.columns.append((gtk.TreeViewColumn('Progress'), "progress"))

		slist = tree.get_model()
		if not slist:
			slist = gtk.ListStore(int, str, str, str, str, str, float)
		slist.clear()

		a = 1

		self.adj = {}

		for (column, ctype) in self.columns:
			if ctype == "text":
				cell = gtk.CellRendererText()
				column.pack_start(cell, True)
				column.add_attribute(cell, "text", a)
			elif ctype == "progress":
				cell = gtk.CellRendererProgress()
				column.pack_start(cell, True)
				column.add_attribute(cell, 'value', a)
			elif ctype == "pixbuf":
				cell = gtk.CellRendererPixbuf()
				column.pack_start(cell, True)
				column.add_attribute(cell, "pixbuf", a)
			tree.append_column(column)
			a += 1

		for (ident, anime) in self.data_mal.iteritems():

			if anime["my_status"] == status:

				if anime["series_episodes"]:
					percentage_watched = (float(anime["my_watched_episodes"]) /
										  float(anime["series_episodes"])) * 100
					watched = str(anime["my_watched_episodes"]) + "/" + str(anime["series_episodes"])
				else:
					percentage_watched = 0
					watched = anime["my_watched_episodes"]

				slist.append([int(anime["series_animedb_id"]), anime["series_title"],
							  SERIES_STATUS[anime["series_status"]],
							  SERIES_TYPE[anime["series_type"]], anime["my_score"],
							  anime["my_watched_episodes"],
							  percentage_watched])

		tree.set_model(slist)

	def statusMessage(self, message):
		self.debug.out("Setting status message...", 3)
		self.wTree.get_widget("statusbar").push(self.context, message)

	def treeviewToStatus(self, widget):
		self.debug.out("Getting status from treeview...", 3)
		if widget == self.getWidget("treeview_current"):
			return 1
		elif widget == self.getWidget("treeview_completed"):
			return 2
		elif widget == self.getWidget("treeview_onHold"):
			return 3
		elif widget == self.getWidget("treeview_dropped"):
			return 5
		elif widget == self.getWidget("treeview_planToWatch"):
			return 6

	def getWidget(self, widgetname):
		self.debug.out("Getting widget...", 4)
		return self.wTree.get_widget(widgetname)

	def getCurrentTreeview(self, deathnote):
		self.debug.out("Getting current treeview...", 3)
		widget = deathnote.get_tab_label(deathnote.get_nth_page(deathnote.get_current_page()))
		if widget == self.wTree.get_widget("label_current"):
			return self.wTree.get_widget("treeview_current")
		elif widget == self.wTree.get_widget("label_completed"):
			return self.wTree.get_widget("treeview_completed")
		elif widget == self.wTree.get_widget("label_onHold"):
			return self.wTree.get_widget("treeview_onHold")
		elif widget == self.wTree.get_widget("label_planToWatch"):
			return self.wTree.get_widget("treeview_planToWatch")

	def callMAL(self, uri, method="POST", postdata=None, headers=None):
		self.debug.out("Making call to MAL...")
		return client.getPage(uri, method=method, cookies=self.cookiesMAL,
							  postdata=postdata, agent="animecollector",
							  headers=headers)

	def working(self, ident, add):
		self.debug.out("Working toggle...", 3)
		if add:
			self.worklist.append(ident)
		else:
			self.worklist.remove(ident)

	def edit(self, widget, event=None):
		self.debug.out("Editing data...")
		self.working("edit", ADD)
		self.statusMessage("Making edit...")
		edits = [("status", COMBO_STATUS[self.getWidget("combobox_status").get_active()]),
				 ("episodes_watched", int(self.getWidget("spinbutton_episodesWatched").get_value())),
				 ("score", int(self.getWidget("spinbutton_score").get_value()))]
		olddata = self.data_mal
		for (name, value) in edits:
			(self.data_mal)[self.current][name] = value
		self.mal.commit(self.current, edits, olddata, self.data_mal)
		self.buzhug.commit(self.current, edits)

	def switchBar(self, widget, event=None):
		self.debug.out("Switching bar...", 3)
		for bar in self.bars:
			button = self.getWidget("togglebutton_" + bar)
			menuitem = self.getWidget("menuitem_bars_" + bar)
			bar = self.getWidget(bar + "Bar")
			if widget == button or widget == menuitem:
				if widget.get_active():
					bar.show()
					menuitem.set_active(True)
					button.set_active(True)
				else:
					bar.hide()
					menuitem.set_active(False)
					button.set_active(False)

	def updateEditBar(self, widget, event=None):
		self.debug.out("Updating the edit bar...", 3)
		status = self.treeviewToStatus(widget)
		(tree, itr) = widget.get_selection().get_selected()
		(self.current, ) = tree.get(itr, 0)
		record = (self.data_mal)[self.current]
		if record["series_episodes"]:
			self.getWidget("spinbutton_episodesWatched").set_range(0,
																   record["series_episodes"])
			self.getWidget("label_totalEpisodes").set_label(str(record["series_episodes"]))
		else:
			self.getWidget("spinbutton_episodesWatched").set_range(0,
																   500)
			self.getWidget("label_totalEpisodes").set_label("?")
		self.getWidget("spinbutton_episodesWatched").set_value(record["my_watched_episodes"])
		self.getWidget("spinbutton_score").set_value(record["my_score"])
		self.getWidget("combobox_status").set_active(STATUS_COMBO[record["my_status"]])
		if record["series_episodes"]:
			self.getWidget("spinbutton_episodesRewatched").set_range(0,
																	 record["series_episodes"])
			self.getWidget("label_totalEpisodesRewatched").set_label(str(record["series_episodes"]))
		else:
			self.getWidget("spinbutton_episodesRewatched").set_range(0,
																	 500)
			self.getWidget("label_totalEpisodesRewatched").set_label("?")
		self.getWidget("spinbutton_episodesRewatched").set_value(record["my_rewatching_ep"])
		self.getWidget("spinbutton_timesRewatched").set_value(record["my_rewatching"])

	def refresh(self, widget, event=None):
		self.debug.out("Refreshing MAL data...")
		if self.username:
			self.statusMessage("Refreshing MAL list.")
			self.working("malUpdate", ADD)
			self.mal.update()
		else:
			self.statusMessage("Unable to refresh list: Not logged in.")

	def applyPrefs(self, widget, event=None):
		self.debug.out("Applying preferences...", 2)
		self.setPrefs()
		self.getWidget("window_preferences").hide()

	def showPrefs(self, widget, event=None):
		self.debug.out("Showing preferences...", 3)
		self.getWidget("window_preferences").show()

	def hidePrefs(self, widget, event=None):
		self.debug.out("Hiding preferences...", 3)
		self.getWidget("window_preferences").hide()
		self.fillPrefs()

	def hideLogin(self, widget, event=None):
		self.debug.out("Hiding login window...", 3)
		self.getWidget("window_login").hide()
		self.getWidget("entry_login_username").set_text("")
		self.getWidget("entry_login_password").set_text("")

	def quit(self, widget, event=None):
		self.quitting = True
		#self.anidb_logout()
		self.debug.out("Quitting...")
		sys.exit(0)

	def web(self, widget, event=None):
		self.debug.out("Loading up web browser...")
		if widget == self.getWidget("button_mal"):
			uri = "http://myanimelist.net"
		elif widget == self.getWidget("button_anidb"):
			uri = "http://anidb.net"
		elif widget == self.getWidget("button_ac"):
			uri = "http://animecollector.lattyware.co.uk"
		webbrowser.open(uri, new=2, autoraise=1)




letsdothis = leeroyjenkins()
