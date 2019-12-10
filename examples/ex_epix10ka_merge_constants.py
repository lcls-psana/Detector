#!/usr/bin/env python
"""
    Script for epix10k merging gain and offset consatnts and producing calibration files.
"""
from __future__ import print_function
#--------------------------------

import sys
import numpy as np
from Detector.GlobalUtils import print_ndarr
from PSCalib.NDArrIO import save_txt

#--------------------------------

print(50*'_')

detname = 'Camera1'
dir = '/reg/g/psdm/detector/gains/epix10k/2018-06-04-%s' % detname
gainmodes = ('FL-L', 'FM-M', 'FH-H', 'AML-L', 'AML-M', 'AHL-L', 'AHL-H')
name_ctype_fmts = (('Dark', 'offset', '%.1f'),\
                   ('Gain', 'gain',   '%.4f'))
ofpref = './epix10k'
shape1 = None

for t,ctype,fmt in name_ctype_fmts :
    ofname = '%s-%s' % (ofpref, ctype)
    print('ofname: %s fmt" %s' % (ofname,fmt))
    #lst_gains = []
    lst_segs = []

    for gmode in gainmodes :
        fname = '%s/%s-%s-%s.txt' % (dir, detname, gmode, t)
        #print('fname: %s' % fname)
        nda = np.loadtxt(fname)
        print_ndarr(nda, 'file: %s\n      nda' % fname)
        lst_segs.append(nda)
        if shape1 is None : shape1 = nda.shape

    nda_one_seg = np.stack(tuple(lst_segs))
    print_ndarr(nda_one_seg, 'nda_one_seg')

    #lst_gains.append(tuple(nda_one_seg))
    #nda = np.stack(lst_gains)
    #print_ndarr(nda, 'calib nda')

    nda_one_seg.shape = (len(gainmodes),1,352, 384)
    print('Re-shape output array to: %s' % str(nda_one_seg.shape))

    np.save('%s.npy'%ofname, nda_one_seg)
    print('Save n-d array in file "%s"' % ('%s.npy'%ofname))

    save_txt('%s.txt'%ofname, nda_one_seg, fmt=fmt)
    print('Save n-d array in file "%s"' % ('%s.txt'%ofname))

#--------------------------------
