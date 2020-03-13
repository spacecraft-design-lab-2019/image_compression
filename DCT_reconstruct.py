"""
DCT_reconstruct.py - By: Keiko Nagami - Friday Mar 13 2020
- Reads bytearrays containing quantized DCT coefficients of five 8x8pixel tiles from text files
- Reconstructs the Quantized DCT coefficient matrices for each tile and computes the inverse DCT to get raw bayer image data
- Saves .png image tiles
- Run this with camera board, WITH SD card plugged in, in OpenMV IDE
"""

# import relevant libraries
import sensor, image, math, umatrix, ulinalg, ulab

sensor.reset() # initialize the camera sensor
sensor.set_pixformat(sensor.RGB565) # sensor.RGB565 takes RGB image
sensor.set_framesize(sensor.VGA) # sensor.VGA takes 640x480 image
sensor.skip_frames(time = 2500) # let new settings take effect

# Bayer filter uses RGGB pattern. Each set contains row indices that correspond to the R,G, or B
set_R = [0, 4, 8, 12,] # R
set_G = [1, 2, 5, 6, 9, 10, 13, 14,]# G
set_B = [3, 7, 11, 15] #B

R_val = 0
G_val = 0
B_val = 0

num_total_packets = 960
packet_count = 0

Q = umatrix.matrix([[16, 11, 10, 16, 24, 40, 51, 61],
            [12, 12, 14, 19, 26, 58, 60, 55],
            [14, 13, 16, 24, 40, 57, 69, 56],
            [14, 17, 22, 29, 51, 87, 80, 62],
            [18, 22, 37, 56, 68, 109, 103, 77],
            [24, 35, 55, 64, 81, 104, 113, 92],
            [49, 64, 78, 87, 103, 121, 120, 101],
            [72, 92, 95, 98, 112, 100, 103, 99]]) # Quantization matrix for quality = 50

for i in range(num_total_packets):
    packet_count = packet_count + 1
    with open('byte_array_to_send' + str(packet_count) + '_of_960' + '.txt', 'rb') as f:
        byte_array_five_tiles = f.read()
    print(i,byte_array_five_tiles) #matches
    for j in range(5): # nuber of tiles per packet
        count = 0
        B = ulinalg.zeros(8,8)
        G = ulinalg.zeros(8,8)
        for u in range(8):
            for v in range(8):
                if u+v <=7:
                    B[u,v] = byte_array_five_tiles[j*36 + count] #recreate full quantized DCT coefficient matrix
                    G[u,v] = (B[u,v] - 128)*Q[u,v] #Get the DCT coefficient matrix
                    count = count + 1
                else:
                    B[u,v] = 128
                    G[u,v] = (B[u,v] - 128)*Q[u,v]
        g = ulinalg.zeros(8,8)
        pixel_block = image.Image(8, 8, sensor.RGB565) # 8x8 bytes per pixel block
        print(pixel_block)
        for x in range(8):
            for y in range(8):
                # inverse DCT
                sum_uv = 0
                for u in range(8):
                    for v in range(8):
                        if u == 0:
                            alpha_u = 1/math.sqrt(2)
                        else:
                            alpha_u = 1
                        if v == 0:
                            alpha_v = 1/math.sqrt(2)
                        else:
                            alpha_v = 1
                        sum_uv = sum_uv + alpha_u*alpha_v*G[u,v]*math.cos((2*x+1)*u*math.pi/16.0)*math.cos((2*y+1)*v*math.pi/16.0)
                bayer_pixel_val = (0.25)*sum_uv + 128.0
                g[x,y] = int(bayer_pixel_val)
                # demosaic from bayer to RGB
                if y in set_R:
                    R_val = int(g[x,y])
                if y in set_G:
                    G_val = int(g[x,y])
                if y in set_B:
                    B_val = int(g[x,y])
                pixel_block.set_pixel(x,y,(R_val, G_val, B_val))
        pixel_block_jpeg = pixel_block.compressed(30) # can't save image without jpeg compressing
        # write the tile to a jpeg image
        with open('tile_from_packet' + str(i) + '_number_' + str(j) + '.png', 'wb') as f: # 960 packets, each packet has 5 tiles
            f.write(pixel_block_jpeg)
