import wx

class SearchDialog(wx.Dialog):

    def __init__(self, *args, **kw):

        self.types = kw["types"]
        kw_cpy = kw.copy()
        del kw_cpy["types"]


        super(SearchDialog, self).__init__(*args, **kw_cpy)
        self.InitUI()
        self.SetSize((500, 300))
        self.SetTitle("Search")
        self.result = ""

    def InitUI(self):

        pnl = wx.Panel(self, size=(500, 300))
        vbox = wx.BoxSizer(wx.VERTICAL)

        wx.StaticText(pnl, -1, 'Title', (20, 100))
        wx.StaticText(pnl, -1, 'Type', (20, 20))

        self.title = wx.TextCtrl(pnl, -1, '', (20, 140), (460, 36))
        self.type = wx.ComboBox(pnl, -1, '', (20, 60), size=(460, 36), choices=self.types, style=wx.ALIGN_CENTER)

        wx.Button(pnl, 1, 'Search', (240, 250), (120, -1))
        wx.Button(pnl, 2, 'Cancel', (360, 250), (120, -1))

        self.Bind(wx.EVT_BUTTON, self.OnCreate, id=1)
        self.Bind(wx.EVT_BUTTON, self.OnCancel, id=2)

        self.SetSizer(vbox)

    def OnCreate(self, event):
        self.result =  "%s%s" % (self.type.GetValue(), self.title.GetValue())
        self.Close()

    def OnCancel(self, event):
        # pass
        self.Close()