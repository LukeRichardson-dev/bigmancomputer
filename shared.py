from math import ceil, log


def bytes_to_int(_bytes):

    return sum([b << (8 * idx) for idx, b in enumerate(_bytes[::-1])])

def int_to_bytes(num):

    return bytearray([0xFF & (num >> i) for i in range(0, 8 * get_order(num, 2**8), 8)][::-1])

def get_order(num, order):

    return ceil(log(num+1, order))