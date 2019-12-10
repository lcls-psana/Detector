#!/usr/bin/env python
#------------------------------
from __future__ import print_function
import os
import sys
import psana
import numpy as np
from PIL import Image
from time import time
from Detector.GlobalUtils import print_ndarr
#------------------------------
#psana.setOption('psana.calib-dir', './calib')

def example01() :
    """Saves per event images of MecTargetChamber.0:Cspad(2x2).<[0-4]> detector in tiff files."""

    #------------------------------
    print('PARAMETERS')
    
    exp     =     sys.argv[1]   # ex.: mecj5515
    runnum  = int(sys.argv[2])  # ex.: 102
    detnum  = int(sys.argv[3])  # ex.: 1 (for MecTargetChamber.0:Cspad2x2.1)

    dsname  = 'exp=%s:run=%d' % (exp, runnum) # ex: 'exp=mecj5515:run=102'
    detname = 'MecTargetChamber.0:Cspad.0' if detnum==0 else 'MecTargetChamber.0:Cspad2x2.%1d' % detnum
    suffix  = detname.replace(":","-").replace(".","-") #.lower()
    cmpars  = (1,1000,500,100) if detnum==0 else (5,2000)
    do_save = True
    mask_bits = 0o377 # for releases >ana-0.17.11
    #------------------------------

    ds  = psana.DataSource(dsname)
    env = ds.env()
    det = psana.Detector(detname, env)
    #runnum = ds.runs().next().run()
    calibdir = env.calibDir()
    shape = det.shape(runnum)

    print('experiment  : %s' % exp)
    print('run number  : %d' % runnum)
    print('dsname      : %s' % dsname)
    print('calibdir    : %s' % calibdir)
    print('detnum      : %s' % detnum)
    print('detname     : %s' % detname)
    print('shape       : %s' % str(shape))
    print('common mode : %s' % str(cmpars))
    print('mask bits   : %s' % bin(mask_bits).replace('0b', ''))
    print('do_save     : %s' % str(do_save))
    print('%s' % (50*'_'))

    #mask = det.mask_calib(runnum)
    #mask = det.mask(runnum, calib=True, status=True, edges=True, central=True, unbond=True, unbondnbrs=True)
    #print_ndarr(mask, 'mask')

#------------------------------

    counter =0
    t0_sec  = time()
    for i, evt in enumerate(ds.events()) :

        evnum = i+1

        #nda = det.raw(evt)
        #nda = det.calib(evt, cmpars)
        #nda *= mask
        #In releases >ana-0.17.11 (nightly-20160127) evaluation of combined mask is included in det.calib
        nda = det.calib(evt, cmpars, mbits=mask_bits)

        if nda is None :
            print('Event %d: Detector data IS NOT FOUND' % evnum)
            continue

        counter += 1

        if do_save :
            img = det.image(evt, nda)
            ofname = 'img-%s-r%04d-e%06d-%s.tiff' % (env.experiment(), runnum, evnum, suffix)
            print('Event %4d, save image in file %s' % (evnum, ofname))
            im = Image.fromarray(img.astype(np.int16))
            im.save(ofname)
            #np.savetxt(ofname, img, fmt='%8.1f', delimiter=' ', newline='\n')

        else :
            print('\nEvent %d' % (evnum))
            print_ndarr(nda, 'cspad raw')

    print('Detector data found in %d events, processing time %.3f sec' % (counter, time()-t0_sec))

#------------------------------

def usage() :   
    """Prints hints about usage of this script"""
    scrname = sys.argv[0]
    msg = '%s'\
          '\nCommand : %s'\
          '\nDoc-str : %s'\
          '\nUsage   : %s <experient> <run-number> <detector-number-[0-4]>'\
          '\nExample : %s mecj5515 102 1'\
          '\n%s\n' % (100*'_',' '.join(sys.argv), example01.__doc__, scrname, scrname, 100*'_')
    print(msg)
    
#------------------------------

if __name__ == "__main__" :
    usage()
    if len(sys.argv)==4: example01()
    else : print('WARNING: Wrong parameters, see comment on Usage.')
    sys.exit(0)

#------------------------------
