#!/usr/bin/env python

from __future__ import print_function
from ImgAlgos.PyAlgos import photons as alg_photons

def test_photons():

    #import sys
    import numpy as np
    from time import time
    from pyimgalgos.GlobalUtils import print_ndarr

    mean, sigma = 0,10
    #shape = (32,185,388)
    shape = (4,512,512)
    mask  = np.ones(shape, dtype=np.uint8)
    data  = np.array(mean + sigma * np.random.standard_normal(size=shape), dtype=np.float32)

    print_ndarr(data, 'data')
    print_ndarr(mask, 'mask')

    t0_sec = time()
    arr3d = alg_photons(data, mask)
    print('\nTime consumed by photons(data, mask) (sec) = %10.6f' % (time()-t0_sec))

    print_ndarr(arr3d, 'arr3d')

    # Plot one of segments from resulting array

    arr2d = arr3d[1,:]
    arr2d.shape = (shape[-2], shape[-1])

    print_ndarr(arr2d, 'arr2d')

    from pyimgalgos.GlobalGraphics import plotImageLarge, show
    #plotImageLarge(data, title='data')
    plotImageLarge(arr2d, title='arr2d')
    show()


if __name__ == "__main__":

    test_photons()

# EOF


