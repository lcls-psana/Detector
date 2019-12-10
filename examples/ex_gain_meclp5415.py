#!/usr/bin/env python

from __future__ import print_function
import sys
from time import time

import psana
from Detector.GlobalUtils import print_ndarr


def ex_01(tname) :
    import numpy as np
    sh=(704, 768)
    arr = 1.001*np.ones(sh, dtype=np.float)
    fname = '0-end.data'
    np.savetxt(fname, arr, fmt='%.3f')
    print('save file: %s' % fname)
    print('mv 0-end.data /reg/d/psdm/MEC/meclp5415/calib/Epix100a::CalibV1/MecTargetChamber.0:Epix100a.0/pixel_gain/')
    print('rm /reg/d/psdm/MEC/meclp5415/calib/Epix100a::CalibV1/MecTargetChamber.0:Epix100a.0/pixel_gain/0-end.data')


def ex_gain(tname) :
    print('\nIn %s' % sys._getframe().f_code.co_name)

    print('test # cases:',\
          '\n    =1 - use standard calib dir (empty -> DCS)',\
          '\n    =2 - use Philip calib dir',\
          '\n    =4 - use local non-empty calib dir',\
          '\n    =3 - use local empty calib dir (empty -> DCS)')

    #default: '/reg/d/psdm/MEC/meclp5415/calib/Epix100a::CalibV1/MecTargetChamber.0:Epix100a.0/pixel_gain/'
    
    if   tname=='1' : pass
    elif tname=='2' : psana.setOption('psana.calib-dir','/reg/neh/home/philiph/psana/meclp5415/calib')
    elif tname=='3' : psana.setOption('psana.calib-dir','./calib_non_empty/calib')
    elif tname=='4' : psana.setOption('psana.calib-dir','./calib_empty/calib')

    ds  = psana.DataSource('exp=meclp5415:run=20:smd')
    env = ds.env()
    #evt = ds.events().next()

    det = psana.Detector('MecTargetChamber.0:Epix100a.0', env)
    #det.print_attributes()

    evid = ds.env().configStore().get(psana.EventId)
    runnum = evid.run()
    runtime = evid.time()[0]
    print(20*'=')
    print('experiment, expNum:',  env.experiment(), env.expNum())
    print('env run:',  runnum)
    print('env time (sec):', runtime)
    print('calibDir:', env.calibDir())
    print('det.source:', det.source)

    from PSCalib.DCFileName import DCFileName
    t0_sec = time()
    o = DCFileName(env, 'Epix', calibdir=env.calibDir())
    #o.print_attrs()
    dt_sec = time()-t0_sec
    print(20*'=', '\nDCS "generic calibration" expected file',\
          '\n  calib path: %s' % o.calib_file_path(),\
          '\n  repo  path: %s' % o.calib_file_path_repo())
    print('  Time to get name (sec) = %.6f' % dt_sec)



    print(20*'=', '\nCheck det.gain')#, 20*'='
    
    t0_sec = time()
    #g = det.gain(evt)    
    g = det.gain(runnum)
    print('  Time to get gain (sec) = %.6f' % (time()-t0_sec))
    print_ndarr(g, '  det.gain(%d)' % runnum)
    print_ndarr(g, '  det.gain(%d)' % runnum, first=100*388, last=100*388+5)

    print(20*'=')

#------------------------------

if __name__ == "__main__" :
    tname = sys.argv[1] if len(sys.argv) > 1 else '1'
    print(50*'_', '\nTest %s:' % tname)
    if   tname in ('1','2','3','4') : ex_gain(tname);
    elif tname == '10' : ex_01(tname)
    else : print('Not-recognized test name: %s' % tname)
    sys.exit('End of test %s' % tname)
 
#------------------------------
