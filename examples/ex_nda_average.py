#!/usr/bin/env python
##-----------------------------
"""Loops over events in the data file, 
   gets calibrated n-d array for cspad, 
   evaluates n-d arrays for averaged and maximum values

   Usage::
   python ex_nda_average.py
   bsub -q psfehq -o log-r0092.log python ex_nda_average.py
"""
from __future__ import print_function

##-----------------------------
import sys
import psana
import numpy as np
from time import time
#from Detector.AreaDetector import AreaDetector
from ImgAlgos.PyAlgos import reshape_nda_to_2d, reshape_nda_to_3d, print_arr_attr, print_arr

##-----------------------------
def example_01():

    # control parameters
    SKIP    = 0
    EVENTS  = 100 + SKIP
    DO_PLOT = False
    DO_PLOT = True

    dsname = 'exp=cxif5315:run=169'
    #src    = psana.Source('DetInfo(CxiDs2.0:Cspad.0)')
    src    = 'CxiDs2.0:Cspad.0'
    print('Example of the detector calibrated data average for\n  dataset: %s\n  source : %s' % (dsname, src))

    # Non-standard calib directory
    #psana.setOption('psana.calib-dir', './calib')

    ds   = psana.DataSource(dsname)
    evt  = next(ds.events())
    env  = ds.env()
    rnum = evt.run()
    
    #det = AreaDetector(src, env, pbits=0, iface='P')
    det = psana.Detector(src, env)
    shape = det.shape(rnum) 

    print('  det.shape() = ', shape) 
    
    #mask = det.mask(evt)
    
    t0_sec  = time()
    counter = 0
    arr_sum = np.zeros(shape, dtype=np.double)
    arr_max = np.zeros(shape, dtype=np.double)

    for i, evt in enumerate(ds.events()) :

        if i<SKIP    : continue
        if not i<EVENTS : break

        cdata = det.calib(evt)
        #cdata = det.raw_data(evt)

        if cdata is None : continue
        if not i%10 : print('  Event: %d' % i)
        counter += 1
        arr_sum += cdata 
        arr_max = np.maximum(arr_max, cdata)

    print('  Detector data found in %d events' % counter)
    print('  Total consumed time = %f sec' % (time()-t0_sec))

    arr_ave = arr_sum/counter if counter>0 else arr_sum
  
    ##-----------------------------
    # Plot averaged image
    if DO_PLOT :
        import pyimgalgos.GlobalGraphics as gg

        #nda = arr_ave
        nda = arr_max
        img = det.image(rnum, nda)
        if img is None : sys.exit('Image is not available. FURTHER TEST IS TERMINATED')
    
        ave, rms = nda.mean(), nda.std()
        gg.plotImageLarge(img, amp_range=(ave-1*rms, ave+3*rms))
        gg.show()

    ##-----------------------------
    # Save n-d arrays in 2-d text files

    arr_ave = reshape_nda_to_2d(arr_ave)
    ofname_ave = 'nda-ave-%s-r%04d.txt' % (env.experiment(), evt.run())    
    print('Save averaged array in file %s' % ofname_ave)
    np.savetxt(ofname_ave, arr_ave, fmt='%8.1f', delimiter=' ', newline='\n')

    arr_max = reshape_nda_to_2d(arr_max)
    ofname_max = 'nda-max-%s-r%04d.txt' % (env.experiment(), evt.run())    
    print('Save maximum  array in file %s' % ofname_max)
    np.savetxt(ofname_max, arr_ave, fmt='%8.1f', delimiter=' ', newline='\n')

##-----------------------------
if __name__ == "__main__" :

    ntest = int(sys.argv[1]) if len(sys.argv)>1 else 1
    print('%s\nExample # %d' % (80*'_', ntest))

    example_01()

    sys.exit(0)

##-----------------------------
