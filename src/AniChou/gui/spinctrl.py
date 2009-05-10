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
	"""Autohide spin control widget class.

	This widget is a composite of a SpinCtrl and a TextCtrl. The SpinCtrl
	handles the data manipulation and is shown when the mouse hovers over
	it or it gets focus. The TextCtrl just show the data when not in
	interaction mode.

	Manipulated data is set to the external reference (data) list at index
	(index) position.

	When the conrol changes data, it will add an index to the change
	stack directory with the object id, a reference to the list and the
	index to the changed value. This can be used by a periodic scheduler
	to further update the database.
	"""

	def __init__(self, parent, data, index, change, range=10, s=(90, 25)):
		"""Autohide spin control widget constructor.

		@param parent: parent on which this widget should be displayed
		@param data:   reference to the data list this widget should 
		               interact with
		@param index:  index in the list the spin should manipulate
		               (has to be done this way to call it by reference)
		@param change: change stack, where changes are pushed to
		@param range:  spin max value range
		@param s:      size of the widget
		"""
		wx.Window.__init__(self, parent, -1, size = s)
		
		MAX_RANGE = 999

		# check what type of spin we are, adapt if not simple
		self.simple = True if isinstance(data[index], int) else False
		if not self.simple:
			(value, range) = data[index]
		else:
			value = data[index]
			(w,h) = s
			s = (int(w/1.5), h)

		# setup persistent data
		self.data = data
		self.index = index
		self.range = range
		self.selected = False
		self.change_stack = change

		# tell the sizers how to handle this window
		self.SetMinSize(s)
		self.SetMaxSize(s)

		# initialize controls
		self.spin = spin = \
			wx.SpinCtrl(parent, -1, size = s)
		self.txtctl = txtctl = \
			wx.TextCtrl(parent, -1, size = s)
	
		if range != 0:
			spin.SetRange(0, range)
		else:
			spin.SetRange(0, MAX_RANGE)

		# bind event handlers
		self.Bind(wx.EVT_SIZE, self.on_size)
		self.Bind(wx.EVT_MOVE, self.on_size)
		self.txtctl.Bind(wx.EVT_ENTER_WINDOW, self.on_mouse_in)
		self.spin.Bind(wx.EVT_LEAVE_WINDOW, self.on_mouse_out)
		self.spin.Bind(wx.EVT_TEXT, self.on_spin)
		self.spin.Bind(wx.EVT_SET_FOCUS, self.on_focus)
		self.spin.Bind(wx.EVT_KILL_FOCUS, self.on_kill_focus)

		# setup starting values
		spin.SetValue(value)
		if not self.simple:
			if range == 0: range = '-'
			txtctl.SetValue(str(value) + ' / ' + str(range))
		else:
			txtctl.SetValue(str(value))

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

		This changes the value of the index in the associated list and
		updates the TextCtrl content.
		"""
		val = self.spin.GetValue()
		if val != self.data[self.index] and self.simple:
			self.data[self.index] = val
			self.txtctl.SetValue(str(self.data[self.index]))
			change_stack[id(self)] = [self.data, self.index]
		elif not self.simple:
			(value, range) = self.data[self.index]
			if val != value:
				self.data[self.index] = (val, range)
				if range == 0: range = '-'
				t = str(val) + ' / ' + str(range)
				self.txtctl.SetValue(t)
				change_stack[id(self)] = [self.data, self.index]
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
	# setup data
	data = [5, 6, 0, 0, 10]
	data2 = [(5,50), (129,720), (0,12), (0,0), (10,0)]
	change_stack = {}
	print 'Initial data: ', data, data2
	
	# setup controls
	app = wx.PySimpleApp()
	frame = wx.Frame(None, -1)
	spins = []
	box = wx.GridSizer(rows=2, cols=5, hgap=0, vgap=0)
	for i in range(5):
		spins.append(spin(frame, data, i, change_stack))
		box.Add(spins[i])
	for i in range(5):
		spins.append(spin(frame, data2, i, change_stack))
		box.Add(spins[5+i])
	frame.SetSizer(box)
	frame.Fit()
	frame.Show()
	
	# run app
	app.MainLoop()

	# print overall data manipulation summary
	print 'New data: ', data, data2
	print 'Change stack: ', change_stack

