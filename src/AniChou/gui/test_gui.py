# =========================================================================== #
# Name:	txtctrl.py
# Purpose: text control widget
#
# Copyright (c) 2009 Sebastian Bartos
#
# License: GPL v3, see COPYING file for details
# =========================================================================== #

import wx
import comboctrl,  progressctl,  spinctrl,  txtctrl

if __name__ == '__main__':
	print 'Running ' + __file__ + '..'
	
	print 'Setting up data set..'
	# name, (episode, max), airing status, mystatus, score, progress
	ctls = []
	change_stack = {}
	data = ['Anime foo', (12, 24), 'Airing', 'Watching', 7, 50]
	data2 = ['Bar anithingy', (4, 24), 'Finished', 'Watching', 5, 20]
	print 'data: ' + str(data)
	print 'data2: ' + str(data2)
	
	print 'Setting up frame control..'
	app = wx.PySimpleApp()
	frame = wx.Frame(None, -1)
	x = wx.TextCtrl(frame, -1, size=(0,0))
	frame.SetBackgroundColour(x.GetBackgroundColour())
	x.Hide()
	box = wx.FlexGridSizer(rows=2, cols=6, hgap=0, vgap=0)

	print 'Setting up data controls..'
	ctls.append(txtctrl.txtctrl(frame, data, 0))
	ctls.append(spinctrl.spin(frame, data, 1, change_stack))
	ctls.append(txtctrl.txtctrl(frame, data, 2, s=(50, 25)))
	ctls.append(comboctrl.combo(frame, data, 3, change_stack))
	ctls.append(spinctrl.spin(frame, data, 4, change_stack))
	ctls.append(progressctl.progress(frame, data, 5))
	ctls.append(txtctrl.txtctrl(frame, data2, 0))
	ctls.append(spinctrl.spin(frame, data2, 1, change_stack))
	ctls.append(txtctrl.txtctrl(frame, data2, 2, s=(50, 25)))
	ctls.append(comboctrl.combo(frame, data2, 3, change_stack))
	ctls.append(spinctrl.spin(frame, data2, 4, change_stack))
	ctls.append(progressctl.progress(frame, data2, 5))
	for i in range(6):
		box.Add(ctls[i], -1, wx.ALIGN_CENTER)
	for i in range(6):
		box.Add(ctls[6+i], -1, wx.ALIGN_CENTER)


	print 'Positioning and display setup..'
	frame.SetSizer(box)
	frame.Fit()
	frame.Show()
	
	## run app
	print 'Running main loop..'
	app.MainLoop()

	print 'Changes made:'
	print change_stack

	print __file__+':\n[DONE]'

