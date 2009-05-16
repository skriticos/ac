# =========================================================================== #
# Name:	txtctrl.py
# Purpose: text control widget
#
# Copyright (c) 2009 Sebastian Bartos
#
# License: GPL v3, see COPYING file for details
# =========================================================================== #

import wx

# Progress control widget class declaration ================================= #
class txtctrl(wx.TextCtrl):
	"""AniChou text control widget

	Text control widgets for anime name.
	"""

	def __init__(self, parent, data, index, s=(200, 25)):
		"""Text control widget constructor.

		@param parent: parent on which this widget should be displayed
		@param data:   reference to the data list this widget should 
					   interact with
		@param index:  index in the list the spin should manipulate
					   (has to be done this way to call it by reference)
		@param s:	  size of the widget
		"""
		
		wx.TextCtrl.__init__(self, parent, -1, size = s,
					style = wx.NO_BORDER)

		# setup persistent data
		self.data = data
		self.index = index

		# tell the sizers how to handle this window
		self.SetMinSize(s)
		self.SetMaxSize(s)
		self.SetValue(data[index])
		
		# some wx bug workarounds
		# self.SetBackgroundColour(txtctl.GetBackgroundColour())
		self.Hide()
		self.Show()

# Sample and test logic ===================================================== #
if __name__ == '__main__':
	"""Create 2 text controls
	"""
	## setup data
	data = ["txt foo", "airing"]
	print 'Initial data: ', data
	
	## setup controls
	app = wx.PySimpleApp()
	frame = wx.Frame(None, -1)
	x = wx.TextCtrl(frame, -1, size=(0,0))
	frame.SetBackgroundColour(x.GetBackgroundColour())
	
	txts = []
	box = wx.GridSizer(rows=1, cols=2, hgap=0, vgap=0)
	
	# add controls
	txts.append(txtctrl(frame, data, 0))
	box.Add(txts[0], -1, wx.ALIGN_CENTER)
	txts.append(txtctrl(frame, data, 1, s=(50, 25)))
	box.Add(txts[1], -1, wx.ALIGN_CENTER)
	
	frame.SetSizer(box)
	frame.Fit()
	frame.Show()
	
	## run app
	app.MainLoop()


