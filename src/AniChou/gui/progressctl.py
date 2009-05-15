# =========================================================================== #
# Name:    progressctl.py
# Purpose: progress control widget
#
# Copyright (c) 2009 Sebastian Bartos
#
# License: GPL v3, see COPYING file for details
# =========================================================================== #

import wx

# Progress control widget class declaration ================================= #
class progress(wx.Gauge):
	"""AniChou progress control widget

	This one is pretty basic, AniChou customized Gauge (progress bar)
	"""

	def __init__(self, parent, data, index, s=(90, 25)):
		"""Progress control widget constructor.

		@param parent: parent on which this widget should be displayed
		@param data:   reference to the data list this widget should 
		               interact with
		@param index:  index in the list the spin should manipulate
		               (has to be done this way to call it by reference)
		@param s:      size of the widget
		"""
		
		wx.Gauge.__init__(self, parent, -1, range=100, size = s)

		# setup persistent data
		self.data = data
		self.index = index

		# tell the sizers how to handle this window
		self.SetMinSize(s)
		self.SetMaxSize(s)
		self.SetValue(data[index])

		txtctl = wx.TextCtrl(parent, -1, size=(0,0))
		txtctl.Hide()
		
		# some wx bug workarounds
		self.SetBackgroundColour(txtctl.GetBackgroundColour())
		self.Hide()
		self.Show()

# Sample and test logic ===================================================== #
if __name__ == '__main__':
	"""Create 2 Gauges
	"""
	## setup data
	data = [50, 90]
	print 'Initial data: ', data
	
	## setup controls
	app = wx.PySimpleApp()
	frame = wx.Frame(None, -1)
	x = wx.TextCtrl(frame, -1, size=(0,0))
	frame.SetBackgroundColour(x.GetBackgroundColour())
	
	gauges = []
	box = wx.GridSizer(rows=1, cols=2, hgap=0, vgap=0)
	
	# simple spins
	for i in range(2):
		gauges.append(progress(frame, data, i))
		box.Add(gauges[i], -1, wx.ALIGN_CENTER)
	
	frame.SetSizer(box)
	frame.Fit()
	frame.Show()
	
	## run app
	app.MainLoop()


