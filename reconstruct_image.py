"""
reconstruct_image.py - By: Keiko Nagami - Friday Mar 13 2020
- reads .png tile files as matrices and reconstructs the full image
- saves full .jpeg image
- Run this with regular python (not micropython)
"""

import matplotlib.image as img
import numpy as np
import copy

num_packets = 960
m = 8 # size of blocks
count = -1
count_j = 0
count_debug = 0
for i in range(num_packets):
    for j in range(5):
        count += 1
        count_debug += 1
        B  = img.imread('tile_from_packet' + str(i) + '_number_' + str(j) + '.png', format='jpeg')
        if count == 0:
            A = copy.deepcopy(B)
        elif count == 480/8-1:
            A = np.vstack((A,B))
            print("one column")
            if count_j == 0:
                C = copy.deepcopy(A)
            else:
                C = np.hstack((C,A))
                print(i,j,count,count_j)
            count_j += 1
            count = -1
        else:
            A = np.vstack((A,B))
print(count_debug)

img.imsave('picture_out_reconstructed.jpeg', C)
