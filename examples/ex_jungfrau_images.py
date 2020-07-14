#!/usr/bin/env python

import sys
import numpy as np
from time import time

import psana
from Detector.GlobalUtils import print_ndarr
import PSCalib.GlobalUtils as gu

import pyimgalgos.GlobalGraphics as gg
import pyimgalgos.Graphics as gr

#------------------------------
EVSKIP  = 0
EVENTS  = EVSKIP + 7
PLOT_IMG = True #False #True #False
PLOT_SPE = False #True #False #True #False

#------------------------------

def usage():
    return '\n    python %s <test-number>' % sys.argv[0]\
         + '\n            where  <test-number> is one of 1,2,40,41,42,51,52,53,54'\
         + '\n    python %s <experiment> <detector-name> <run-number>' % sys.argv[0]\
         + '\n    python %s cxic00318 jungfrau4M 35' % sys.argv[0]

#------------------------------

def dsname_source(tname):
    if   tname=='1' : return 'exp=xpptut15:run=410', 'Jungfrau512k', 410
    elif tname=='2' : return 'exp=xpptut15:run=430', 'Jungfrau1M',   430
    elif tname=='40': return '/reg/d/psdm/xpp/xpptut13/scratch/cpo/e968-r0177-s01-c00.xtc', 'DetLab.0:Jungfrau.2', 177
    elif tname=='41': return '/reg/d/psdm/det/detdaq17/xtc/e968-r0177-s01-c00.xtc', 'DetLab.0:Jungfrau.2', 177
    elif tname=='42': return '/reg/d/psdm/xpp/xpptut13/scratch/cpo/e968-r0177-s01-c00.xtc', 'DetLab.0:Jungfrau.2', 177
    elif tname=='51': return 'exp=detdaq17:run=178', 'DetLab.0:Jungfrau.3', 178
    elif tname=='52': return 'exp=detdaq17:run=179', 'DetLab.0:Jungfrau.3', 179
    elif tname=='53': return 'exp=detdaq17:run=180', 'DetLab.0:Jungfrau.3', 180
    elif tname=='54': return 'exp=cxic00318:run=35', 'CxiDs1.0:Jungfrau.0', 35
    elif len(sys.argv)==4:
        print 'command example: %s' % usage()
        exp, detname, runnum = sys.argv[1], sys.argv[2], int(sys.argv[3])
        return 'exp=%s:run=%d'%(exp, runnum), detname, runnum

    else: sys.exit('Not recognized test name: "%s"\n  try command:%s' % (tname, usage()))


    # MISSING DATA
    #elif tname=='1' : return 'exp=cxi11216:run=9',    'CxiEndstation.0:Jungfrau.0', None # 9,11,12 - dark for gain modes
    #elif tname=='2' : return 'exp=xcsx22015:run=503', 'XcsEndstation.0:Jungfrau.0', None # dark: 503, 504, 505
    #elif tname=='20': return 'exp=xcsx22015:run=508', 'XcsEndstation.0:Jungfrau.0', None # dark: 508, 509, 510; 516, 517, 518
    #elif tname=='21': return 'exp=xcsx22015:run=509', 'XcsEndstation.0:Jungfrau.0', None 
    #elif tname=='22': return 'exp=xcsx22015:run=510', 'XcsEndstation.0:Jungfrau.0', None 
    #elif tname=='3' : return 'exp=xcsx22015:run=513', 'XcsEndstation.0:Jungfrau.0', None # data with variable gain
    #elif tname=='4' : return 'exp=xcsx22015:run=552', 'XcsEndstation.0:Jungfrau.0', None # Silver behenate, attenuation 1.2e-2
    #elif tname=='5' : return 'exp=mfx11116:run=624',  'MfxEndstation.0:Jungfrau.0', None
    #elif tname=='6' : return 'exp=mfx11116:run=689',  'MfxEndstation.0:Jungfrau.1', None # Philip test 0.5M constants
    #elif tname=='30': return 'exp=mfxls1016:run=369', 'MfxEndstation.0:Jungfrau.1', None # dark:369 test for clemens

#------------------------------
    
def test_jungfrau_methods(tname):

    if tname in ('51','52','53'): psana.setOption('psana.calib-dir', '/reg/neh/home/dubrovin/LCLS/con-detector/calib')

    dsname, src, rnum = dsname_source(tname)
    runnum = rnum if rnum is not None else int(dsname.split(':')[1].split('=')[1])

    ds  = psana.DataSource(dsname)
    env = ds.env()
    
    print 'experiment %s' % env.experiment()
    print 'run        %d' % runnum
    print 'dataset    %s' % (dsname) 
    print 'calibDir:', env.calibDir()

    #for key in evt.keys(): print key

    ##-----------------------------
    figim, axim, axcb, imsh = gg.fig_axim_axcb_imsh(figsize=(13,12)) if PLOT_IMG else (None, None, None, None)
    if figim is not None: gg.move_fig(figim, 300, 0)

    fighi, axhi = None, None
    if PLOT_SPE:
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

    if statmask is not None:
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

    for i, evt in enumerate(ds.events()):
        print '%s\nEvent %4d' % (50*'_', i)

        if i <EVSKIP: continue
        if i>=EVENTS: break

        t0_sec = time()
        nda_raw = det.raw(evt)
        if nda_raw is None: 
            print('raw is None')
            continue

        print_ndarr(nda_raw, 'nda_raw')

        raw_fake = None # 1000*np.ones((2, 512, 1024), dtype=np.uint16)
        nda = det.calib(evt, cmpars=(7,3,100), nda_raw=raw_fake) # cmpars=(7,1,100)

        if nda is None: 
            print('det.calib() is None, so plot det.raw()')
            nda = nda_raw
        else:
            print_ndarr(nda, 'det.calib')

        if tname=='42':
            det_shape = nsegs, nrows, ncols = (8, 512, 1024)
            size = nsegs*nrows*ncols
            nda = np.arange(size, dtype=np.uint32)
            nda.shape = det_shape

            row_asc  = np.arange(nrows, dtype=np.uint32)
            col_asc  = np.arange(ncols, dtype=np.uint32)
            seg_rows, seg_cols = np.meshgrid(row_asc, col_asc)
            nda[0,seg_rows,seg_cols] = (seg_rows*ncols + seg_cols*nrows)*4

        print '    Consumed time for det.raw/calib(evt) = %7.3f sec' % (time()-t0_sec)
        print_ndarr(nda, 'data nda')

        ave,  rms  = None, None
        amin, amax = None, None

        if PLOT_IMG:
            ndarr = np.array(nda)
            ndarr *= mask_geo
    
            img = det.image(evt, ndarr)
            #img = ndarr; ndarr.shape = (1024,1024) # up and down pannels look flipped 

            if img is None:
                print 'Image is not available.'
                continue

            #print_ndarr(img, 'img')

            axim.clear()
            if imsh is not None: del imsh
            imsh = None

            ave, rms = ndarr.mean(), ndarr.std()

            print 'ave, rms=', ave, rms
            amin, amax = (-1, 10) if tname=='4' else\
                         (ave-0.1*rms, ave+0.3*rms) if tname=='5' else\
                         (-1, 1) if tname=='30' else\
                         (0,size) if tname=='42' else\
                         (ave-1*rms, ave+1*rms)
                         #(57000,57800) if tname in ('40','41') else\
            gg.plot_imgcb(figim, axim, axcb, imsh, img, amin=amin, amax=amax, origin='upper', title='Event %d'%i, cmap='jet') # , cmap='inferno'
            #figim.canvas.draw()
            #gg.save_fig(figim, fname=ofnimg, pbits=0)
            gr.show(mode='do_not_hold')
            gg.save('img.png', True)

        if PLOT_SPE:
            #arrhi = ndarr # nda_raw
            #arrhi, range_x = nda_raw,(0,(1<<16)-1)
            #arrhi, range_x = ndarr, (-2,2)
            #arrhi, range_x = ndarr, (ave-1*rms, ave+1*rms) 
            arrhi, range_x = ndarr, (amin, amax) 
            #range_x=(0,(1<<16)-1) # (arrhi.min(), arrhi.max())

            axhi.clear()
            hi = gr.hist(axhi, arrhi.flatten(), bins=100, amp_range=range_x, weights=None, color=None, log=True)
            gr.add_title_labels_to_axes(axhi, title='Event %d'%i, xlabel='Raw data, ADU',\
                                                                  ylabel='Entries', color='k')
            #gr.save_fig(fig, fname='spec-%02d.png'%i, verb=True)

        if PLOT_IMG or PLOT_SPE:
            gr.show(mode='do_not_hold')

    dt_sec_tot = time()-t0_sec_tot
    print 'Loop over %d events time = %.3f sec or %.3f sec/event' % (EVENTS, dt_sec_tot, dt_sec_tot/EVENTS)

    if PLOT_IMG or PLOT_SPE: gg.show()

    ##-----------------------------
    #sys.exit('TEST EXIT')
    ##-----------------------------

#------------------------------

if __name__ == "__main__":
    tname = sys.argv[1] if len(sys.argv)>1 else '0'
    print '%s\nTest %s' % (80*'_', tname)
    test_jungfrau_methods(tname)
    print 'command example: %s' % usage()
    sys.exit ('End of %s' % sys.argv[0])

#------------------------------
