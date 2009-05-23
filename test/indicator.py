import wx
import indicator

class TestWindow(wx.Frame):
    def __init__(self, parent, id, title):
        wx.Frame.__init__(self, parent, id, title, size=(500, 400))

#        pa = wx.Panel(self, -1)
        li = indicator.StarIndicator(self, -1, size=(200, 20))
        li.maximum = 10
        li.editable = True
        li.expand = False
        
        self.Centre()
        self.Show()

app = wx.App()
TestWindow(None, -1, 'Aliens')
app.MainLoop()