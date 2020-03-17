# image_compression

There are 3 files in this repo:
1) DCT.py

- Run on camera board using OpenMV IDE with SD card plugged in, uses micropython
- This is the script that would run on the camera board
- Takes an image, breaks up the image into 8x8pixel tiles, gets the DCT coefficients of each of these tiles, and writes DCT coefficents of 5 image tiles to one "packet" in bytearray form. These packets are currently being written to the SD card as .txt files. These .txt files are what would need to be transmitted via radio.
- TODO: Currently this takes a very long time to send one image (~1 second per tile). Need to make this faster for it to be feasible.

2) DCT_reconstruct.py

- Meant to be run on the ground
- Currently runs on camera board using OpenMV IDE with SD card plugged in, uses micropython 
- Reads bytearrays from .txt files written by DCT.py and computes the inverse DCT. Gets the raw bayer image data, then converts to RGB image data and writes .png files for each image tile
- TODO: convert this to regular python so it doesn't need to be run on a camera board. Did this in micropython so that the bytearray types and Image constructors would be same from DCT.py.
- TODO: current demosaic method from Bayer to RGB just uses the R, G, or B value from a previous last value of each row within each 8x8 pixel tile. Could probably do something where you look at the R, G, or B values in the same column above and below each pixel. 

3) reconstruct_image.py

- Meant to be run on the ground
- Runs on your computer with regular python (not micropython)
- Reads the .png files from DCT_reconstruct.py and stitches the tiles together and saves the full .jpeg image

Read comments in each script for more information. Much of the JPEG compression approach comes from here: https://en.wikipedia.org/wiki/JPEG. 
Another approach could be to use a JPEG parser that parses the information in a full JPEG file to find the relevant information that would be needed to reconstruct the image on the ground. 
