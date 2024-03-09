# Binary to PNG - File encoding

Encode your binary files into a series of PNGs, and provide reference images you want them to look like. This is a silly project and I don't see any actual use for this (apart from obfuscating your files). There are a couple important notes:

 1. This *does not encrypt* your files, just encodes them, so don't use this for any security.
 2. This *does not compress* your files. Because of the inherent overhead used in the process, the total size will actually *increase*.

There is more or less no reason to do this to your files *except* obfuscating.

## General usage

Included is a script which helps streamline usage `img-encoder.sh`. Despite what the name suggests, it does handle both encoding and decoding. 

### Setup

The script is only designed to work while also encoding with additional picture information, so you need to actually provide some reference images. Create a folder in the root directory called *"ref_imgs"* and place all the images you want to source from in there. The script will cycle through all these images to use as the template of the output. The encoded images have their resolution scaled up by a factor of 2, to allow more data to fit in each image.

### Encoding

```
./img-encoder.sh encode [src-file]
```

This will create a directory in `out/encoded/`, and output a series of images with the encoded binary data. It will automatically pick names, but theoretically you can change these to anything you want, as sequence information is encoded inside each image.

### Decoding

```
./img-encoder.sh decode [enc-directory] [output-filename]
```

This will read each file in `[enc-directory]` and decode and stream the data into output-filename, and warn if there are any issues with the data.

## Other comments

This is a simple project I made for fun. I am not maintaining this codebase. I'm certain there will be a large number of issues that make this fragile/unusable.

## Possible Improvements/Features

Possible updates which may or may never come. In no particular order

 - Option for scaling factor
 - Option to not include any reference images
 - Custom bit-depth of reference images
 - Custom output bit-depth
 - Smarter reference image matching
 - Dithering in image matching
