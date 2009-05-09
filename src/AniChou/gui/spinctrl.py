# =========================================================================== #
# Name:    spinctrl.py
# Purpose: autohide spin control widget declaration module
#
# Copyright (c) 2009 Sebastian Bartos
#
# License: GPL v3, see COPYING file for details
# =========================================================================== #

import wx

# Autohide spin control class declaration =================================== #
class spin(wx.Window):

	def __init__(self, parent, data, entry, range=10, width=50, height=25):
		"""Autohide spin control widget constructor.

		@param parent: parent on which this widget should be displayed
		@param data:   reference to the data list this widget should 
		               interact with
		@param entry:  entry in the list the spin should manipulate
		               (has to be done this way to call it by reference)
		@param range:  spin max value range
		@param width:  width of the widget
		@param height: height of the widget
		"""
		wx.Window.__init__(self, parent, -1, size = (width, height))

		self.data = data
		self.entry = entry
		self.range = range
		self.selected = False

		# initialize controls
		self.spin = spin = \
			wx.SpinCtrl(parent, -1, size = (width, height))
		self.txtctl = txtctl = \
			wx.TextCtrl(parent, -1, size = (width, height))
	
		spin.SetRange(0, range)

		# bind event handlers
		self.Bind(wx.EVT_SIZE, self.on_size)
		self.txtctl.Bind(wx.EVT_ENTER_WINDOW, self.on_mouse_in)
		self.spin.Bind(wx.EVT_LEAVE_WINDOW, self.on_mouse_out)
		self.spin.Bind(wx.EVT_TEXT, self.on_spin)
		self.spin.Bind(wx.EVT_SET_FOCUS, self.on_focus)
		self.spin.Bind(wx.EVT_KILL_FOCUS, self.on_kill_focus)

		# setup starting values
		spin.SetValue(data[entry])
		txtctl.SetValue(str(data[entry]))

	def on_size(self, *args):
		"""Called when the window changes size/position.

		This event handler is called when the sizers push around the
		window. It places the child widgets to the correct position.
		"""
		self.txtctl.SetPosition(self.GetPosition())
		self.spin.SetPosition(self.GetPosition())

	def on_mouse_in(self, *args):
		"""Mouse enters window area.
		"""
		self.txtctl.Hide()
		self.spin.Show()

	def on_mouse_out(self, *args):
		"""Mouse leaves window area
		"""
		if not self.selected:
			self.spin.Hide()
			self.txtctl.Show()
	
	def on_spin(self, *args):
		"""Value is changed.

		This changes the value of the entry in the assosiated list and
		updates the TextCtrl content.
		"""
		self.data[self.entry] = self.spin.GetValue()
		self.txtctl.SetValue(str(self.data[self.entry]))
		self.selected = False
	
	def on_focus(self, *args):
		"""Keeps spin active when control is clicked.
		"""
		self.selected = True

	def on_kill_focus(self, *args):
		"""Hides spin when another window gets focus.
		"""
		self.selected = False
		self.on_mouse_out()

# Sample and test logic ===================================================== #
if __name__ == '__main__':
	"""Create 5 spin controls and place them besides each other.
	"""
	app = wx.PySimpleApp()
	frame = wx.Frame(None, -1)
	data = [5, 6, 4, 0, 10]
	print 'Initial data: ', data
	spin1 = spin(frame, data, 0)
	spin2 = spin(frame, data, 1)
	spin3 = spin(frame, data, 2)
	spin4 = spin(frame, data, 3)
	spin5 = spin(frame, data, 4)
	box = wx.BoxSizer(wx.HORIZONTAL)
	box.Add(spin1)
	box.Add(spin2)
	box.Add(spin3)
	box.Add(spin4)
	box.Add(spin5)
	frame.SetSizer(box)
	frame.Show()
	app.MainLoop()
	print 'New data: ', data

