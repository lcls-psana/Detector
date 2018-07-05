#!/usr/bin/env python
#------------------------------
import os
import sys
import psana
import numpy as np
from PIL import Image
from time import time
from Detector.GlobalUtils import print_ndarr
from PSCalib.GeometryAccess import img_from_pixel_arrays
#------------------------------
#psana.setOption('psana.calib-dir', './calib')

def example01() :
    """Saves per event images of MecTargetChamber.0:Cspad0.0 detector quad [0-3] in tiff files."""

    #------------------------------
    print 'PARAMETERS'
    
    exp     =     sys.argv[1]   # ex.: mecj5515
    runnum  = int(sys.argv[2])  # ex.: 102
    quadnum = int(sys.argv[3])  # ex.: 1  from allowed range [0-3]

    dsname  = 'exp=%s:run=%d' % (exp, runnum) # ex: 'exp=mecj5515:run=102'
    detname = 'MecTargetChamber.0:Cspad.0' 
    suffix  = detname.replace(":","-").replace(".","-") #.lower()
    cmpars  = (1,1000,500,100)
    do_save = True
    mask_bits = 0377 # for releases >ana-0.17.11
    #------------------------------

    ds  = psana.DataSource(dsname)
    env = ds.env()
    det = psana.Detector(detname, env)
    calibdir = env.calibDir()
    shape = det.shape(runnum)

    print 'experiment  : %s' % exp
    print 'run number  : %d' % runnum
    print 'dsname      : %s' % dsname
    print 'calibdir    : %s' % calibdir
    print 'quadnum     : %s' % quadnum
    print 'detname     : %s' % detname
    print 'shape       : %s' % str(shape)
    print 'common mode : %s' % str(cmpars)
    print 'mask bits   : %s' % bin(mask_bits).replace('0b', '')
    print 'do_save     : %s' % str(do_save)
    print '%s' % (50*'_')

    iX, iY = det.geometry(runnum).get_pixel_coord_indexes('QUAD:V1', quadnum)
    #print_ndarr(iX, 'iX')
    #print_ndarr(iY, 'iY')
#------------------------------

    counter =0
    t0_sec  = time()
    for i, evt in enumerate(ds.events()) :

        evnum = i+1

        #nda = det.raw(evt)
        #In releases >ana-0.17.11 (nightly-20160127) evaluation of combined mask is included in det.calib
        nda = det.calib(evt, cmpars, mbits=mask_bits)

        if nda is None :
            print 'Event %d: Detector data IS NOT FOUND' % evnum
            continue

        counter += 1

        if do_save :
            nda.shape = (4, 8, 185, 388)
            ndaq = nda[quadnum,:]
            img = img_from_pixel_arrays(iX, iY, W=ndaq)
            #img = det.image(evt, nda)
            ofname = 'img-%s-r%04d-e%06d-%s-quad-%1d.tiff' % (env.experiment(), runnum, evnum, suffix, quadnum)
            print 'Event %4d, save image in file %s' % (evnum, ofname)
            im = Image.fromarray(img.astype(np.int16))
            im.save(ofname)
            #np.savetxt(ofname, img, fmt='%8.1f', delimiter=' ', newline='\n')

        else :
            print('\nEvent %d' % (evnum))
            print_ndarr(nda, 'cspad raw')

    print 'Detector data found in %d events, processing time %.3f sec' % (counter, time()-t0_sec)

#------------------------------

def usage() :   
    """Prints hints about usage of this script"""
    scrname = sys.argv[0]
    msg = '%s'\
          '\nCommand : %s'\
          '\nDoc-str : %s'\
          '\nUsage   : %s <experient> <run-number> <quad-number-[0-3]>'\
          '\nExample : %s mecj5515 102 1'\
          '\n%s\n' % (100*'_',' '.join(sys.argv), example01.__doc__, scrname, scrname, 100*'_')
    print msg
    
#------------------------------

if __name__ == "__main__" :
    usage()
    if len(sys.argv)==4: example01()
    else : print 'WARNING: Wrong parameters, see comment on Usage.'
    sys.exit(0)

#------------------------------
