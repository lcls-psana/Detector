#!/usr/bin/env python

"""2020-01-14 
   generates fake files for Jungfrau4M / 1M of shapes
   (3,8,512,1024) / (3,2,512,1024)
   pedestals, pixel_status, pixel_gain, pixel_offset of shapes
"""
#----------

import numpy as np
from PSCalib.NDArrIO import save_txt

#----------

def calibfiles(shape=(3,8,512,1024), jfname='jungfrau4M') :

    w = np.ones(shape[1:], dtype=np.float64)

    p = np.ones(shape, dtype=np.float64)*100
    s = np.zeros(shape, dtype=np.int64)
    g = np.concatenate((41.5*w, -1.39*w, -0.11*w)) # g0/1/2 = 41.5/-1.39/-0.11
    o = np.concatenate((0.01*w,   300*w,    50*w)) # o0/1/2 = 0.01/300/50
    g.shape=shape
    o.shape=shape

    save_txt(jfname+'_fake_pedestals.txt',    p, fmt='%1f', verbos=True)
    save_txt(jfname+'_fake_pixel_status.txt', s, fmt='%1d', verbos=True)
    save_txt(jfname+'_fake_pixel_gain.txt',   g, fmt='%4f', verbos=True)
    save_txt(jfname+'_fake_pixel_offset.txt', o, fmt='%1f', verbos=True)

    cdir = '/reg/d/psdm/det/detdaq17/calib/Jungfrau::CalibV1/DetLab.0:Jungfrau.2/'
    print('DO NOT FORGET TO DEPLOY IN: %s' % cdir+'pedestals/0-end.data')
    print('DO NOT FORGET TO DEPLOY IN: %s' % cdir+'pixel_status/0-end.data')
    print('...')
    print('Ex: /reg/d/psdm/xcs/xcsx22015/calib/Jungfrau::CalibV1/XcsEndstation.0:Jungfrau.0/')

#----------

if __name__ == "__main__" :
    import sys
    tname = sys.argv[1] if len(sys.argv)>1 else '1'
    if   tname=='1' : calibfiles(shape=(3,8,512,1024), jfname='jungfrau4M')
    elif tname=='2' : calibfiles(shape=(3,2,512,1024), jfname='jungfrau1M')
    else : sys.exit('Not recognized test name: "%s"' % tname)

#----------
