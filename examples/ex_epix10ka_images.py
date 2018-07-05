####!/usr/bin/env python

import sys
import numpy as np
from time import time

import psana
from Detector.UtilsEpix import calib_epix10ka
from Detector.GlobalUtils import print_ndarr
import PSCalib.GlobalUtils as gu

import pyimgalgos.GlobalGraphics as gg
import pyimgalgos.Graphics as gr

#------------------------------
EVSKIP  = 10
EVENTS  = EVSKIP + 10
PLOT_IMG = True #False #True #False
PLOT_SPE = True #False #True #False

#------------------------------

def dsname_source(tname) :
    if   tname=='1' : return 'exp=mfxx32516:run=377', 'MfxEndstation.0:Epix10ka.0' # Dark. Auto H to L, filter dac 1E, integration 50
    elif tname=='2' : return 'exp=mfxx32516:run=368', 'MfxEndstation.0:Epix10ka.0' # Dark. fixed high, filter dac 11, integration 100
    elif tname=='3' : return 'exp=mfxx32516:run=365', 'MfxEndstation.0:Epix10ka.0' # fixed low
    elif tname=='4' : return 'exp=mfxx32516:run=363', 'MfxEndstation.0:Epix10ka.0' # fixed high
    else :
        print 'Example for\n dataset: %s\n source : %s \nis not implemented' % (dsname, src)
        sys.exit(0)

#------------------------------
    
def test_epix10ka_methods(tname) :

    dsname, src = dsname_source(tname)
    runnum = int(dsname.split(':')[1].split('=')[1])

    ds  = psana.DataSource(dsname)
    env = ds.env()
    pssrc = psana.Source(src)

    print 'experiment %s' % env.experiment()
    print 'run        %d' % runnum
    print 'dataset    %s' % (dsname) 
    print 'calibDir:', env.calibDir()

    #for key in evt.keys() : print key

    ##-----------------------------
    figim, axim, axcb, imsh = gg.fig_axim_axcb_imsh(figsize=(13,12)) if PLOT_IMG else (None, None, None, None)
    if figim is not None : gg.move_fig(figim, 300, 0)

    fighi, axhi = None, None
    if PLOT_IMG :
        fighi = gr.figure(figsize=(10,6), title='Spectrum', move=(600,0))
        axhi  = gr.add_axes(fighi, axwin=(0.08, 0.08, 0.90, 0.87)) 

    ##-----------------------------

    det = psana.Detector(src, env)

    par = runnum
    shape_nda = det.shape(par)
    print 'det.source      : %s' % det.source
    print 'shape of ndarray: %s' % str(det.shape(par))
    print 'size of ndarray : %d' % det.size(par)
    print 'ndim of ndarray : %d' % det.ndim(par)

    peds = det.pedestals(par)
    print_ndarr(peds, 'pedestals')
    
    rms = det.rms(par)
    print_ndarr(rms, 'rms')
    
    mask = det.mask(par, calib=False, status=True,\
           edges=False, central=False, unbond=False, unbondnbrs=False)
    print_ndarr(mask, 'mask')
    
    gain = det.gain(par)
    print_ndarr(gain, 'gain')
    
    offset = det.offset(par)
    print_ndarr(offset, 'offset')
    
    bkgd = det.bkgd(par)
    print_ndarr(bkgd, 'bkgd')
    
    datast = det.datast(par)
    print_ndarr(datast, 'datast')

    status = det.status(par)
    print_ndarr(status, 'status')

    statmask = det.status_as_mask(par)
    print_ndarr(statmask, 'statmask')
    print 'number of bad status pixels: %d' % (len(statmask[statmask==0]))

    status_mask = det.status_as_mask(par)
    print_ndarr(status_mask, 'status_mask')
    
    cmod = det.common_mode(par)
    print_ndarr(cmod, 'common_mod')

    coords_x = det.coords_x(par)
    print_ndarr(coords_x, 'coords_x')

    coords_y = det.coords_y(par)
    print_ndarr(coords_y, 'coords_y')

    areas = det.areas(par)
    print_ndarr(areas, 'area')

    pixel_size = det.pixel_size(par)
    print '%s\npixel size: %s' % (80*'_', str(pixel_size))
    
    mask_geo = det.mask_geo(par, mbits=3, width=1)
    print_ndarr(mask_geo, 'mask_geo')

    ipx, ipy = det.point_indexes(par) # , pxy_um=(0,0)) 
    print 'Detector origin indexes: ix, iy:', ipx, ipy

    print_ndarr(det.image_xaxis(par), 'image_xaxis')
    print_ndarr(det.image_yaxis(par), 'image_yaxis')
    
    t0_sec_tot = time()

    for i, evt in enumerate(ds.events()) :
        print '%s\nEvent %4d' % (50*'_', i)

        if i <EVSKIP: continue
        if i>=EVENTS: break

        t0_sec = time()
        nda_raw = det.raw(evt)

        #if nda_raw is None : continue
        #====================================
        #nda = nda_raw
        nda = calib_epix10ka(det, evt, pssrc)
        #====================================

        if nda is None : continue
        print '    Consumed time for det.raw/calib(evt) = %7.3f sec' % (time()-t0_sec)
        print_ndarr(nda, 'data nda')

        sh = nda.shape
        nda.shape = (sh[-2], sh[-1])

        if PLOT_IMG :
            ndarr = np.array(nda)
            #ndarr *= mask_geo
    
            #img = det.image(evt, ndarr)
            img = ndarr #; ndarr.shape = (1024,1024) # up and down pannels look flipped 
        
            if img is None :
                print 'Image is not available.'
                continue

            #print_ndarr(img, 'img')

            axim.clear()
            if imsh is not None : del imsh
            imsh = None

            ave, rms = ndarr.mean(), ndarr.std()
            #amin, amax = (-1, 10) if tname=='4' else\
            #             (ave-0.1*rms, ave+0.3*rms) if tname=='5' else\
            #             (ave-2*rms, ave+6*rms)
            amin, amax = (ave-2*rms, ave+6*rms)

            gg.plot_imgcb(figim, axim, axcb, imsh, img, amin=amin, amax=amax, origin='upper', title='Event %d'%i, cmap='inferno')
            #figim.canvas.draw()
            #gg.save_fig(figim, fname=ofnimg, pbits=0)

        if PLOT_SPE :
            #arrhi = nda_raw
            arrhi = nda
            axhi.clear()
            range_x=(0,(1<<16)-1) # (arrhi.min(), arrhi.max())
            hi = gr.hist(axhi, arrhi.flatten(), bins=100, amp_range=range_x, weights=None, color=None, log=True)
            gr.add_title_labels_to_axes(axhi, title='Event %d'%i, xlabel='Raw data, ADU',\
                                                                  ylabel='Entries', color='k')
            #gr.save_fig(fig, fname='spec-%02d.png'%i, verb=True)

        if PLOT_IMG or PLOT_SPE :
            gr.show(mode='do_not_hold')

    dt_sec_tot = time()-t0_sec_tot
    print 'Loop over %d events time = %.3f sec or %.3f sec/event' % (EVENTS, dt_sec_tot, dt_sec_tot/EVENTS)

    if PLOT_IMG or PLOT_SPE : gg.show()

    ##-----------------------------
    #sys.exit('TEST EXIT')
    ##-----------------------------

#------------------------------

if __name__ == "__main__" :

    import logging
    logger = logging.getLogger(__name__)
    logging.basicConfig(format='%(levelname)s: %(message)s', level=logging.DEBUG)

    tname = sys.argv[1] if len(sys.argv)>1 else '1'
    print '%s\nTest %s' % (80*'_', tname)
    test_epix10ka_methods(tname)
    sys.exit ('End of %s' % sys.argv[0])

#------------------------------
