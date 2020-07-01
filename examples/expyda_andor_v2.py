#!/usr/bin/env python
##-----------------------------

from __future__ import print_function
import sys
import psana
#import Detector
from Detector.PyDetectorAccess import PyDetectorAccess
from Detector.GlobalUtils import print_ndarr
from time import time

##-----------------------------

#EventKey(type=psana.Andor.FrameV1, src='DetInfo(SxrEndstation.0:Andor.0)')

ds  = psana.DataSource('/reg/g/psdm/detector/data_test/types/0013-SxrEndstation.0-Andor.0.xtc') # exp=sxrb6813:run=34

env = ds.env()
calibdir = env.calibDir()
print('calibdir = %s' % calibdir)

#evt = ds.events().next()
#rnum = evt.run()

src = psana.Source('DetInfo(SxrEndstation.0:Andor.0)')
pda = PyDetectorAccess(src, env, pbits=0)

for i,evt in enumerate(ds.events()) :
    nda = pda.raw_data(evt, env)
    if nda is not None :
        print('Event %4d' % i, end=' ')
        print_ndarr(nda, 'raw data')
        break
    #print(evt.keys())

##-----------------------------
t0_sec = time()
##-----------------------------

rnum = evt.run()
print('run number %d' % rnum)

if True :
    img = nda
    import pyimgalgos.GlobalGraphics as gg
    ave, rms = img.mean(), img.std()
    gg.plotImageLarge(img, amp_range=(ave-1*rms, ave+2*rms))
    gg.show()


print('shape_config', pda.shape_config(env))

from Detector.PyDataAccess import get_andor_config_object

o = get_andor_config_object(env, src)

print('frameSize ', o.frameSize())  # 524300
print('numPixels ', o.numPixels())  # 262144
print('numPixelsX', o.numPixelsX()) # 512
print('numPixelsY', o.numPixelsY()) # 512
print('width()   ', o.width())      # 2048 
print('height()  ', o.height())     # 2048
print('binX()    ', o.binX())       # 4
print('binY()    ', o.binY())       # 4

##-----------------------------

sys.exit('End of test %s' % sys.argv[0])

##-----------------------------
