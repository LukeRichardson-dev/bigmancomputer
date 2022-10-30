from math import ceil, log
from data_bus import DataBus
from registers import FlagRegister, x64_Register

from shared import bytes_to_int, int_to_bytes


class UnsignedInteger:

    @classmethod
    def from_bits(cls, bits):

        return cls(sum([(bit == '1') << idx for idx, bit in enumerate(bits[::-1])]), size=len(bits))

    def __init__(self, value, size=None):
        
        self.size = size if size is not None else ceil(log(value+1, 2**8))
        self.value = value

    def as_bits(self):
        
        return "".join(["1" if 0x1 << i & self.value else "0" for i in range(self.size)][::-1])

class SignedInteger:

    def __init__(self, binary):
        self.size = len(binary)

        num = 0
        is_compliament = binary[0] == "1"
        for idx, bit in enumerate(binary[1:][::-1]):

            if (bit == "1") ^ is_compliament:
                num |= 0x1 << idx

        if is_compliament:
            num = -(num + 1)

        self.value = num

    def as_bits(self):

        num = self.value
        bits = ""

        is_compliament = num != abs(num)
        if is_compliament:
            num = -(num + 1)

        while num != 0:

            mask = 0x1 << len(bits)
            is_one = num & mask
            num ^= is_one
            bits = ("1" if is_one ^ (mask * is_compliament) else "0") + bits

        return ("1" if is_compliament else "0") + bits

    def __str__(self):

        return self.value.__str__()

class FloatingPoint:

    @classmethod
    def from_bits(cls, mantissa, exponent):

        return cls(
            SignedInteger(mantissa),
            SignedInteger(exponent),
        )

    def __init__(self, mantissa, exponent):

        self.mantissa = mantissa
        self.exponent = exponent

    def as_real(self):

        return (self.mantissa.value / 2**self.mantissa.size) * (2 ** self.exponent.value)


class ALU:

    def run(self, code, buses, flags_reg):

        if code == 0b00010000:
            self.uadd(
                next(buses),
                next(buses),
                next(buses),
                flags_reg
            )
                
    
    @staticmethod
    def uadd(ibus1, ibus2, obus, flags):
        nbytes = len(ibus1.data)
        new = bytes_to_int(ibus1.data) + bytes_to_int(ibus2.data)
        new_bytes = int_to_bytes(new).rjust(nbytes, b'\0')

        if len(new_bytes) > nbytes:
            overflow, *new_bytes = new_bytes
            flags['lll'] = [overflow]

        obus.data = new_bytes


def test():

    reg = x64_Register()
    reg['l'] = b'\x00\x00\x00\x0f'
    reg['h'] = b'\x00\x00\x00\x0f'

    flags = FlagRegister(0)

    alu = ALU()
    obus = DataBus(reg['l'], True)
    alu.run(
        0b00010000,
        iter( [ DataBus(reg['l']),
                DataBus(reg['h']),
                obus ] ),
        flags
    )

    reg['l'] = obus.data
    assert reg['l'] == b'\x00\x00\x00\x1e'

    reg['h'] = b'\xff\xff\xff\xff'
    obus = DataBus(reg['l'], True)
    alu.run(
        0b00010000,
        iter( [ DataBus(reg['l']),
                DataBus(reg['h']),
                obus ] ),
        flags
    )
    reg['l'] = obus.data

    assert flags['lll'] == b'\x01'
    assert reg['l'] == b'\x00\x00\x00\x1d'


if __name__ == '__main__': test()
