from random import randrange
from shared import bytes_to_int

class DataBus:

    def __init__(self, data, writeable=False):

        self.writeable = writeable
        self.size = len(data)
        self.__data = data

    @property
    def data(self):

        return self.__data.copy()

    @data.setter
    def data(self, data):

        if not self.writeable: 
            self.data = bytearray([randrange(0, 0xFF) for _ in range(self.size)])
            return

        self.__data = data

    @property
    def value(self):

        return bytes_to_int(self.data)