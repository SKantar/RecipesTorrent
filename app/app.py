from frames.main import Main
from frames.login import Login
import wx
from utils.utils import get_storage_path, get_files, load_object
from client.dht.config import regions, category_names
storage_path = get_storage_path()

app = wx.App()

if 'login.pkl' in get_files(storage_path):
    login_data = load_object("%s/login.pkl" % storage_path)
    Main(None, -1, 'Raf Chef', login_data, category_names, storage_path)
else:

    Login(None, -1, 'Connect', regions, category_names, storage_path)

app.MainLoop()
