
import os
from os.path import isfile, join
import pickle

def create_folder(path):
    try:
        os.makedirs(path)
    except OSError:
        pass

def get_storage_path():
    path = os.path.dirname(os.path.dirname(__file__)) + "/storage"
    create_folder(path)
    return path

def get_files(path):
    return [f for f in os.listdir(path) if isfile(join(path, f))]

def store_object(object, path):
    output = open(path, 'wb')
    pickle.dump(object, output)

def load_object(path):
    file = open(path, 'rb')
    object = pickle.load(file)
    file.close()
    return object