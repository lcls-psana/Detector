#------------------------------
#!/usr/bin/env python

import psana
import numpy as np
from time import sleep
from Detector.GlobalUtils import print_ndarr

import pyimgalgos.GlobalGraphics as gg

SKIP   = 0 # 286
EVTMAX = 6 + SKIP

#ds = psana.DataSource('/reg/g/psdm/detector/data_test/types/0003-CxiDs2.0-Cspad.0-fiber-data.xtc')
#epics_var = psana.Detector('CXI:DS1:MMS:06.RBV')

#mfxn7816 run 26 #EventKey(type=psana.CsPad.DataV2, src='DetInfo(MfxEndstation.0:Cspad.0)', alias='CsPad')

psana.setOption('psana.calib-dir', '/reg/d/psdm/mfx/mfxn7816/calib')
#ds  = psana.DataSource('exp=mfxn7816:run=36')
ds  = psana.DataSource('/reg/g/psdm/detector/data_test/types/0023-MfxEndstation.0-Cspad.0.xtc')
det = psana.Detector('MfxEndstation.0:Cspad.0')
env = ds.env()
print 'Use calib dir: %s', env.calibDir()

fig1, axim1, axcb1, imsh1 = gg.fig_axim_axcb_imsh(figsize=(11,10))
 
for nev,evt in enumerate(ds.events()):

    #if not (nev in (92, 117, 176, 186, 188, 247, 260, 272)) : continue

    if nev<SKIP      : continue
    if not (nev<EVTMAX) : break

    print 50*'_','\nEvent: %04d' % nev
    for k in evt.keys() : print k

    #nda = det.raw(evt) - det.pedestals(evt)
    #nda = det.pedestals(evt)
    #nda = det.gain(evt)

    #nda = det.calib(evt)
    #nda = det.calib(evt, cmpars=(1,200,100,200))
    print 'Common mode parameters: ', det.common_mode(evt)

    #nda -= det.common_mode_correction(evt, nda) # , cmpars=(1,50,50,100))
    #nda = det.gain_mask_non_zero(evt, gain=det._gain_mask_factor)
 
    nda = det.calib(evt, cmpars=(1,50,25,100))
    #nda = det.calib(evt, cmpars=(5,100))
    img = det.image(evt, nda)
    if img is None : continue

    ave, rms = img.mean(), img.std()
    amin, amax =  ave-1*rms, ave+6*rms
    gg.plot_imgcb(fig1, axim1, axcb1, imsh1, img, amin=amin, amax=amax, title='Image, ev: %04d' % nev)
    gg.move_fig(fig1, x0=400, y0=30)
    fig1.canvas.draw()
    #gg.plotImageLarge(img, amp_range=(ave-1*rms, ave+6*rms))
    gg.show(mode='do not hold')
    fname = 'img-cspad-mfxn7816-r36-a.npy'
    np.save(fname, img)
    print 'Save image in file: %s' % fname

    #sleep(3)

gg.show()

#------------------------------
