r'''    h 16
        /
     h 32 - l 16 ()
     (4, 7)
     /
64 (0, 7)
     \
     l 32
     (0, 3)
'''


from shared import bytes_to_int, int_to_bytes


class x64_Register:

    def __init__(self):

        self.data = bytearray([0] * 8)

    @staticmethod
    def __sec_to_range(sec):

        _range = (0, 7)

        for i in sec:
            avg = (_range[0] + _range[1]) // 2

            if i == 'h':
                _range = (avg+1, _range[1])
            else:
                _range = (_range[0], avg)

        return _range[0], _range[1] + 1

    def __getitem__(self, key):

        if key is int:
            return self.data[key]

        _range = self.__sec_to_range(key)
        return self.data[_range[0]:_range[1]]

    def __setitem__(self, key, value):

        if key is int:
            self.data[key] = value
            return

        _range = self.__sec_to_range(key)
        self.data[_range[0]:_range[1]] = value

        

class ProgramCounter(x64_Register):

    def inc(self):

        self.data = int_to_bytes(bytes_to_int(self.data) + 1).rjust(8, b'\0')

    def jump(self, addr):

        self.data = int_to_bytes(addr).rjust(8, b'\0')


class FlagRegister(x64_Register):

    def __init__(self, overflow=0):

        self.data = bytearray([overflow, *[0x0 for _ in range(7)]])


def test():

    pc = ProgramCounter()
    pc.jump(0x1122334455667788)

    assert pc['']    == b'\x11\x22\x33\x44\x55\x66\x77\x88'
    assert pc['h']   == b'\x55\x66\x77\x88'
    assert pc['l']   == b'\x11\x22\x33\x44'
    assert pc['ll']  == b'\x11\x22'
    assert pc['lh']  == b'\x33\x44'
    assert pc['hl']  == b'\x55\x66'
    assert pc['hh']  == b'\x77\x88'
    assert pc['lll'] == b'\x11'
    assert pc['llh'] == b'\x22'
    assert pc['lhl'] == b'\x33'
    assert pc['lhh'] == b'\x44'
    assert pc['hll'] == b'\x55'
    assert pc['hlh'] == b'\x66'
    assert pc['hhl'] == b'\x77'
    assert pc['hhh'] == b'\x88'

    pc['hhh'] = b'\x99'
    assert pc['hhh'] == b'\x99'
    pc['l'] = b'\x22\x22\x22\x22'
    assert pc['l'] == b'\x22\x22\x22\x22'
    
if __name__ == '__main__': test()
