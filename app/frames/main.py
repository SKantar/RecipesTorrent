import wx
from dialog.create_new import CreateNewDialog
from dialog.open_existing import OpenRecipeDialog
from dialog.search import SearchDialog
from client.dht.pydht import DHT
from client.dht.hashing import hash_function
from client.dht.config import BOOTSTRAP_HOST
from urllib2 import urlopen
import os
import pickle
from os.path import isfile, join

from threading import Thread
import time
from wx.lib.pubsub import pub
test = 0

EVT_RESULT_ID = wx.NewId()


def EVT_RESULT(win, func):
    """Define Result Event."""
    win.Connect(-1, -1, EVT_RESULT_ID, func)


class ResultEvent(wx.PyEvent):
    """Simple event to carry arbitrary result data."""

    def __init__(self, data):
        """Init Result Event."""
        wx.PyEvent.__init__(self)
        self.SetEventType(EVT_RESULT_ID)
        self.data = data


class TestThread(Thread):
    """Test Worker Thread Class."""

    # ----------------------------------------------------------------------
    def __init__(self, wxObject):
        """Init Worker Thread Class."""
        Thread.__init__(self)
        self.wxObject = wxObject
        self.start()  # start the thread

    # ----------------------------------------------------------------------
    def run(self):
        """Run Worker Thread."""
        i = 0
        while not self.wxObject.dht.connected:
            time.sleep(1)
            i += 1
            if i > 10:
                break
            print i
        if i < 60:
            wx.PostEvent(self.wxObject, ResultEvent("Thread finished!"))

class MyStatusBar(wx.StatusBar):
    def __init__(self, parent):
        wx.StatusBar.__init__(self, parent)

        self.SetFieldsCount(2)
        self.SetStatusText('Welcome to Raf Chef', 0)
        self.SetStatusWidths([-5, -2])
        self.icon = wx.StaticBitmap(self, -1, wx.Bitmap('icons/disconnected.png'))
        self.Bind(wx.EVT_SIZE, self.OnSize)
        self.PlaceIcon()

        # pub.subscribe(self.OnSize, "panelListener")

    def PlaceIcon(self):
        rect = self.GetFieldRect(1)
        self.icon.SetPosition((rect.x+3, rect.y+3))

    def OnSize(self, event):
        self.PlaceIcon()

class ListCtrlLeft(wx.ListCtrl):
    def __init__(self, parent, id, types):
        wx.ListCtrl.__init__(self, parent, id, style=wx.LC_REPORT | wx.LC_HRULES | wx.LC_NO_HEADER | wx.LC_SINGLE_SEL)

        # types = [key for key, value in categories.iteritems()]

        self.parent = parent

        self.Bind(wx.EVT_SIZE, self.OnSize)
        self.Bind(wx.EVT_LIST_ITEM_SELECTED, self.OnSelect)

        self.InsertColumn(0, '')

        for i in range(len(types)):
            self.InsertStringItem(0, types[i])

    def OnSize(self, event):
        size = self.parent.GetSize()
        self.SetColumnWidth(0, size.x-5)
        event.Skip()

    def OnSelect(self, event):
        window = self.parent.GetGrandParent().FindWindowByName('ListControlOnRight')
        index = event.GetIndex()
        window.LoadData(index)

    def OnDeSelect(self, event):
        index = event.GetIndex()
        self.SetItemBackgroundColour(index, 'WHITE')

    def OnFocus(self, event):
        self.SetItemBackgroundColour(0, 'red')

class ListCtrlRight(wx.ListCtrl):
    def __init__(self, parent, id, types, dht):
        wx.ListCtrl.__init__(self, parent, id, style=wx.LC_REPORT | wx.LC_HRULES | wx.LC_NO_HEADER | wx.LC_SINGLE_SEL)
        self.dht = dht
        self.types = types
        self.parent = parent
        self.Bind(wx.EVT_SIZE, self.OnSize)
        self.InsertColumn(0, '')

        self.Bind(wx.EVT_LEFT_DCLICK, self.OnClick)


    def OnSize(self, event):
        size = self.parent.GetSize()
        self.SetColumnWidth(0, size.x-5)
        event.Skip()

    def LoadData(self, index):
        self.DeleteAllItems()
        for key, value in self.dht.data.iteritems():
            if value["type"] == self.types[len(self.types) - 1 - index]:
                self.InsertStringItem(0, value["title"])

    def OnClick(self, event):
        name = self.GetItem(itemId=self.FocusedItem, col=0).GetText()
        type = self.Parent.Parent.Parent.Parent.list1.GetItem(itemId=self.Parent.Parent.Parent.Parent.list1.FocusedItem, col=0).GetText()
        chgdep = OpenRecipeDialog(None, object=self.dht["%s%s"%(type,name)], title='Open Recipe')
        chgdep.ShowModal()
        chgdep.Destroy()

class Main(wx.Frame):
    def __init__(self, parent, id, title, login_data, categories, storage, store=False):
        wx.Frame.__init__(self, parent, id, title, size=(800, 600))



        ip = BOOTSTRAP_HOST #urlopen('http://ip.42.pl/raw').read()
        port = int(login_data["port"])
        region = login_data["region"]

        # self.types = [key for key, value in categories.iteritems()]

        files = [f for f in os.listdir(storage) if isfile(join(storage, f))]

        if not store:
            login_file = open(("%s/login.pkl" % storage), 'rb')
            login_data = pickle.load(login_file)
            self.dht = DHT(ip, port, region, id=login_data["id"], storage=storage)
        else:
            self.dht = DHT(ip, port, region, id=-1, storage=storage)
            login_data["id"] = self.dht.id
            output = open("%s/login.pkl" % storage, 'wb')
            pickle.dump(login_data, output)
            output.close()

        self.types = categories


        for file_name in files:
            if file_name != "login.pkl":
                file = open(("%s/%s" % (storage, file_name)), 'rb')
                object = pickle.load(file)
                file.close()
                self.dht.data[hash_function(object["type"], object["title"])] = object


        hbox = wx.BoxSizer(wx.HORIZONTAL)
        splitter = wx.SplitterWindow(self, -1, style=wx.SP_LIVE_UPDATE|wx.SP_NOBORDER)

        vbox1 = wx.BoxSizer(wx.VERTICAL)

        self.panel1 = wx.Panel(splitter, -1)
        panel11 = wx.Panel(self.panel1, -1, size=(-1, 40))
        panel11.SetBackgroundColour('#53728c')
        st1 = wx.StaticText(panel11, -1, 'Categories', (5, 5))
        st1.SetForegroundColour('WHITE')

        panel12 = wx.Panel(self.panel1, -1, style=wx.SIMPLE_BORDER)
        vbox = wx.BoxSizer(wx.VERTICAL)
        self.list1 = ListCtrlLeft(panel12, -1, self.types)

        vbox.Add(self.list1, 1, wx.EXPAND)
        panel12.SetSizer(vbox)
        panel12.SetBackgroundColour('WHITE')

        vbox1.Add(panel11, 0, wx.EXPAND)
        vbox1.Add(panel12, 1, wx.EXPAND)

        self.panel1.SetSizer(vbox1)

        vbox2 = wx.BoxSizer(wx.VERTICAL)

        self.panel2 = wx.Panel(splitter, -1)
        panel21 = wx.Panel(self.panel2, -1, size=(-1, 40), style=wx.NO_BORDER)
        st2 = wx.StaticText(panel21, -1, 'Recipes', (5, 5))
        st2.SetForegroundColour('WHITE')
        panel21.SetBackgroundColour('#53728c')

        panel22 = wx.Panel(self.panel2, -1, style=wx.SIMPLE_BORDER)
        vbox3 = wx.BoxSizer(wx.VERTICAL)

        self.list2 = ListCtrlRight(panel22, -1, self.types, self.dht)
        self.list2.SetName('ListControlOnRight')
        vbox3.Add(self.list2, 1, wx.EXPAND)
        panel22.SetSizer(vbox3)
        panel22.SetBackgroundColour('WHITE')
        vbox2.Add(panel21, 0, wx.EXPAND)
        vbox2.Add(panel22, 1, wx.EXPAND)

        self.panel2.SetSizer(vbox2)

        self.toolbar = self.CreateToolBar()
        self.toolbar.AddLabelTool(1, 'New', wx.Bitmap('icons/new.png'))
        self.toolbar.AddLabelTool(3, 'Open', wx.Bitmap('icons/search.png'))
        self.toolbar.AddLabelTool(2, 'Exit', wx.Bitmap('icons/exit.png'))
        self.toolbar.Realize()

        self.toolbar.EnableTool(1, False)
        self.toolbar.EnableTool(2, False)
        self.toolbar.EnableTool(3, False)
        #
        self.Bind(wx.EVT_TOOL, self.NewRecipe, id=1)
        self.Bind(wx.EVT_TOOL, self.ExitApp, id=2)
        self.Bind(wx.EVT_TOOL, self.OpenRecipe, id=3)

        hbox.Add(splitter, 1, wx.EXPAND | wx.TOP | wx.BOTTOM, 5)
        self.SetSizer(hbox)

        self.statusbar = MyStatusBar(self)
        self.SetStatusBar(self.statusbar)

        EVT_RESULT(self, self.enable)

        splitter.SplitVertically(self.panel1, self.panel2)
        self.Centre()
        self.Show(True)

        TestThread(self)


    def enable(self, msg):
        self.toolbar.EnableTool(1, True)
        self.toolbar.EnableTool(2, True)
        self.toolbar.EnableTool(3, True)
        self.statusbar.SetStatusText('User connected')
        self.statusbar.icon.SetBitmap(wx.Bitmap('icons/connected.png'))
        self.Update()

    def ExitApp(self, event):
        self.Close()

    def NewRecipe(self, event):
        chgdep = CreateNewDialog(None, types=self.types, title='Create New')
        chgdep.ShowModal()
        if chgdep.recipe:
            if chgdep.recipe["title"] in self.types:
                dlg = wx.MessageDialog(self, "You cant create recipe with name %s" % chgdep.recipe["title"], "Confirm Exit", wx.OK | wx.CANCEL | wx.ICON_QUESTION)
                dlg.ShowModal()
                dlg.Destroy()
            else:
                self.dht[chgdep.recipe["title"]] = chgdep.recipe
                index = len(self.types) - 1 - self.types.index(chgdep.recipe["type"])
                self.list1.Select(index)
                self.list2.LoadData(index)
        chgdep.Destroy()

    def OpenRecipe(self, event):
        chgdep = SearchDialog(None, types=self.types, title='Search')
        chgdep.ShowModal()
        if chgdep.result:
            recipe = self.dht[chgdep.result]
            if recipe:
                chgdep = OpenRecipeDialog(None, object=recipe, title='Open Recipe')
                chgdep.ShowModal()
                chgdep.Destroy()
        chgdep.Destroy()
