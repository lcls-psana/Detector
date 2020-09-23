#----------

import sys
import psana
import numpy as np

from PSCalib.GeometryAccess import img_from_pixel_arrays
from Detector.GlobalUtils import info_ndarr, print_ndarr

#----------

if __name__ == "__main__" :
    """
       Self-test
       Usage: python <path>/AreaDetectorCompaund.py <test-number>
    """

    from time import time

    ntest = int(sys.argv[1]) if len(sys.argv)>1 else 4
    print 'Test # %d' % ntest

    dsname, detname = 'exp=mfxls4916:run=298', 'MfxEndstation.0:Jungfrau.1'
    print 'Example for\n  dataset: %s\n  detname : %s' % (dsname, detname)

    #psana.Source('DetInfo(CxiDs2.0:Cspad.0)')
    ds = psana.DataSource(dsname)

    env = ds.env()
    cls = env.calibStore()
    eviter = ds.events()
    evt = eviter.next()
    rnum = evt.run()

    #for key in evt.keys() : print key

    t0_sec = time()
    det = psana.Detector(detname)
    print '\nConstructor time (sec) = %.6f' % (time()-t0_sec)

    #print 'det methods - dir(det):\n ', '\n  '.join([s for s in dir(det) if s[0]!='_'])

    print 'rnum     :', rnum
    print 'calibdir :', str(env.calibDir())
    print 'size     :', str(det.size(evt))
    print 'shapes   :', str(det.shape(evt))
    print 'ndims    :', str(det.ndim(evt))
    print 'det.name :', det.name

    t0_sec = time()
    raw = det.raw(evt)
    print '\ndet.raw(evt) consumed time (sec) = %.6f' % (time()-t0_sec)
    print_ndarr(raw, name='raw as nda', first=0, last=5)

    calib = det.calib(evt)
    print_ndarr(calib, name='calib', first=0, last=5)

    print_ndarr(det.pedestals(rnum), name='pedestals', first=0, last=5)
    print_ndarr(det.gain(rnum),      name='gain     ', first=0, last=5)
    print_ndarr(det.offset(rnum),    name='offset   ', first=0, last=5)

    print_ndarr(det.coords_x(evt),   name='coords_x ', first=0, last=5)
    print_ndarr(det.coords_y(evt),   name='coords_y ', first=0, last=5)

    #print_ndarr(det.indexes_x(evt), name='indexes_x no offset', first=1000, last=1005)
    #print_ndarr(det.indexes_x(evt, xy0_off_pix=(1500,1500)), name='indexes_x, off_pix=(1000,1000)', first=1000, last=1005)

    #img = reshape_to_2d(det.raw(evt))
    
    #_ = det.image(evt, nda_in=calib, pix_scale_size_um=None, xy0_off_pix=None, do_update=False)

    # NOTICE:
    # xy0_off_pix=(VERT,HORIZ)
    # do_update=True is required if indexes_x/y called

    xy0_offset =(550,550) if ntest==1 else (1400,1400)

    img = det.image(evt, nda_in=raw, xy0_off_pix=xy0_offset)
    print_ndarr(img, name='img', first=0, last=5)

    if False :
        from pyimgalgos.GlobalUtils import reshape_to_2d
        from pyimgalgos.GlobalGraphics import plotImageLarge, show

        plotImageLarge(img, title='img as %s' % str(img.shape), amp_range=(0,5000))
        show()

    sys.exit('TEST COMPLETED')

#----------
