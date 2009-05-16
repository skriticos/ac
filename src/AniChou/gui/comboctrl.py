# =========================================================================== #
# Name:    comboctrl.py
# Purpose: autohide combo control widget declaration module
#
# Copyright (c) 2009 Sebastian Bartos
#
# License: GPL v3, see COPYING file for details
# =========================================================================== #

# XXX: needs some cleanup

import wx

# Autohide combo control class declaration =================================== #
class combo(wx.Window):
	"""Autohide combo control widget class.
	"""

	def __init__(self, parent, data, index, change, s=(150, 25)):
		"""Autohide combo control widget constructor.

		@param parent: parent on which this widget should be displayed
		@param data:   reference to the data list this widget should 
		               interact with
		@param index:  index in the list the combo should manipulate
		               (has to be done this way to call it by reference)
		@param change: change stack, where changes are pushed to
		@param s:      size of the widget
		"""

		# note: may be a good idea to export this to data.py
		self.choices = [
			'Watichng', 
			'Completed', 
			'On Hold', 
			'Plan to Watch',
			'Dropped', 
			'Re-watching']

		# call parrent constructor
		wx.Window.__init__(self, parent, -1, size = s)

		# setup persistent data
		self.data = data
		self.index = index
		self.change_stack = change
		self.selected = False

		# tell the sizers how to handle this window
		self.SetMinSize(s)
		self.SetMaxSize(s)

		# size computation for Coice
		(x, y) = s
		s2 = (x-6, y-6)
		
		# initialize controls
		self.combo = combo = \
			wx.Choice(parent, -1, size = s, choices=self.choices)
		self.txtctl = txtctl = \
			wx.TextCtrl(parent, -1, size = s2,
					style = wx.TE_CENTER| wx.NO_BORDER)
	
		# bind event handlers
		self.Bind(wx.EVT_SIZE, self.on_size)
		self.Bind(wx.EVT_MOVE, self.on_size)
		self.txtctl.Bind(wx.EVT_ENTER_WINDOW, self.on_mouse_in)
		self.txtctl.Bind(wx.EVT_LEFT_DOWN, self.on_click)
		self.combo.Bind(wx.EVT_LEAVE_WINDOW, self.on_mouse_out)
		self.combo.Bind(wx.EVT_CHOICE, self.on_combo)
		self.combo.Bind(wx.EVT_SET_FOCUS, self.on_focus)
		self.combo.Bind(wx.EVT_KILL_FOCUS, self.on_kill_focus)

		# setup starting values
		txtctl.SetValue(str(data[index]))

		# some wx bug workarounds
		self.SetBackgroundColour(txtctl.GetBackgroundColour())
		self.combo.Show()
		self.combo.Hide()

	def on_size(self, *args):
		"""Called when the window changes size/position.

		This event handler is called when the sizers push around the
		window. It places the child widgets to the correct position.
		"""
		(x,y) = self.GetPosition()
		self.txtctl.SetPosition((x+3,y+3))
		self.combo.SetPosition((x, y))

	def on_mouse_in(self, *args):
		"""Mouse enters window area.
		"""
		# self.txtctl.Hide()
		# self.combo.Show()
		pass
	
	def on_click(self, *args):
		"""Mouse clicks window area.
		"""
		self.txtctl.Hide()
		self.combo.Show()

	def on_mouse_out(self, *args):
		"""Mouse leaves window area
		"""
		self.combo.Hide()
		self.txtctl.Show()
	
	def on_combo(self, *args):
		"""Value is changed.

		This changes the value of the index in the associated list and
		updates the TextCtrl content.
		"""
		val = self.combo.GetCurrentSelection()
		
		# simple mode update
		if val != self.data[self.index]:
			self.data[self.index] = self.choices[val]
			self.txtctl.SetValue(str(self.data[self.index]))
			self.change_stack[id(self)] = [self.data, self.index]
		self.selected = False
	
	def on_focus(self, *args):
		"""Keeps combo active when control is clicked.
		"""
		self.selected = True

	def on_kill_focus(self, *args):
		"""Hides combo when another window gets focus.
		"""
		self.selected = False
		self.on_mouse_out()

# Sample and test logic ===================================================== #
if __name__ == '__main__':
	"""Create 5 combo controls and place them besides each other.
	"""
	## setup data
	data = ['Watching', 'On Hold']
	change_stack = {}
	print 'Initial data: ', data
	
	## setup controls
	app = wx.PySimpleApp()
	frame = wx.Frame(None, -1)
	x = wx.TextCtrl(frame, -1, size=(0,0))
	frame.SetBackgroundColour(x.GetBackgroundColour())
	
	combos = []
	box = wx.GridSizer(rows=1, cols=2, hgap=0, vgap=0)
	
	# simple combos
	for i in range(2):
		combos.append(combo(frame, data, i, change_stack))
		box.Add(combos[i], -1, wx.ALIGN_CENTER)
	
	frame.SetSizer(box)
	frame.Fit()
	frame.Show()
	
	## run app
	app.MainLoop()

	## print overall data manipulation summary
	print 'New data: ', data
	print 'Change stack: ', change_stack

