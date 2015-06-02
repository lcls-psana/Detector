#!/usr/bin/env python

import sys
import psana

from Detector.PyDetector import PyDetector

##-----------------------------
ntest = 1
if len(sys.argv)>1 : ntest = int(sys.argv[1])
print 'Test # %d' % ntest

##-----------------------------

dsname, src                 = 'exp=cxif5315:run=169', psana.Source('DetInfo(CxiDs2.0:Cspad.0)')
if   ntest==2 : dsname, src = 'exp=meca1113:run=376', psana.Source('DetInfo(MecTargetChamber.0:Cspad2x2.1)')
elif ntest==3 : dsname, src = 'exp=amob5114:run=403', psana.Source('DetInfo(Camp.0:pnCCD.0)')
elif ntest==4 : dsname, src = 'exp=xppi0614:run=74',  psana.Source('DetInfo(NoDetector.0:Epix100a.0)')
elif ntest==5 : dsname, src = 'exp=sxrg3715:run=46',  psana.Source('DetInfo(SxrEndstation.0:Andor.2)')
#elif ntest==5 : dsname, src = 'exp=sxrb6813:run=52',  psana.Source('DetInfo(SxrEndstation.0:Andor.0)')
#elif ntest==5 : dsname, src = 'exp=mecb3114:run=17',  psana.Source('DetInfo(MecTargetChamber.0:Andor.1)')
elif ntest==6 : dsname, src = 'exp=sxrf9414:run=72',  psana.Source('DetInfo(SxrEndstation.0:Fccd960.0)')
elif ntest==7 : dsname, src = 'exp=xcsi0112:run=15',  psana.Source('DetInfo(XcsBeamline.0:Princeton.0)')
#elif ntest==8 : dsname, src = '',  psana.Source('DetInfo()')


#/reg/d/psdm/sxr/sxrg3715/calib/Andor::CalibV1/SxrEndstation.0:Andor.2/pedestals/25-end.data


print 'Example for\n  dataset: %s\n  source : %s' % (dsname, src)

# Use non-standard calib directory
#opts = {'psana.calib-dir':'./calib',}
#psana.setOptions(opts)
#psana.setOption('psana.calib-dir', './calib')
psana.setOption('psana.calib-dir', './empty/calib')

ds  = psana.DataSource(dsname)
evt = ds.events().next()
env = ds.env()

#for key in evt.keys() : print key

##-----------------------------

def print_ndarr(nda, name='') :
    if nda is not None :
        print '%s\n%s: \n%s\n shape:%s  size:%d  dtype:%s' % (80*'_', name, nda, str(nda.shape), nda.size, nda.dtype)
    else :
        print '%s\n%s: %s' % (80*'_', name, nda)

##-----------------------------

det = PyDetector(src, env, pbits=0)

ins = det.instrument()

print 80*'_', '\nInstrument: ', ins
#det.set_print_bits(511);
#det.set_def_value(-5.);
#det.set_mode(1);
det.print_members()

peds = det.pedestals(evt)
print_ndarr(peds, 'pedestals')

shape_nda = det.shape(evt)
print_ndarr(shape_nda, 'shape of ndarray')

print 'size of ndarray: %d' % det.size(evt)
print 'ndim of ndarray: %d' % det.ndim(evt)

#####################
#sys.exit('TEST EXIT')
#####################

rms = det.rms(evt)
print_ndarr(rms, 'rms')

gain = det.gain(evt)
print_ndarr(gain, 'gain')

mask = det.mask(evt)
print_ndarr(mask, 'mask')

bkgd = det.bkgd(evt)
print_ndarr(bkgd, 'bkgd')

stat = det.status(evt)
print_ndarr(stat, 'stat')

cmod = det.common_mode(evt)
print_ndarr(cmod, 'common_mod')

nda_raw = det.raw_data(evt)

i=0
if nda_raw is None :
    for i, evt in enumerate(ds.events()) :
        nda_raw = det.raw_data(evt)
        if nda_raw is not None :
            print 'Detector data found in event %d' % i
            break

print_ndarr(nda_raw, 'Raw data')

if nda_raw is None :
    print 'Detector data IS NOT FOUND in %d events' % i
    sys.exit('FURTHER TEST IS TERMINATED')

#det.set_print_bits(511);

# THIS ONLY WORKS IF geometry is available
#nda = det.coords_x(evt)
#print_ndarr(nda, 'coords_x')

img_arr = nda_raw.flatten() - peds.flatten() if peds is not None else nda_raw.flatten()
img = None

# Image producer is different for 3-d and 2-d arrays 
if len(nda_raw.shape) > 2 :
    img = det.image(evt, img_arr)
else :
    img = img_arr
    img.shape = nda_raw.shape

print_ndarr(img, 'Image data-peds')

print 80*'_'
##-----------------------------

if img is None :
    print 'Image is not available'
    sys.exit('FURTHER TEST IS TERMINATED')

import pyimgalgos.GlobalGraphics as gg

ave, rms = img.mean(), img.std()
gg.plotImageLarge(img, amp_range=(ave-1*rms, ave+1*rms))
gg.show()

##-----------------------------

sys.exit(0)
