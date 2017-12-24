import hashlib
import random
from config import *
from id_hashing import ID


def hash_function(data1, data2):
    d1 = d2 = ''
    if data1:
        d1 = data1
    if data2:
        d2 = data2
    id = str(d1) + str(d2)
    if len(id) < 32:
        for i in range(len(id), 32):
            id += '0'
    return ID(id).get_long_id()


def hash_function_partial(data):
    return ID(str(data)).get_long_id(), hash_function(data, None), len(data)

def random_id(seed=None):
    if seed:
        random.seed(seed)
    return random.randint(0, (2 ** id_bits)-1)
