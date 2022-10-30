from data_bus import DataBus
from registers import FlagRegister, ProgramCounter, x64_Register
from memory import Memory


class Registers:

    def __init__(self, *, gpr=16):
        
        self.program_counter = ProgramCounter()
        self.flags = FlagRegister()
        self.general_registers = [ x64_Register() for _ in range(gpr) ]

    @property
    def mapping(self):
        return {
            'pc': self.program_counter,
            'fl': self.flags,
            **{f'{idx:0>2x}': reg for idx, reg in enumerate(self.general_registers)}, 
        }  

    @staticmethod
    def to_bytes(_repr: str):

        ab, mask = _repr[:2], _repr[2:]
        mask_bits = sum((bit == 'h') << idx for idx, bit in enumerate(mask)) << 2

        b1 = 0
        b1 |= len(mask)
        b1 |= mask_bits
        b1 |= 0b10000000

        return bytearray([b1, ord(ab[0]), ord(ab[1])])

    '''
        First bit for other stuff: ignore it.
        Last two bits are sector size.
        bits before are sector mask (Note that these are in reverse).
    '''
    @staticmethod
    def from_bytes(b1, b2, b3):

        sector_size = b1 & 0b00000011
        sector = "".join('h' if ((0x1 << i) & b1) else 'l' for i in range(2, 2+sector_size))
    
        code = chr(b2) + chr(b3)
        return code, sector

    def __getitem__(self, code):

        return self.mapping[code]


def test_registers():

    regs = Registers()
    assert regs.from_bytes(0b10011111, 65+32, 66+32) == ('ab', 'hhh')
    assert regs.from_bytes(0b10000000, 66+32, 67+32) == ('bc', ''   )
    assert regs.from_bytes(0b10001110, 67+32, 68+32) == ('cd', 'hh' )
    assert regs.from_bytes(0b10000001, 68+32, 65+32) == ('da', 'l'  )
    
    assert regs.to_bytes('abhhh') == bytearray([0b10011111, 65+32, 66+32])
    assert regs.to_bytes('bc'   ) == bytearray([0b10000000, 66+32, 67+32])
    assert regs.to_bytes('cdhh' ) == bytearray([0b10001110, 67+32, 68+32])
    assert regs.to_bytes('dal'  ) == bytearray([0b10000001, 68+32, 65+32])


class ControlUnit:

    def __init__(self, *, gpr=16, memsize=524288):

        self.registers = Registers(gpr=gpr)
        self.memory = Memory.zeros(memsize)

    def set_mem(self, memory):

        self.memory = memory

    def __next__(self):

        pc = self.registers.program_counter
        addr_bus = DataBus(pc[''], False)
        data_bus = DataBus(bytearray([0]), True)
        out_bus = self.memory.present(addr_bus, data_bus)
        pc.inc()
        return out_bus.data[0]

    def run(self):

        self.registers.program_counter.jump(0)

        while True:

            instruction = next(self)

            if instruction == 0x00:  # HALT
                break

            elif instruction == 0x01: # OUTU
                new = next(self)
                print(new)

            elif instruction == 0x02: # OUTC
                new = next(self)
                print(chr(new), end='')

            elif instruction == 0x03: # COUT
                while (new := next(self)):
                    print(chr(new), end='')

            elif instruction == 0x04: # MOUT
                _, data = self.stream_to_data(self)
                print(", ".join(str(i) for i in data), end='')

            elif instruction == 0x05: # STA
                (is_reg, *other), data = self.stream_to_data(self)
                size = 8 * 2**(3 - len(other[2])) if is_reg else other[1]


    def stream_to_data(self, stream):

        is_reg, *other = self.dereference(stream)

        if is_reg:
            code, sector = other[0]
            return (True, code, sector), self.registers[code][sector]
            
        else:
            size, address = other
            data = self.memory.present(
                DataBus(address), 
                DataBus([0]*size, True)
            ).data
            return (False, size, address), data

    def dereference(self, bytestream):

        b1 = next(bytestream)
        if b1 & 0b10000000:
            b2 = next(bytestream)
            b3 = next(bytestream)
            return True, self.registers.from_bytes(b1, b2, b3)

        size = next(bytestream)
        address = [next(bytestream) for _ in range(4)]
        return False, size, address




def test_cu():

    cu = ControlUnit()
    cu.registers['01']['ll'] = b'hi'
    cu.set_mem(Memory(
        [0x04, *(cu.registers.to_bytes('01'))] + [0x00] * (2 ** 16)
    ))
    cu.run()

if __name__ == '__main__': 
    test_registers()
    test_cu()