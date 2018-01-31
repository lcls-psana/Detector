#!/usr/bin/env python
#------------------------------
"""
   Methods of the Detector interface to psana data:
   https://lcls-psana.github.io/Detector/index.html#module-AreaDetector

   Geometry:
   /reg/d/psdm/sxr/sxrx22915/calib/PNCCD::CalibV1/Camp.0:pnCCD.1/geometry/0-end.data

   Pedestals:
   /reg/d/psdm/sxr/sxrx22915/calib/PNCCD::CalibV1/Camp.0:pnCCD.1/pedestals/96-end.data
"""
from time import time
import sys
import numpy as np
import psana
from pyimgalgos.GlobalUtils import print_ndarr

#------------------------------

from Detector.UtilsPNCCD import common_mode_pnccd

#------------------------------

EVENTS  = 10

DSNAME  = 'exp=sxrx22915:run=104'
DETNAME = 'Camp.0:pnCCD.1' # 'pnccd'

#DSNAME  = 'exp=xpptut15:run=340'
#DETNAME = 'Camp.0:pnCCD.0' # 'pnccdFront'

#------------------------------
#------------------------------

def test_pnccd() :
    ds = psana.DataSource(DSNAME)
    d  = psana.Detector(DETNAME)
    img = None
    for nev,evt in enumerate(ds.events()):
    
        if nev > EVENTS : break
    
        print '%s\nEvent %4d' % (50*'_', nev)

        print_ndarr(d.raw(evt),            name='raw        ', first=0, last=5)
        print_ndarr(d.calib(evt),          name='calib      ', first=0, last=5)
        print_ndarr(d.gain(evt),           name='gain       ', first=0, last=5)
        print_ndarr(d.pedestals(evt),      name='pedestals  ')
        print_ndarr(d.status(evt),         name='status     ')
        print_ndarr(d.mask(evt),           name='mask       ', first=0, last=5)
        print_ndarr(d.status_as_mask(evt), name='status mask', first=0, last=5)
        print_ndarr(d.common_mode(evt),    name='common_mode')

#------------------------------

def test_pnccd_graph() :

    from pyimgalgos.GlobalGraphics import fig_axes, plot_imgcb, show #, hist1d
    from pyimgalgos.Graphics import figure, add_axes, hist

    fig, axim, axcb = fig_axes(figsize=(10,7),\
                               win_axim=(0.05,  0.03, 0.87, 0.93),\
                               win_axcb=(0.923, 0.03, 0.02, 0.93))

    fighi = figure(figsize=(6,5), title='Spectrum', dpi=80, facecolor='w', edgecolor='w', frameon=True, move=(800,0))
    axhi  = add_axes(fighi, axwin=(0.15, 0.10, 0.83, 0.85))
    imsh, hi = None, None

    peds = None
    mask = None
    gain = None

    ds = psana.DataSource(DSNAME)
    d  = psana.Detector(DETNAME)
    for nev,evt in enumerate(ds.events()):
    
        if nev > EVENTS : break
        print '%s\nEvent %4d' % (50*'_', nev)

        if evt is None : continue

        #--------------------
        # Default corrections
        #nda = d.calib(evt) # cmpars=(3.  348.  348.  128.) - def

        #--------------------
        # DIY corrections
        if peds is None : peds = d.pedestals(evt)
        if mask is None : mask = d.mask(evt, calib=True, status=True)
        #if mask is None : mask = d.mask_calib(evt)
        #if mask is None : mask = d.status_as_mask(evt)
        if gain is None : gain = d.gain(evt)

        raw = d.raw(evt)
        if raw is None : continue
        nda = np.array(raw, dtype=np.float32)

        if peds is not None : nda -= peds

        #nda = np.multiply(nda, mask)

        #--------------------
        t0_sec = time()

        #d.common_mode_apply(evt, nda, cmpars=(3, 348, 348, 128)) # C++ correction           (0.11 s/evt)
        #common_mode_pnccd(nda, None, cmp=(8,1,500))  # median in rows                      (0.24 s/evt)
        #common_mode_pnccd(nda, mask, cmp=(8,1,500))  # median in rows 128 - main cm corr   (0.36 s/evt)
        #common_mode_pnccd(nda, mask, cmp=(8,2,500))  # median in rows 512                  (0.11 s/evt)
        #common_mode_pnccd(nda, None, cmp=(8,2,500))  # median in rows 512                  (0.08 s/evt)
        #common_mode_pnccd(nda, mask, cmp=(8,4,500))  # median in columns 512               (0.12 s/evt)
        #common_mode_pnccd(nda, None, cmp=(8,4,500))  # median in columns 512               (0.09 s/evt)
        common_mode_pnccd(nda, mask, cmp=(8,5,500))  # median in rows 128 and columns 512  (0.43 s/evt) THE BEST
        #common_mode_pnccd(nda, mask, cmp=(8,7,500))  # median in rows 128 and columns 512  (0.65 s/evt)
    
        print 'ex_pnccd_plot_in_evloop: CM consumed time (sec) =', time()-t0_sec
        #--------------------

        if gain is not None : nda *= gain
        #if mask is not None : nda *= mask

        #nda = mask
        #nda = gain
        #nda = peds
        #nda = raw

        #--------------------
        #print_ndarr(peds, name='peds', first=0, last=5)
        #print_ndarr(raw, name='raw', first=0, last=5)
        #print_ndarr(nda, name='nda', first=0, last=5)

        img = d.image(evt,nda)
        #img = nda; img.shape = (4*512,512)

        
        #print_ndarr(img, name='img', first=0, last=5)
        #--------------------
        # plot image

        ave, rms = np.mean(nda), np.std(nda)
        amin, amax = ave-3*rms, ave+5*rms

        axim.clear()
        del imsh; imsh = None        
        plot_imgcb(fig, axim, axcb, imsh, img, amin, amax, title='Event %d'%nev, cmap='jet') # 'inferno'
        
        #--------------------
        # plot spectral histogram

        axhi.clear()
        del hi;
        hi = hist(axhi, nda, bins=200, amp_range=(amin, amax), weights=None, color=None, log=False) 
        axhi.set_title('Event %d'%nev, fontsize=12)
        axhi.set_xlabel('ADU', fontsize=10)
        axhi.set_ylabel('Entries', fontsize=10)

        show(mode='Do not hold')
    show()

    ofname = 'pnccd-img.npy'
    np.save(ofname, img)
    print 'Last image array saved in %s' % ofname

    ofname = 'pnccd-nda.npy'
    np.save(ofname, nda)
    print 'Last n-d array saved in %s' % ofname

#------------------------------

if __name__ == "__main__" :
    print 80*'_'
    tname = sys.argv[1] if len(sys.argv)>1 else '1'
    if   tname == '1' : test_pnccd()
    elif tname == '2' : test_pnccd_graph()
    else : sys.exit ('Not recognized test name: "%s"' % tname)
    sys.exit ('End of %s' % sys.argv[0])

#------------------------------
