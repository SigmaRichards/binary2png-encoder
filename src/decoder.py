#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#Imports~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

import os
from tqdm import tqdm

from consts import HEADER_LENGTH, PREFIX
from utils import get_checksum
from header import read_header, make_header
from images import read_image
from b64handler import b64_dec, dec_b64_bytearray

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#Handler~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

def data_from_img(file):
    raw = read_image(file)
    head_info = read_header(raw)
    adata = raw[HEADER_LENGTH:(HEADER_LENGTH+head_info['num_byte'])]
    assert get_checksum(adata)==head_info['checksum'], "Checksums don't match!"
    b64 = dec_b64_bytearray(adata)
    decoded = b64_dec(b64)
    return decoded

def decode_imgs(file_list, newfile):
    #Check all images are available
    is_encoded = None
    count = None
    order = dict()
    #print('Checking files...')
    for cfile in file_list:
        raw = read_image(cfile)
        chead = raw[:HEADER_LENGTH + 2]
        head_info = read_header(chead)
        if is_encoded is None:
            is_encoded = head_info['ebi'] > 0
        assert is_encoded == (head_info['ebi'] > 0), 'inconsistent encoding scheme'
        if count is None:
            count = head_info['tot_imgs']
        assert count == head_info['tot_imgs'], 'inconsistent counts on images'
        assert head_info['cur_img'] <= count, 'index higher than count'
        assert head_info['cur_img'] not in order, 'Multiple image with same index'
        order[head_info['cur_img']] = cfile
    for i in range(count + 1):
        assert i in order,"Not all indexes accounted for"
    #print('Writing data to decoded file')
    with open(newfile, 'wb') as f:
        for i in tqdm(range(count + 1)):
            cfile = order[i]
            f.write(data_from_img(cfile))
    return


#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#Main~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

def main():
    import sys
    if len(sys.argv) <= 2:
        print("Usage: ./img-encoder.sh decode [input-folder] [output-file]")
        return 1
    file_dir = sys.argv[-2]
    outfile = sys.argv[-1]
    files = [os.path.join(file_dir,a) for a in os.listdir(file_dir)]
    decode_imgs(files, outfile)
    return 0

if __name__ == "__main__":
    ret = main()
    if type(ret) is int:
        exit(ret)
