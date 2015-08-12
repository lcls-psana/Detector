#!/usr/bin/env python

##-----------------------------
import sys
import psana
import numpy as np
from time import time
from Detector.PyDetector import PyDetector
from ImgAlgos.PyAlgos import reshape_nda_to_2d, reshape_nda_to_3d, print_arr_attr, print_arr
import pyimgalgos.GlobalGraphics as gg
##-----------------------------

def example_01():

    SKIP   = 0
    EVENTS = 1000 + SKIP

    dsname = 'exp=cxif5315:run=169'
    src    = psana.Source('DetInfo(CxiDs2.0:Cspad.0)')
    print 'Example of the detector calibrated data average for\n  dataset: %s\n  source : %s' % (dsname, src)

    # Non-standard calib directory
    #psana.setOption('psana.calib-dir', './calib')

    ds  = psana.DataSource(dsname)
    evt = ds.events().next()
    env = ds.env()
    
    det = PyDetector(src, env, pbits=0)
    shape = det.shape(evt) 

    print '  det.shape() = ', shape 
    
    #mask = det.mask(evt)
    
    t0_sec = time()
    counter=0
    arr_sum = np.zeros(shape, dtype=np.double)

    for i, evt in enumerate(ds.events()) :

        if i<SKIP    : continue
        if not i<EVENTS : break

        cdata = det.calib(evt)
        if cdata is None : continue
        if not i%10 : print '  Event: %d' % i
        counter += 1
        arr_sum += cdata 

    print '  Detector data found in %d events' % counter
    print '  Total consumed time = %f sec' % (time()-t0_sec)

    arr_ave = arr_sum/counter if counter>0 else arr_sum
  
    ##-----------------------------
    # Plot averaged image

    img = det.image(evt, arr_ave)
    if img is None : sys.exit('Image is not available. FURTHER TEST IS TERMINATED')
    
    ave, rms = arr_ave.mean(), arr_ave.std()
    gg.plotImageLarge(img, amp_range=(ave-1*rms, ave+3*rms))
    gg.show()

    ##-----------------------------
    # Save n-d array in text file
    
    arr_ave = reshape_nda_to_2d(arr_ave)
    ofname = 'nda-ave-%s-r%04d.txt' % (env.experiment(), evt.run())    
    print 'Save array in file %s' % ofname
    np.savetxt(ofname, arr_ave, fmt='%8.1f', delimiter=' ', newline='\n')

##-----------------------------
##-----------------------------

if __name__ == "__main__" :

    ntest = int(sys.argv[1]) if len(sys.argv)>1 else 1
    print '%s\nExample # %d' % (80*'_', ntest)

    example_01()

    sys.exit(0)

##-----------------------------
