import numpy as np
from PIL import Image

from consts import HEADER_LENGTH

def image_from_bytes(byts, width, height, channels):
    arr = np.frombuffer(byts, np.uint8).reshape((height, width, channels))
    img = Image.fromarray(arr)
    return img

def read_image(file, mod = True):
    img = np.array(Image.open(file), dtype = np.uint8).flatten()
    if mod:
        img[HEADER_LENGTH:] = img[HEADER_LENGTH:] % 64
    return img.tobytes()
