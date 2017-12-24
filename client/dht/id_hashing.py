from random import choice
from string import ascii_letters
from array import array

class ID(object):

    ID_LENGTH = 256

    def __init__(self, id=None):
        if id == None:
            id = ''.join(choice(ascii_letters) for i in range(self.ID_LENGTH / 8))

        # if len(id) != self.ID_LENGTH / 8:
        #     raise ValueError("Specified Data need to be '%s' characters long." % (self.ID_LENGTH / 8))

        self.__id = str(id)
        self.__long_id = long('0x%s' % id.encode('hex'), 0)
        self.__num_chars = len(str(id))

    def get_long_id(self):
        return self.__long_id

    def get_long_id_and_n(self):
        return self.__long_id, self.__num_chars

    def get_id(self):
        return self.__id

    def get_first_set_bit_index(self, number):
        prefix_length = 0
        marker = long("0x80000000000000000000000000000000", 16)
        while number & marker == 0 and prefix_length <= 128:
            number = number << 1
            prefix_length += 1
        return prefix_length

    def get_distance(self, to):
        return self.ID_LENGTH - self.get_first_set_bit_index(long(self.__long_id ^ to.get_long_id()))

    def __hash__(self):
        hash = 7
        hash = 83 * hash + self.__hash_array()
        return hash

    def __repr__(self):
        return self.__long_id

    def __hash_array(self):
        if len(self.__id) == 0:
            return 0
        result = 1
        hash_array = array('B', self.__id)
        for element in hash_array:
            result = 31 * result + element
        return result % (2 * 2147483648)

    def __lt__(self, other):
        return self.__long_id < other.get_long_id()

    def __le__(self, other):
        return self.__long_id <= other.get_long_id()

    def __eq__(self, other):
        return self.__long_id == other.get_long_id()

    def __ne__(self, other):
        return self.__long_id != other.get_long_id()

    def __gt__(self, other):
        return self.__long_id > other.get_long_id()

    def __ge__(self, other):
        return self.__long_id >= other.get_long_id()

    def __sub__(self, other):
        return self.__long_id ^ other.get_long_id()

    def __str__(self):
        return '%s' % hex(self.__long_id)[2:]


# id1 = ID("Germany-100987654321")
# id2 = ID("Germany-123456789010")
# id3 = ID("Barcelona-1234567890")
# print id1
# print id2
# print id3
#
# print "=================================="
# print '%s' % hex(id1 - id2)[2:]
# print '%s' % hex(id3 - id1)[2:]
