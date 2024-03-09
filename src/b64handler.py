import base64
import numpy as np

from consts import ENCODER_TABLE, DECODER_TABLE

def get_b64_enc(data):
    out = base64.b64encode(data)
    return out

def b64_dec(b64):
    pad = b'=' * (len(b64) % 4)
    d64 = base64.b64decode(b64 + pad)
    return d64

def get_b64_bytestring(data):
    d64 = get_b64_enc(data).strip(b'=')
    n64 = np.frombuffer(d64, dtype=np.uint8)
    return ENCODER_TABLE[n64].tobytes()

def dec_b64_bytearray(data):
    intarr = np.frombuffer(data, dtype = np.uint8)
    decarr = DECODER_TABLE[intarr]
    return decarr.tobytes()
