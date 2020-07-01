#!/usr/bin/env python
#------------------------------
#import os
from __future__ import print_function
import sys
import numpy as np
from time import time
#------------------------------
import psana
from Detector.GlobalUtils import print_ndarr
#------------------------------

def dataset(tname):
    print('\nIn %s' % sys._getframe().f_code.co_name)

    dsname, src = 'exp=cxif5315:run=169', 'CxiDs2.0:Cspad.0'
    #if tname in ('1', '2', '3') :
    print('Example for\n  dataset: %s\n  source : %s' % (dsname, src))

    #psana.setOption('psana.calib-dir', './calib')
    #psana.setOption('psana.calib-dir', './empty/calib')

    ds  = psana.DataSource(dsname)
    evt = next(ds.events())
    env = ds.env()
    nrun = evt.run()
    print('env.calibDir(): %s' % env.calibDir())

    for key in evt.keys() : print(key)

#------------------------------

def detector(tname):
    print('\nIn %s' % sys._getframe().f_code.co_name)

    #from Detector.AreaDetector import AreaDetector
    #det = AreaDetector(src, env, pbits=0)

    det = psana.Detector(src, env)

    ins = det.instrument()
    print(80*'_', '\nInstrument: ', ins)
    #det.set_print_bits(511);
    #det.set_def_value(-5.);
    #det.set_mode(1);
    #det.set_do_offset(True); # works for ex. Opal1000
    
    #det.print_attributes()

    #par = nrun # evt or nrun
    
    #shape_nda = det.shape(par)
    #print_ndarr(shape_nda, 'shape of ndarray')
    
    #peds = det.pedestals(par)
    #rms = det.rms(par)
    #mask = det.mask(par)

    #gain = det.gain(par)
    #print_ndarr(gain, 'gain')
    
    #bkgd = det.bkgd(par)
    #status = det.status(par)
    #status_mask = det.status_as_mask(par)
    #cmod = det.common_mode(par)
    #nda_cdata = det.calib(evt)
    #nda_cdata_ub = det.calib(evt, cmpars=(5,50))
    #print_ndarr(nda_cdata_ub, 'calibrated data for cspad unbond pixels')
    
    #coords_x = det.coords_x(par)
    #areas = det.areas(par)
    #mask_geo = det.mask_geo(par)
    #mask_geo.shape = (32,185,388)
    #pixel_size = det.pixel_size(par)
        
    #t0_sec = time()
    #nda_raw = det.raw(evt)
    #print('Consumed time = %9.6f sec' % (time()-t0_sec))

    #i=0
    #if nda_raw is None :
    #    for i, evt in enumerate(ds.events()) :
    #        nda_raw = det.raw(evt)
    #        if nda_raw is not None :
    #            print('Detector data found in event %d' % i)
    #        break

    #print_ndarr(nda_raw, 'raw data')

#------------------------------

def test(tname):
    print('\nIn %s' % sys._getframe().f_code.co_name)
    print('test' % tname)

#------------------------------

def plot_image(img):
    import pyimgalgos.GlobalGraphics as gg
    ave, rms = img.mean(), img.std()
    gg.plotImageLarge(img, amp_range=(ave-1*rms, ave+2*rms))
    gg.show()

#------------------------------

if __name__ == "__main__" :
    print(80*'_')
    tname = sys.argv[1] if len(sys.argv)>1 else '1'
    if tname in ('1', '2', '3') : dataset(tname)
    elif tname == '4'           : dataset(tname)
    else : sys.exit ('Not recognized test name: "%s"' % tname)
    sys.exit ('End of %s' % sys.argv[0])

#------------------------------
