from __future__ import print_function

from pyimgalgos.GlobalUtils import print_ndarr
import numpy as np

print('numpy version:', np.version.version)

a = np.array(list(range(27))); a.shape = (3,9)
print_ndarr(a,'Original array:')
print(a)

s = np.hsplit(a, 3)

print_ndarr(s,'hsplit to tuple of arrays:')
print(s)

b = np.hstack(s)
print_ndarr(b,'hstack from tuple of arrays:')
print(b)
