import hashlib
import numpy as np

HEADER_LENGTH = 84

group_table = [
    [['A','Z'], [0,  25]],
    [['a','z'], [26, 51]],
    [['0','9'], [52, 61]],
]
special_table = [
    ['+', 62],
    ['/', 63]
]

def build_prefix():
    h = hashlib.new('sha256')
    h.update(b'pngbinaryencoding\n')
    return h.digest()

def get_encoder_table():
    enc_table = np.zeros(123 , dtype=np.uint8) -1
    for (cl, ch), (vl, vh) in group_table:
        r0 = range(ord(cl), ord(ch)+1)
        r1 = range(vl, vh+1)
        for refc, refi in zip(r0, r1):
            enc_table[refc] = refi
    for cv, iv in special_table:
        enc_table[ord(cv)] = iv
    return enc_table

def get_decoder_table():
    dec_table = np.zeros(64 , dtype=np.uint8) -1
    for (cl, ch), (vl, vh) in group_table:
        r0 = range(ord(cl), ord(ch)+1)
        r1 = range(vl, vh+1)
        for refc, refi in zip(r0, r1):
            dec_table[refi] = refc
    for cv, iv in special_table:
        dec_table[iv] = ord(cv)
    return dec_table

PREFIX = build_prefix()
ENCODER_TABLE = get_encoder_table()
DECODER_TABLE = get_decoder_table()
