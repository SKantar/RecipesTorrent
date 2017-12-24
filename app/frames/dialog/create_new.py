import wx
import base64

class CreateNewDialog(wx.Dialog):

    def __init__(self, *args, **kw):

        self.types = kw["types"]
        kw_cpy = kw.copy()
        del kw_cpy["types"]


        super(CreateNewDialog, self).__init__(*args, **kw_cpy)
        self.InitUI()
        self.SetSize((500, 550))
        self.SetTitle("Create New Recipe")
        self.recipe = {}

    def InitUI(self):

        pnl = wx.Panel(self, size=(500, 550))
        vbox = wx.BoxSizer(wx.VERTICAL)

        wx.StaticText(pnl, -1, 'Title', (20, 20))
        wx.StaticText(pnl, -1, 'Type', (20, 60))
        wx.StaticText(pnl, -1, 'Picture', (20, 100))
        wx.StaticText(pnl, -1, 'Ingredients', (20, 140))

        self.title = wx.TextCtrl(pnl, -1, '', (130, 15), (350, 36))
        self.type = wx.ComboBox(pnl, -1, '', (130, 55), size=(350, 36), choices=self.types, style=wx.ALIGN_CENTER)

        self.file = wx.FilePickerCtrl(pnl, wx.ID_ANY, pos=(130, 95), size=(350, 36))
        self.ingredients = wx.TextCtrl(pnl, -1, '', (130, 135), (350, 72), style=wx.TE_MULTILINE)
        self.description = wx.TextCtrl(pnl, -1, 'Description...', (20, 212), (460, 264), style=wx.TE_MULTILINE)

        wx.Button(pnl, 1, 'Create', (240, 500), (120, -1))
        wx.Button(pnl, 2, 'Cancel', (360, 500), (120, -1))

        self.Bind(wx.EVT_BUTTON, self.OnCreate, id=1)
        self.Bind(wx.EVT_BUTTON, self.OnCancel, id=2)

        self.SetSizer(vbox)

    def OnCreate(self, event):
        picture = ""
        if self.file.GetPath():
            with open(self.file.GetPath(), "rb") as imageFile:
                picture = base64.b64encode(imageFile.read())


        self.recipe.update({
            "title" : self.title.GetValue(),
            "type" : self.type.GetValue(),
            "picture" : picture,
            "ingredients" : self.ingredients.GetValue(),
            "description" : self.description.GetValue()
        })
        self.Close()

    def OnCancel(self, event):
        self.Close()
