# =========================================================================== #
# Name:	wxmockup.py
# Purpose: Mockup for wxPython to test the looks on different platforms.
#
# ToDo:	The icon theme must be replaced
#		The data model for the listview has to be elaborated
#
# Copyright (c) 2009 Sebastian Bartos
#
# License: GPL v3, see COPYING file for details
# =========================================================================== #
 
import wx, sys, platform
import wx.lib.mixins.listctrl

# Some sample data
adat = {
# schema: <row no.>: (<name>, <episodes>, <status>, <score>, <progress>)
1:('Welcome to the NHK', '9 / 24', 'Watching', 7, 37),
2:('Starship Operators', '3 / 13', 'Watching', 0, 23),
3:('Nagasarete Airantou', '2 / 26', 'Watching', 0, 7),
4:('Witch Hunter Robin', '1 / 26', 'Watching', 0, 3),
5:('Fruits Basket', '25 / 26', 'Watching', 0, 96),
6:('Clannad ~After Story~', '11 / 24', 'Watching', 6, 45)
}

class TestListCtrl(wx.ListCtrl, wx.lib.mixins.listctrl.ListCtrlAutoWidthMixin):
	def __init__(self, parent, ID, pos=wx.DefaultPosition,
				 size=wx.DefaultSize, style=0):
		wx.ListCtrl.__init__(self, parent, ID, pos, size, style)
		wx.lib.mixins.listctrl.ListCtrlAutoWidthMixin.__init__(self)

class TestListCtrlPanel(wx.Panel, wx.lib.mixins.listctrl.ColumnSorterMixin):
	def __init__(self, parent):
		wx.Panel.__init__(self, parent, -1, style=wx.WANTS_CHARS)
		sizer = wx.BoxSizer(wx.VERTICAL)

		tID = wx.NewId()
		self.list = TestListCtrl(self, tID,
								 style=wx.LC_REPORT 
								 #| wx.BORDER_SUNKEN
								 | wx.BORDER_NONE
								 | wx.LC_EDIT_LABELS
								 | wx.LC_SORT_ASCENDING
								 #| wx.LC_NO_HEADER
								 #| wx.LC_VRULES
								 #| wx.LC_HRULES
								 #| wx.LC_SINGLE_SEL
								 )
		sizer.Add(self.list, 1, wx.EXPAND)
		self.PopulateList()
		self.itemDataMap = adat
		wx.lib.mixins.listctrl.ColumnSorterMixin.__init__(self, 3)
		self.SetSizer(sizer)
		self.SetAutoLayout(True)

	def PopulateList(self):
		# schema: <row no.>: (<name>, <episodes>, <status>, <score>, <progress>)
		self.list.InsertColumn(0, "Title")
		self.list.InsertColumn(1, "Episodes", wx.LIST_FORMAT_CENTER)
		self.list.InsertColumn(2, "Status", wx.LIST_FORMAT_CENTER)
		self.list.InsertColumn(3, "Score", wx.LIST_FORMAT_CENTER)
		self.list.InsertColumn(4, "Progress")
	
		index = 1
		for key, data in adat.items():
			index = self.list.InsertStringItem(0,data[0])
			self.list.SetStringItem(index, 1, data[1])
			self.list.SetStringItem(index, 2, data[2])
			self.list.SetStringItem(index, 3, str(data[3]))
			self.list.SetStringItem(index, 4, 'not there yet')
			self.list.SetItemData(index, key)

		self.list.SetColumnWidth(0, 350)#wx.LIST_AUTOSIZE)
		self.list.SetColumnWidth(1, 100)#wx.LIST_AUTOSIZE)
		self.list.SetColumnWidth(2, wx.LIST_AUTOSIZE)
		self.list.SetColumnWidth(3, 75)#wx.LIST_AUTOSIZE)
		self.list.SetColumnWidth(4, wx.LIST_AUTOSIZE)
	
	def GetListCtrl(self):
		return self.list


class FixedStatusBar(wx.StatusBar):
	""" Costume status bar that fixes the wx brokenness
	
	The wx.StatusBar widget is notoriously borken on dark themes. It ignores
	system settings for 3d border and font color while using the background
	color. This derivate fixes the issue by overriding the drawing routine.
	It is only designed of single column widgets. Based on:
	http://aspn.activestate.com/ASPN/Mail/Message/wxpython-users/3595576
	http://mail.python.org/pipermail/python-list/2007-January/596101.html
	http://docs.wxwidgets.org/stable/wx_wxsystemsettings.html
	"""
	def __init__(self, parent, 
			id=-1, style=wx.DEFAULT_STATUSBAR_STYLE, name=wx.StatusLineNameStr):
		wx.StatusBar.__init__(self, parent, id, style, name)
		self.Bind(wx.EVT_PAINT, self.OnPaint)
		
	def OnPaint(self,event):
		dc = wx.PaintDC(self)
		self.Draw(dc)
		
	def Draw(self, dc):
		fg = wx.SystemSettings.GetColour(wx.SYS_COLOUR_MENUTEXT)
		bg = self.GetBackgroundColour()
		dc.BeginDrawing()
		dc.SetBackground(wx.Brush(bg))
		dc.Clear()
		dc.SetTextForeground(fg)
		dc.DrawText(self.GetStatusText(), 10, 4)
		dc.EndDrawing()

class TestFrame(wx.Frame):
	def __init__(self, parent, ID, title):
		wx.Frame.__init__(
				self, parent, 
				id=1, title=title, pos=wx.DefaultPosition, size=(800, 600))
	
		self.SetIcon(wx.Icon('ac.ico', wx.BITMAP_TYPE_ICO))

		## Setup menu
		menu_file = wx.Menu()
		menu_file_import = wx.MenuItem(
				menu_file, wx.ID_ANY, '&Import..', 'Import data from file..')
		menu_file_import.SetBitmap(wx.Bitmap('import.png'))
		menu_file.AppendItem(menu_file_import)
		menu_file_export = wx.MenuItem(
				menu_file, wx.ID_ANY, '&Export..', 'Export data to file..')
		menu_file_export.SetBitmap(wx.Bitmap('export.png'))
		menu_file.AppendItem(menu_file_export)
		menu_file_quit = wx.MenuItem(
				menu_file, wx.ID_ANY, '&Quit\tCtrl+Q', 'Quit AniChou..')
		menu_file_quit.SetBitmap(wx.Bitmap('quit.png'))
		menu_file.AppendItem(menu_file_quit)
		
		menu_edit = wx.Menu()
		menu_edit.Append(
				wx.ID_ANY, '&Tracker', 'Toggle playtracker..',
				kind=wx.ITEM_CHECK)
		menu_edit_prefs = wx.MenuItem(
				menu_edit,
				wx.ID_ANY, '&Preferences', 'Show preferences dialog..')
		menu_edit_prefs.SetBitmap(wx.Bitmap('preferences.png'))
		menu_edit.AppendItem(menu_edit_prefs)

		menu_net = wx.Menu()
		menu_net_sync = wx.MenuItem(
				menu_net,
				wx.ID_ANY, '&Syncronize\tF5', 'Syncronize list with MyAnimeList..')
		menu_net_sync.SetBitmap(wx.Bitmap('sync.png'))
		menu_net.AppendItem(menu_net_sync)
		menu_net_mal = wx.MenuItem(
				menu_net,
				wx.ID_ANY, '&MyAnimeList', 'Open MyAnimeList website..')
		menu_net_mal.SetBitmap(wx.Bitmap('mal.png'))
		menu_net.AppendItem(menu_net_mal)
		menu_net_ac = wx.MenuItem(
				menu_net,
				wx.ID_ANY, '&AniChou', 'Open club site..')
		menu_net_ac.SetBitmap(wx.Bitmap('ac.png'))
		menu_net.AppendItem(menu_net_ac)
		
		menu_help = wx.Menu()
		menu_help_about = wx.MenuItem(
				menu_help, wx.ID_ANY, '&About', 'About dialog..')
		menu_help_about.SetBitmap(wx.Bitmap('about.png'))
		menu_help.AppendItem(menu_help_about)

		self.menuBar = wx.MenuBar()
		self.menuBar.Append(menu_file, "&File");
		self.menuBar.Append(menu_edit, "&Edit");
		self.menuBar.Append(menu_net, "&Network")
		self.menuBar.Append(menu_help, "&Help");

		self.SetMenuBar(self.menuBar)

		## Setup nootebook pages
		panel_notebook = wx.Panel(self, -1)
		notebook = wx.Notebook(panel_notebook)
		notebook_pages = list()
		notebook_pages.append(TestListCtrlPanel(notebook))
		for i in range(1, 5):
			notebook_pages.append(wx.Panel(notebook))
		
		# watching_page = TestListCtrlPanel(notebook_pages[0])

		tabs = dict()
		tabnames = \
				['Watching', 'On Hold', 'Completed', 'Plan to Watch', 'Dropped']
		for i in range(5):
			tabs[i] = tabnames[i]
		for key, value in tabs.items():
			notebook.AddPage(notebook_pages[key], value)

		sizer = wx.BoxSizer()
		sizer.Add(notebook, 1, wx.EXPAND)
		panel_notebook.SetSizer(sizer)

 
class TestApp(wx.App):
	def OnInit(self):
		frame = TestFrame(None, -1, "AniChou")
		self.SetTopWindow(frame)
		if platform.system() == 'Linux':
			statusBar = FixedStatusBar(frame)
		else:
			statusBar = wx.StatusBar(frame)
		statusBar.SetStatusText("status text..")
		frame.SetStatusBar(statusBar)
		frame.Show(True)
		frame.Center()
		return True
 
if __name__ == '__main__':
	app = TestApp()
	app.MainLoop()

