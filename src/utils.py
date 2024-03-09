import hashlib

def encode_int(i, num):
    b = i.to_bytes(num, 'big')
    return b

def decode_int(b):
    i = int.from_bytes(b, 'big')
    return i

def ceil_div(n,d):
    return -(-n // d)

def get_checksum(data):
    h = hashlib.new('sha256')
    h.update(data)
    return h.digest()
