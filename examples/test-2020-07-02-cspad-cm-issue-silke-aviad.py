#------------------------------
#import logging
#logger = logging.getLogger(__name__)
#logging.basicConfig(format='[%(levelname).1s] L%(lineno)04d : %(message)s', datefmt='%Y-%m-%dT%H:%M:%S', level=logging._levelNames['DEBUG'])

import psana
import numpy as np
from Detector.GlobalUtils import print_ndarr

DOPLOT = True
SKIP   = 1
EVTMAX = 10 + SKIP

#psana.setOption('psana.calib-dir', '/reg/d/psdm/mfx/mfxn7816/calib')

#ds  = psana.DataSource('/reg/d/psdm/cxi/cxilq5515/xtc/e1076-r0117-s00-c00.xtc')
#ds  = psana.DataSource('exp=cxilq5515:run=117')
#ds  = psana.DataSource('exp=cxilq5515:run=190:smd') # 23020
ds  = psana.DataSource('exp=cxilq5515:run=190:hdf5') # 23041
#ds  = psana.DataSource('/reg/d/psdm/cxi/cxilq5515/hdf5/cxilq5515-r0190.h5') 
    # DOES NOT WORK - eventId is None -> no timestamp -> crash to retreive cm constants from DCS
det = psana.Detector('CxiDs1.0:Cspad.0')
#det.set_print_bits(0o377)

env = ds.env()
print 'Use calib dir: %s', env.calibDir()

if DOPLOT:
    import pyimgalgos.GlobalGraphics as gg
    fig1, axim1, axcb1, imsh1 = gg.fig_axim_axcb_imsh(figsize=(11,10))

img = None
 
for nev,evt in enumerate(ds.events()):

    #if not (nev in (92, 117, 176, 186, 188, 247, 260, 272)) : continue
    #if not(nev%100): print 50*'_','\nEvent total: %04d' % nev
    if nev<SKIP      :
        print 'Common mode parameters: ', det.common_mode(evt)
        continue
    if not (nev<EVTMAX) : break

    print 'Event: %04d' % nev
    #print 50*'_','\nEvent: %04d' % nev
    #for k in evt.keys() : print k

    #nda = det.calib(evt, cmpars=(1,50,25,100))
    nda = det.calib(evt)
    img = det.image(evt, nda)
    if img is None : 
        print '   WARNING: img is None'
        continue

    if DOPLOT:
        ave, rms = img.mean(), img.std()
        amin, amax =  ave-1*rms, ave+6*rms
        gg.plot_imgcb(fig1, axim1, axcb1, imsh1, img, amin=amin, amax=amax, title='Image, ev: %04d' % nev)
        gg.move_fig(fig1, x0=400, y0=30)
        fig1.canvas.draw()
        gg.show(mode='do not hold')

if DOPLOT:
    fname = 'img-cspad-cxilq5515-r117.npy'
    np.save(fname, img)
    print 'Save image in file: %s' % fname
    gg.show()

#------------------------------
