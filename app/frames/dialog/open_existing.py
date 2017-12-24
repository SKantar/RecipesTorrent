import wx
import base64
import tempfile

def scale_bitmap(bitmap, width, height):
    image = wx.ImageFromBitmap(bitmap)
    image = image.Scale(width, height, wx.IMAGE_QUALITY_HIGH)
    result = wx.BitmapFromImage(image)
    return result

class OpenRecipeDialog(wx.Dialog):
    def __init__(self, *args, **kw):

        self.obj = kw["object"]
        kw_cpy = kw.copy()
        del kw_cpy["object"]

        super(OpenRecipeDialog, self).__init__(*args, **kw_cpy)
        self.InitUI()
        self.SetSize((500, 550))
        self.SetTitle("Recipe")

    def InitUI(self):

        pnl = wx.Panel(self, size=(500, 550))
        vbox = wx.BoxSizer(wx.VERTICAL)

        wx.StaticText(pnl, -1, "Title:", (240, 20) , (240, -1))
        wx.StaticText(pnl, -1, self.obj["title"], (240, 50), (240, -1))
        wx.StaticText(pnl, -1, "Type:", (240, 90), (240, -1))
        wx.StaticText(pnl, -1, self.obj["type"], (240, 120), (240, -1))
        wx.StaticText(pnl, -1, "Ingredients:", (240, 160), (240, -1))
        wx.StaticText(pnl, -1, self.obj["ingredients"], (240, 190), (240, -1))
        wx.StaticText(pnl, -1, "Method of preparation:", (20, 240), (240, -1))
        wx.StaticText(pnl, -1, self.obj["description"], (20, 270), (240, -1))

        if self.obj["picture"]:
            imageFile = base64.b64decode(self.obj["picture"])

            fileout = tempfile.NamedTemporaryFile(delete=False)
            fileout.write(imageFile)
            fileout.close()

            image = scale_bitmap(wx.Image(fileout.name).ConvertToBitmap(), 200, 200)
            wx.StaticBitmap(pnl, -1, image, (20, 20), (200, 200))


        wx.Button(pnl, 2, 'Cancel', (360, 500), (120, -1))

        self.Bind(wx.EVT_BUTTON, self.OnCancel, id=2)

        self.SetSizer(vbox)

    def OnCancel(self, event):
        self.Close()