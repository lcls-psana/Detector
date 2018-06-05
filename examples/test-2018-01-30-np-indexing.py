# source activate ana-1.0.5   #  np.version.version = 1.11.2
# source activate ana-1.3.1   #  np.version.version = 1.11.3
# source activate ana-1.3.44  #  np.version.version = 1.11.3

import numpy as np

print 'numpy version:', np.version.version

a = np.array(range(12)); a.shape = (4,3)
m = np.array((1,1,0,0,1,1,0,0,0,1,1,1)); m.shape = (4,3)

print 'a=', a
print 'm=', m

print 'a[m]:\n', a[m]
print 'a[m>0]:\n', a[m>0]
