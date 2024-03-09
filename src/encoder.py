#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#Imports~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

import os
import sys
import cv2
import numpy as np
from PIL import Image
from functools import reduce
from tqdm import tqdm

from consts import HEADER_LENGTH
from header import make_header
from utils import get_checksum
from images import image_from_bytes
from b64handler import get_b64_bytestring

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#General Util~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

def num_enc_bytes_free(width, height, channels = 4):
    """
    Number of bytes across each pixel and channel MINUS header
    """
    tot_bytes = width * height * channels
    enc_bytes_avail = tot_bytes - HEADER_LENGTH
    return enc_bytes_avail

def num_dec_bytes_free(width, height, channels = 4):
    """
    Assumes using base64. Returns the number of decoded (i.e. non-encoded)
    bytes free in proposed image, and the number of encoded bytes this
    requires.
    """
    ebytes = num_enc_bytes_free(width, height, channels)
    dbytes = 3 * ebytes // 4
    ebytesA = 4 * dbytes // 3
    return dbytes, ebytesA

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#Images~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

def get_ref_img(img_ref, ref_scale, **info):
    img  = Image.open(img_ref)
    imgA = np.array(img, dtype = np.uint8)
    imgA = imgA.reshape((img.height, img.width, -1))
    if ref_scale != 1:
        imgA = cv2.resize(imgA, (0,0), fx = ref_scale, fy = ref_scale)
    imgA = imgA - (imgA % 64)
    #ENSURE HEADER IS INTACT
    tshape = imgA.shape
    imgA = imgA.flatten()
    imgA[:HEADER_LENGTH] = 0
    imgA = imgA.reshape(tshape)
    return imgA

def get_img_file_order(tot_size, ref_files, ref_scale):
    ref_sizes = {k:get_ref_img(k, ref_scale).shape for k in ref_files}
    valid_files = dict()
    for k,v in ref_sizes.items():
        v = num_dec_bytes_free(*v)
        if v[0] > 0:
            valid_files[k] = v
    assert len(valid_files) > 0, "No valid files given"
    #Iterate through files to calculate how many bytes get used
    rem_size = tot_size
    out_order = []
    ind = 0
    while rem_size > 0:
        if ref_files[ind] in valid_files:
            rem_size -= valid_files[ref_files[ind]][0]
            out_order.append(ref_files[ind])
        ind = (ind + 1) % len(ref_files)
    out = [[a, valid_files[a], reduce(lambda x,y: x*y, ref_sizes[a])] for a in out_order]
    return out

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#File encoding handler~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

def join_ref_enc_imgs(ref, img):
    aimg = np.array(img).reshape(ref.shape)
    return ref + aimg

def encoded_img(data,**info):
    d64 = get_b64_bytestring(data)
    header = make_header(encode = True,
                         t_img = info['num_img'],
                         c_img = info['cur_img'],
                         n_byt = len(d64),
                         cs    = get_checksum(d64))
    out_data = (header + d64).ljust(info['img_byt'], b'\0')
    ref = get_ref_img(**info)
    img = image_from_bytes(out_data, *ref.shape)
    oimga = join_ref_enc_imgs(ref, img)
    return Image.fromarray(oimga)

def encode_file(file, out_dir, ref_dir, ref_scale):
    tot_bytes = os.stat(file).st_size
    ref_files = [os.path.join(ref_dir, a) for a in os.listdir(ref_dir)]
    file_order = get_img_file_order(tot_bytes, ref_files, ref_scale)
    cur_img = 0
    info = dict(
        cur_img = cur_img,
        ref_scale = ref_scale,
        num_img = len(file_order),
        img_ref = file_order[cur_img][0],
        dec_byt = file_order[cur_img][1],
        img_byt = file_order[cur_img][2],
    )
    with open(file, 'rb') as f:
        pbar = iter(tqdm(range(len(file_order))))
        while (chunk := f.read(info['dec_byt'][0])) :
            if cur_img == -1:
                raise ValueError('More data than expected')
            next(pbar)
            #Get image and save
            img = encoded_img(chunk, **info)
            out_filename = f"{os.path.basename(file)}_imgbin_{cur_img}.png"
            out_path = os.path.join(out_dir, out_filename)
            img.save(out_path)
            #Update for next iteration
            cur_img += 1
            if cur_img < len(file_order):
                info = dict(
                    cur_img = cur_img,
                    ref_scale = ref_scale,
                    num_img = len(file_order),
                    img_ref = file_order[cur_img][0],
                    dec_byt = file_order[cur_img][1],
                    img_byt = file_order[cur_img][2],
                )
            else:
                cur_img = -1
        try:
            next(pbar)
        except StopIteration:
            pass

    return

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#Main~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

def main():
    if len(sys.argv) <= 1:
        print("Usage: ./img-encoder.sh encode [file]")
        return 1
    file = sys.argv[-1]
    if not os.path.exists(file):
        print(f"File does not exist: {file}")
        return 1
    out_dir = os.path.join("out", "encoded", os.path.basename(file))
    os.makedirs(out_dir, exist_ok = True)
    ref_dir = 'ref_imgs'
    os.makedirs(ref_dir, exist_ok = True)
    if len(os.listdir(ref_dir)) == 0:
        print(f"No reference images in directory: {ref_dir}")
        return 2
    ref_scale = 2.0
    encode_file(file, out_dir, ref_dir, ref_scale)
    return 0

if __name__ == "__main__":
    ret = main()
    if type(ret) is int:
        exit(ret)

