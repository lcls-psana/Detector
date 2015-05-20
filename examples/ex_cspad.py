#!/usr/bin/env python

import sys
import psana

from Detector.PyDetector import PyDetector

ds  = psana.DataSource('exp=cxif5315:run=169')
evt = ds.events().next()
env = ds.env()

src = psana.Source('DetInfo(CxiDs2.0:Cspad.0)')

#for key in evt.keys() : print key

def print_ndarr(nda, name='') :
    print '\n%s: %s' % (name, nda)
    print '      shape:%s  size:%d  dtype:%s' % (str(nda.shape), nda.size, nda.dtype)

det = PyDetector(src,env)

peds = det.pedestals(evt)
#print '\npedestals:\n', peds[0:20]
print_ndarr(peds, 'pedestals')

rms = det.rms(evt)
print_ndarr(rms, 'rms')

gain = det.gain(evt)
print_ndarr(gain, 'gain')
#print '\npixel_gain:\n', pgain[0:20]

mask = det.mask(evt)
print_ndarr(mask, 'mask')
#print '\npixel_mask:\n', pmask[0:20]

bkgd = det.bkgd(evt)
print_ndarr(bkgd, 'bkgd')
#print '\npixel_bkgd:\n', pbkgd[0:20]

stat = det.status(evt)
print_ndarr(stat, 'stat')
#print '\npixel_status:\n', pstat[0:20]

cmod = det.common_mode(evt)
print_ndarr(cmod, 'cmod')
#print '\ncommon_mode:\n', pcmod

ins = det.inst()
print '\nInstrument: ', ins

#det.set_print_bits(255);
#det.set_def_value(-5.);
#det.set_mode(1);

nda = det.coords_x(evt)
print_ndarr(nda, 'coords_x')

nda_raw = det.raw_data(evt)
print_ndarr(nda_raw, 'Raw data')

data = nda_raw.flatten() - peds
img = det.image(evt, data)
print_ndarr(img, 'Image data-peds')

##-----------------------------

import pyimgalgos.GlobalGraphics as gg

ave, rms = img.mean(), img.std()
gg.plotImageLarge(img, amp_range=(ave-1*rms, ave+1*rms))
gg.show()

##-----------------------------

sys.exit(0)
