"""
DCT.py - By: Keiko Nagami - Friday Mar 13 2020
- Takes a Bayer image of size 480x640
- Breaks image up into 8 x 8 pixel blocks
- Gets the quantized DCT coefficients after performing a discrete cosine transform on each block
- Packs 5 tiles in one byte array to send; saves these as a text files
- Run this with camera board, WITH SD card plugged in, in OpenMV IDE
"""

# import relevant libraries
import sensor, image, math, umatrix, ulinalg, ulab, utime
sensor.reset() # initialize the camera sensor
sensor.set_pixformat(sensor.RGB565) # sensor.RGB565 takes RGB image
sensor.set_framesize(sensor.VGA) # sensor.VGA takes 640x480 image
sensor.skip_frames(time = 2500) # let new settings take effect


"""
def jpeg_dct(bayer_tile):

    This function performs the discrete cosine transform (DCT) on raw bayer image data and returns
    the DCT coefficients after they are quantized. Quantization is done to be able to send the DCT
    coefficients as byte array information in range [0,255]. See https://en.wikipedia.org/wiki/JPEG for more.

    bayer_tile: input of one 8x8 pixel tile of bayer information with range [0, 255]
    g: bayer_tile information centered at 0 for range [-128,127]
    G: DCT coefficients as floats
    B: ouput of Quantized DCT coefficients in byte range [0,255]
"""
def jpeg_dct(bayer_tile):
    g = ulinalg.zeros(8,8)
    G = ulinalg.zeros(8,8)
    B = ulinalg.zeros(8,8)
    for u in range(8):
        for v in range(8):
            sum_xy = 0
            coeff = 1/math.sqrt(2)
            for x in range(8):
                for y in range(8):
                    g[x,y] = bayer_tile[x,y] - 128
                    sum_xy = sum_xy + g[x,y]*math.cos((2*x + 1)*u*3.14/16)*math.cos((2*y + 1)*v*3.14/16)
            if u == 0:
                alpha_u = coeff
            else:
                alpha_u = 1
            if v == 0:
                alpha_v = coeff
            else:
                alpha_v = 1
            G[u,v] = (1/4)*alpha_u*alpha_v*sum_xy
            B[u,v] = round(G[u,v]/Q[u,v]) + 128 # add 128 to get in byte range [0,255]
    return B

"""
def thresholding(input_matrix):

    This function is used to remove values from the quantized DCT coefficient matrix that are of
    high frequencies, and inputs the lower frequency information into a byte array. This code is
    currently hard coded to remove all coefficients that are in the lower right triangle of the
    DCT coefficient matrix. We use the fact that the sum of the indices (i+j) is constant along any
    diagonal of a matrix to find the values that will be written in the byte array.

    input_matrix: input Quantized DCT coefficient matrix
    output_bytearray: bytearray with DCT coeffiecients that are low frequency
"""
def thresholding(input_matrix):
    output_bytearray = bytearray(36)
    count = 0
    for i in range(8):
        for j in range(8):
            if i + j <= 7:
                output_bytearray[count] = int(round(input_matrix[i,j]))
                count = count + 1
    return output_bytearray

"""
def init_basis_functions():

    NOTE: This function is not currently used. When called, a memory error is produced.

    This function precalculates the basis functions that are to be used in the computation
    of the DCT coefficients. Currently, the code is calculating these basis functions in a loop
    for every tile. If this function could be called once at the beginning of the script, this code
    would  *in theory* not take as long as it currently does to run. However, there is not enough memory on
    the board to precompute and store this information

    dict: dictionary to hold basis functions
    store_matrix: matrix of basis functions to be stored for each (p,q)
    key: (p,q) coordinate as a string to get the store_matrix in dict
"""
def init_basis_functions():
    dict = {}
    for p in range(8):
        for q in range(8):
            print(p,q)
            store_matrix = ulinalg.zeros(8,8)
            for m in range(8):
                for n in range(8):
                    store_matrix[m,n] = math.cos((2*m + 1)*p*3.14/16)*math.cos((2*n + 1)*q*3.14/16)
            key = str(p) + str(q)
            dict[key] = [store_matrix]
    return dict




img = sensor.snapshot() # take an image
count = 0
tiles_per_packet = 5
byte_array_to_send = bytearray(36*tiles_per_packet) #less than 200 byte byte array
packet_count = 0
num_total_packets = 960 # (480pixels/8pixelsperblock)*(640pixels/8pixelsperblock)/5blocksperpacket = 960packets
Q = umatrix.matrix([[16, 11, 10, 16, 24, 40, 51, 61],
            [12, 12, 14, 19, 26, 58, 60, 55],
            [14, 13, 16, 24, 40, 57, 69, 56],
            [14, 17, 22, 29, 51, 87, 80, 62],
            [18, 22, 37, 56, 68, 109, 103, 77],
            [24, 35, 55, 64, 81, 104, 113, 92],
            [49, 64, 78, 87, 103, 121, 120, 101],
            [72, 92, 95, 98, 112, 100, 103, 99]]) # Quantization matrix for quality = 50 from https://en.wikipedia.org/wiki/JPEG

#init_basis_functions()
for i in range(640/8):
    for j in range(480/8):
        bayer_matrix = ulinalg.zeros(8,8)
        for x in range(8):
            for y in range(8):
                bayer_matrix[x,y] = img.get_pixel(i*8+x, j*8+y) # 8x8 bayer matrix
        B_matrix = jpeg_dct(bayer_matrix)
        B_bytearray = thresholding(B_matrix) #byte array of one tile
        if count <= 4: # put bytearrays of five tiles in one longer bytearray
            for m in range(36):
                byte_array_to_send[count*36 + m] = B_bytearray[m]
            if count == 4:
                packet_count = packet_count + 1
                print(packet_count, byte_array_to_send)
                # write packet of five tiles to file
                with open('byte_array_to_send' + str(packet_count) + '_of_' + str(num_total_packets) + '.txt', 'wb') as f:
                    f.write(byte_array_to_send)
                count = -1
                byte_array_to_send = bytearray(36*tiles_per_packet)
            count = count + 1
