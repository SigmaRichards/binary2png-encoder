import warnings

from consts import PREFIX, HEADER_LENGTH
from utils import decode_int, encode_int

def read_header(data):
    header = data[:HEADER_LENGTH]
    if header[:32] != PREFIX:
        print(header[:32], PREFIX)
        raise ValueError("Prefix does not match!")
    out = dict(
        ebi = decode_int(header[32:33]),
        tot_imgs = decode_int(header[33:35]),
        cur_img  = decode_int(header[35:37]),
        num_byte = decode_int(header[37:46]),
        checksum = header[46:78]
    )
    return out

def make_header(encode = True, t_img = 1, c_img = 0, n_byt = 0, cs = None):
    header = PREFIX
    ebi = encode_int(0,1)
    if encode:
        ebi = encode_int(1, 1)
    header = header + ebi
    assert t_img > 0, "Must have atleast 1 image"
    header = header + encode_int(t_img - 1, 2)
    assert c_img >= 0, "Image indexing starts at 0, negative values not allowed"
    header = header + encode_int(c_img, 2)
    assert n_byt >= 0, "Cannot encode negative number of bytes"
    header = header + encode_int(n_byt, 9)
    if cs is None:
        warnings.warn("No checksum supplied, filling with 0s")
        header = header + encode_int(0, 32)
    else:
        assert len(cs) == 32, "expected checksum as bytestring with length 32"
        header = header + cs
    header = header + encode_int(0, 6)
    assert len(header) == HEADER_LENGTH, "Header length does not match expected!"
    return header
