
from random import randrange
from data_bus import DataBus


class Memory:

    @classmethod
    def zeros(cls, size, *, difficulty=1):

        return cls(b'\0' * size, difficulty=difficulty)

    @classmethod
    def random(cls, size, *, difficulty=1):

        return cls(bytearray([randrange(0, 0xFF) for _ in range(size)]), difficulty=difficulty)

    def __init__(self, _bytes, *, difficulty=1):

        self.difficulty = difficulty # TODO
        self.size = len(_bytes)
        self.__memory = bytearray(_bytes)

    def present(self, addr_bus, data_bus):
        
        addr = addr_bus.value
        if data_bus.writeable:

            return DataBus(self.__memory[addr:addr+data_bus.size])

        self.__memory[addr:addr+addr.size] = data_bus.data
