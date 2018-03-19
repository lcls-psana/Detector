#!/usr/bin/env python

#--------------------------------

import numpy as np
from Detector.GlobalUtils import print_ndarr
from PSCalib.NDArrIO import save_txt

#--------------------------------

print 50*'_'

#dirsegs = 'M068', 'M088'
dirsegs = ('M044',)
#ifname, ofname, ofmt = '%s/g%d_gain.npy',   'jf_pixel_gain',   '%.4f'
ifname, ofname, ofmt = '%s/g%d_offset.npy', 'jf_pixel_offset', '%.1f'

lst_gains = []
for gi in range(3) :
    lst_segs = []
    for dir in dirsegs :
        fname = ifname % (dir, gi)
        nda = np.load(fname)
        print_ndarr(nda, 'file: %s nda:' % fname)
        lst_segs.append(nda)
    nda_one_gain = np.stack(tuple(lst_segs))
    print_ndarr(nda_one_gain, 'nda_one_gain')

    lst_gains.append(tuple(nda_one_gain))

nda = np.stack(lst_gains)
print_ndarr(nda, 'calib nda')

#sh = (3,<nsegs>,512,1024)

np.save('%s.npy'%ofname, nda)
print 'Save n-d array in file "%s"' % ('%s.npy'%ofname)

save_txt('%s.txt'%ofname, nda, fmt=ofmt)
print 'Save n-d array in file "%s"' % ('%s.txt'%ofname)

#--------------------------------
