#!/usr/bin/env python
#------------------------------
"""
   Methods of the Detector interface to psana data:
   https://lcls-psana.github.io/Detector/index.html#module-AreaDetector

   Geometry:
   /reg/g/psdm/detector/data_test/calib/Epix10kaQuad::CalibV1/...
"""
from time import time
import sys
import numpy as np
import psana
from pyimgalgos.GlobalUtils import print_ndarr

#------------------------------

from Detector.UtilsPNCCD import common_mode_pnccd

#------------------------------
EVSKIP  = 10
EVENTS  = EVSKIP + 100

DSNAME  = 'exp=mecx32917:run=93' # 106'
DETNAME = 'MecTargetChamber.0:Epix10kaQuad.2'

psana.setOption('psana.calib-dir', '/reg/g/psdm/detector/data_test/calib')

#------------------------------
#------------------------------

def test_pnccd() :

    ds = psana.DataSource(DSNAME)
    d  = psana.Detector(DETNAME)
    #d.set_print_bits(0177777)
    img = None
    for nev,evt in enumerate(ds.events()):
        if nev < EVSKIP : continue
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

def test_pnccd_graph(tname) :

    test_description(tname)

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
        
    nda_old = None

    ds = psana.DataSource(DSNAME)
    d  = psana.Detector(DETNAME)
    for nev,evt in enumerate(ds.events()):
    
        print '%s\nEvent %4d' % (50*'_', nev)
        if nev < EVSKIP : continue
        if nev > EVENTS : break
 
        if evt is None : continue

        nda = None
        if mask is None : mask = d.mask(evt, calib=True, status=True)
        print_ndarr(d.common_mode(evt), name='common_mode parameters')

        raw = d.raw(evt)
        if raw is None : continue

        #--------------------
        # Default correction
        if   tname=='2' : nda = d.calib(evt) # cmpars=(8,5,500) - def
        elif tname=='3' : nda = d.calib(evt, cmpars=0) # - NO cm correction
        elif tname=='4' : nda = d.calib(evt, cmpars=(8,5,500), mask=mask) # explicit new cmpars
        elif tname=='5' : nda = d.calib(evt, cmpars=(3,348,348,128), mask=mask) # explicit old
        elif tname=='6' : nda = raw
        elif tname=='10' :
            #--------------------
            # DIY corrections
            if peds is None : peds = d.pedestals(evt)
            if mask is None : mask = d.mask(evt, calib=True, status=True)
            #if mask is None : mask = d.mask_calib(evt)
            #if mask is None : mask = d.status_as_mask(evt)
            if gain is None : gain = d.gain(evt)
            
            nda = np.array(raw, dtype=np.float32)
            
            if peds is not None : nda -= peds
            
            #nda = np.multiply(nda, mask)
            if gain is not None : nda *= gain

            #common_mode_pnccd(nda, None, cmp=(8,1,500))  # median in rows 128                  (0.24 s/evt)
            #common_mode_pnccd(nda, mask, cmp=(8,1,500))  # median in rows 128 - main cm corr   (0.36 s/evt)
            #common_mode_pnccd(nda, mask, cmp=(8,2,500))  # median in rows 512                  (0.11 s/evt)
            #common_mode_pnccd(nda, None, cmp=(8,2,500))  # median in rows 512                  (0.08 s/evt)
            #common_mode_pnccd(nda, mask, cmp=(8,4,500))  # median in columns 512               (0.12 s/evt)
            #common_mode_pnccd(nda, None, cmp=(8,4,500))  # median in columns 512               (0.09 s/evt)
            #common_mode_pnccd(nda, mask, cmp=(8,8,500))  # median in banks_512x128             (0.16 s/evt)
            #common_mode_pnccd(nda, None, cmp=(8,8,500))  # median in banks_512x128             (0.25 s/evt) 
            common_mode_pnccd(nda, mask, cmp=(8,5,500))   # median in rows 128 and columns 512  (0.40 s/evt) THE BEST
            #common_mode_pnccd(nda, mask, cmp=(8,7,500))  # median combined                     (0.65 s/evt)
            #common_mode_pnccd(nda, mask, cmp=(8,13,500)) # median combined                     (0.43 s/evt)

            # Implementation through Detector interface:
            #d.common_mode_apply(evt, nda, (3, 348, 348, 128))   # old C++ correction            (0.11 s/evt)
            #d.common_mode_apply(evt, nda, (8,5,500), mask=mask) # new py                        (0.41 s/evt)

        #--------------------
        t0_sec = time()

        print 'ex_pnccd_plot_in_evloop: CM consumed time (sec) =', time()-t0_sec
        #--------------------

        mask_badpix = d.status_as_mask(evt)
        print_ndarr(mask_badpix, name='mask_badpix', first=0, last=5)
        print_ndarr(nda, name='nda', first=0, last=5)
        

        if mask_badpix is not None : nda *= mask_badpix

        #nda = mask
        #nda = gain
        #nda = peds
        #nda = raw

        #--------------------
        #print_ndarr(peds, name='peds', first=0, last=5)
        #print_ndarr(raw, name='raw', first=0, last=5)
        #print_ndarr(nda, name='nda', first=0, last=5)

        #dnda = nda-nda_old if nda_old is not None else nda
        #nda_old = nda

        img = d.image(evt,nda)
        #img = nda; img.shape = (4*512,512)
        
        #print_ndarr(img, name='img', first=0, last=5)
        #--------------------
        # plot image

        ave, rms = np.mean(nda), np.std(nda)
        amin, amax = ave-3*rms, ave+5*rms
        #amin, amax = 2500, 4000

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

def test_description(tname=None) :
    msg = '%s\nAdditional parameter:' % (80*'_')
    df = tname==None
    if df or tname == '1' : msg += '\n 1 - print raw data and calibration constants'
    if df or tname == '2' : msg += '\n 2 - image for d.calib(evt) - default'
    if df or tname == '3' : msg += '\n 3 - image for d.calib(evt, cmpars=0) - NO common mode correction'
    if df or tname == '4' : msg += '\n 4 - image for d.calib(evt, cmpars=(8,5,500), mask=mask) - explicit new cmpars' 
    if df or tname == '5' : msg += '\n 5 - image for d.calib(evt, cmpars=(3,348,348,128), mask=mask) - explicit old'
    if df or tname == '6' : msg += '\n 6 - image for d.raw(evt)'
    if df or tname =='10' : msg += '\n10 - image for DIY correction'
    print(msg)

#------------------------------

if __name__ == "__main__" :
    print 80*'_'
    tname = sys.argv[1] if len(sys.argv)>1 else None
    if   tname == '1' : test_pnccd()
    elif tname in ('2','3','4','5','6','10') : test_pnccd_graph(tname)
    else :
        test_description(tname=None)
        sys.exit ('Not recognized test name: "%s"' % tname)
    sys.exit ('End of %s' % sys.argv[0])

#------------------------------
