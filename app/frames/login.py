from main import Main

import wx
import pickle

class Login(wx.Frame):

    def __init__(self, parent, id, title, regions, categories, storage):
        wx.Frame.__init__(self, parent, id, title, size=(400, 300))
        self.storage = storage
        self.categories = categories
        self.InitUI(regions)
        self.SetTitle("Connect to Network")
        self.Centre()
        self.Show(True)

    def InitUI(self, regions):
        pnl = wx.Panel(self, size=(400, 300))
        vbox = wx.BoxSizer(wx.VERTICAL)
        wx.StaticText(pnl, -1, 'Region', (20, 40))
        wx.StaticText(pnl, -1, 'Port', (20, 110))
        self.region = wx.ComboBox(pnl, -1, '', (20, 70), size=(350, 36), choices=regions, style=wx.ALIGN_CENTER)
        self.port = wx.TextCtrl(pnl, -1, '', (20, 140), (350, 36))

        wx.Button(pnl, 1, 'Connect', (130, 240), (120, -1))
        wx.Button(pnl, 2, 'Cancel', (250, 240), (120, -1))

        self.Bind(wx.EVT_BUTTON, self.onConnect, id=1)
        self.Bind(wx.EVT_BUTTON, self.OnCancel, id=2)

        self.SetSizer(vbox)

    def OnCancel(self, event):
        self.Close()

    def onConnect(self, evemt):

        login_data = {
            "port": self.port.GetValue(),
            "region": self.region.GetValue(),
            "id": -1
        }

        self.Close()
        Main(None, -1, 'Raf Chef', login_data, self.categories, self.storage, store=True)

