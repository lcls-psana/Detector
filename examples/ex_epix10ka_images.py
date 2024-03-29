#!/usr/bin/env python
#from __future__ import print_function
#from __future__ import division

import sys
import numpy as np
from time import time

import psana
from Detector.UtilsEpix10ka import calib_epix10ka_any, map_pixel_gain_mode_for_raw
from Detector.GlobalUtils import print_ndarr
import PSCalib.GlobalUtils as gu

import pyimgalgos.GlobalGraphics as gg
import pyimgalgos.Graphics as gr

EVSKIP  = 100
EVENTS  = 10 + EVSKIP
PLOT_IMG      = True #False #True
PLOT_GAIN_MAP = False #True #False #True
PLOT_SPE      = False
PLOT_ANY      = PLOT_IMG or PLOT_SPE or PLOT_GAIN_MAP

# /reg/d/psdm/det/detdaq17/e968-r0131   - source unmasked (up to ~ event 10000), then masked vertically after ~ event 15000
# /reg/d/psdm/det/detdaq17/e968-r0132   - source masked horizontally at bottom after ~ event 15000.

def dsname_source(tname):

    psana.setOption('psana.calib-dir', '/reg/g/psdm/detector/data_test/calib/')

    if   tname=='1': return 'exp=mfxx32516:run=377', 'MfxEndstation.0:Epix10ka.0' # Dark. Auto H to L, filter dac 1E, integration 50
    elif tname=='2': return 'exp=mfxx32516:run=368', 'MfxEndstation.0:Epix10ka.0' # Dark. fixed high, filter dac 11, integration 100
    elif tname=='3': return 'exp=mfxx32516:run=365', 'MfxEndstation.0:Epix10ka.0' # fixed low
    elif tname=='4': return 'exp=mfxx32516:run=363', 'MfxEndstation.0:Epix10ka.0' # fixed high
    elif tname=='5': return 'exp=detdaq17:run=131',  'DetLab.0:Epix10ka2M.0' # fixed high
    elif tname=='6': return 'exp=xcsx35617:run=6',   'XcsEndstation.0:Epix10ka2M.0' # fixed high
    elif tname=='7': return 'exp=xcsx35617:run=12',  'XcsEndstation.0:Epix10ka2M.0' # fixed high
    elif tname=='8':
        psana.setOption('psana.calib-dir', '/reg/neh/home/dubrovin/LCLS/con-detector/calib/')
        #psana.setOption('psana.calib-dir', '/reg/d/psdm/XCS/xcsx35617/calib')

        #return 'exp=xcsx35617:run=528',  'XcsEndstation.0:Epix10ka2M.0' # FH, FM, ... all
        #return 'exp=xcsx35617:run=394',  'XcsEndstation.0:Epix10ka2M.0' # FH
        #return 'exp=xcsx35617:run=419',  'XcsEndstation.0:Epix10ka2M.0' # AML
        return 'exp=xcsx35617:run=414',  'XcsEndstation.0:Epix10ka2M.0' # AHL
    elif tname=='9':
        # /reg/d/psdm/MFX/mfxc00118/calib/Epix10ka2M::CalibV1/MfxEndstation.0:Epix10ka2M.0/pedestals/
        #psana.setOption('psana.calib-dir', '/reg/g/psdm/detector/gains/epix10k/calib/')
        psana.setOption('psana.calib-dir', '/reg/d/psdm/MFX/mfxc00118/calib/')
        return 'exp=mfxc00118:run=41', 'MfxEndstation.0:Epix10ka2M.0' # silver behranate
    elif tname=='10':
        psana.setOption('psana.calib-dir', '/reg/d/psdm/MFX/mfxc00118/calib/')
        return 'exp=mfxc00118:run=70:smd', 'MfxEndstation.0:Epix10ka2M.0' # run=70,71,72,73: Fe55 in Q0,Q1,Q2,Q3
    else:
        print('Example for\n dataset: %s\n source: %s \nis not implemented' % (dsname, src))
        sys.exit(0)


def selected_record(nrec):
    return nrec<5\
       or (nrec<50 and not nrec%10)\
       or (not nrec%100)
       #or (nrec<500 and not nrec%100)\


def test_epix10ka_methods(tname):

    dsname, src = dsname_source(tname)
    runnum = int(dsname.split(':')[1].split('=')[1])

    ds  = psana.DataSource(dsname)
    env = ds.env()
    pssrc = psana.Source(src)

    print('experiment %s' % env.experiment())
    print('run        %d' % runnum)
    print('dataset    %s' % (dsname))
    print('calibDir:', env.calibDir())

    #for key in evt.keys(): print key

    figim,  axim,  axcb,  imsh  = gg.fig_axim_axcb_imsh(figsize=(13,12)) if PLOT_IMG      else (None, None, None, None)
    figim2, axim2, axcb2, imsh2 = gg.fig_axim_axcb_imsh(figsize=(13,12)) if PLOT_GAIN_MAP else (None, None, None, None)
    if figim  is not None: gg.move_fig(figim,  300, 0)
    if figim2 is not None: gg.move_fig(figim2, 200, 0)

    fighi, axhi = None, None
    if PLOT_SPE:
        fighi = gr.figure(figsize=(10,6), title='Spectrum', move=(600,0))
        axhi  = gr.add_axes(fighi, axwin=(0.08, 0.08, 0.90, 0.87))

    det = psana.Detector(src, env)

    par = runnum
    shape_nda = det.shape(par)

    print('det.source     : %s' % det.source)
    print('shape of ndarray: %s' % str(det.shape(par)))
    print('size of ndarray: %d' % det.size(par))
    print('ndim of ndarray: %d' % det.ndim(par))

    peds = det.pedestals(par)
    print_ndarr(peds, 'pedestals')

    rms = det.rms(par)
    print_ndarr(rms, 'rms')

    #mask = det.mask(par, calib=False, status=True,\
    #       edges=False, central=False, unbond=False, unbondnbrs=False)

    # mode=0/1/2 masks zero/four/eight neighbors around each bad pixel
    mask = det.mask(par, calib=False, status=True, edges=True, central=True, width=1, wcentral=1, mode=0)
    print_ndarr(mask, 'mask')

    gain = det.gain(par)
    print_ndarr(gain, 'gain')

    #offset = det.offset(par)
    #print_ndarr(offset, 'offset')

    #bkgd = det.bkgd(par)
    #print_ndarr(bkgd, 'bkgd')

    #datast = det.status_data(par)
    #print_ndarr(datast, 'datast')

    status = det.status(par)
    print_ndarr(status, 'status')

    #statmask = det.status_as_mask(par)
    #print_ndarr(statmask, 'statmask')
    #print('number of bad status pixels: %d' % (len(statmask[statmask==0])))

    # mode 0/1/2 masks zero/four/eight neighbors around each bad pixel
    mask_status = det.status_as_mask(par, mode=2, indexes=(0,1,2,3,4)) # indexes=(0,1,2)

    arr1 = np.ones_like(mask_status, dtype=np.uint8)
    print_ndarr(mask_status, 'mask_status')
    num1 = np.select((mask_status>0,), (arr1,), 0).sum()
    print(' ====> mask of status number of 0s: %d and 1s: %d' % (arr1.size-num1, num1))

    cmod = det.common_mode(par)
    print_ndarr(cmod, 'common_mod')

    coords_x = det.coords_x(par)
    print_ndarr(coords_x, 'coords_x')

    coords_y = det.coords_y(par)
    print_ndarr(coords_y, 'coords_y')

    areas = det.areas(par)
    print_ndarr(areas, 'area')

    pixel_size = det.pixel_size(par)
    print('%s\npixel size: %s' % (80*'_', str(pixel_size)))

    # mbits = 1 - mask edges, +2 - mask central
    mask_geo = det.mask_geo(par, mbits=3, width=20, wcentral=5)
    print_ndarr(mask_geo, 'mask_geo')

    ipx, ipy = det.point_indexes(par) # , pxy_um=(0,0))
    print('Detector origin indexes: ix, iy:', ipx, ipy)

    print_ndarr(det.image_xaxis(par), 'image_xaxis')
    print_ndarr(det.image_yaxis(par), 'image_yaxis')

    t0_sec_tot = time()

    sum_nda = None
    counter = 1

    for i, evt in enumerate(ds.events()):

        if selected_record(i): print('%s\nEvent %4d' % (50*'_', i))

        if i <EVSKIP: continue
        if i>=EVENTS: break

        nda_raw = det.raw(evt)

        if nda_raw is None: continue

        t0_sec = time()
        #nda = nda_raw
        nda = calib_epix10ka_any(det, evt)
        #nda = mask_geo + 1
        #nda = mask_status + 1
        #nda = mask + 1
        #nda = peds[3,:,:,:]

        if sum_nda is None: sum_nda = nda
        else:
            sum_nda += nda
            counter += 1

        t1_sec = time()
        #nda *=  mask

        t2_sec = time()
        #nda *=  mask_geo
        #nda *=  mask_status

        if nda is None: continue
        print_ndarr(nda, '%s\nEvent %4d, calib %7.3f sec, mask %7.3f sec' % (50*'_', i, t1_sec-t0_sec, t2_sec-t1_sec))

        #sh = nda.shape
        #nda.shape = (nda.size/sh[-1], sh[-1])

        ndarr = np.array(nda, dtype=np.float32) # * (1./46.7) # factor for default gain=1
        #ndarr *= mask_geo

        #arr_sel = ndarr[6, 10:340, 10:370].copy()
        #ndarr[6, 10:340, 10:370] -= 500

        #arr_sel = ndarr[6, 10:170, 200:350].copy()
        #ndarr[6, 10:170, 200:350] -= 500

        #arr_sel = ndarr[6, 120:170, 200:250].copy()
        #ndarr[6, 120:170, 200:250] -= 500

        #arr_sel = ndarr[1, 10:340, 10:370].copy()
        #ndarr[1, 10:340, 10:370] -= 500

        #arr_sel = ndarr[1, 5:170, 5:185].copy()
        #ndarr[1, 5:170, 5:185] -= 500

        #ave, rms = np.median(ndarr), ndarr.std()
        #print('ave %.3f rms: %.3f' % (ave, rms)

        ave = np.median(ndarr)
        rms = np.median(np.abs(ndarr-ave))
        print('med %.3f spr: %.3f' % (ave, rms))

        #amin, amax = (-1, 10) if tname=='4' else\
        #             (ave-0.1*rms, ave+0.3*rms) if tname=='5' else\
        #             (ave-2*rms, ave+6*rms)
        amin, amax = (ave-0.5*rms, ave+3*rms)
        if   tname=='8': amin, amax = (0, 40000)
        elif tname=='10': amin, amax = (-2.5, 5)

        img = None

        if PLOT_IMG:
            #shape = (16, 352, 384)
            #ndarr[0,:] = 1
            img = det.image(evt, ndarr) # [600:1000, 600:1000] #[300:1300, 300:1300]
            #img = ndarr #; ndarr.shape = (1024,1024) # up and down pannels look flipped

            if img is None:
                print('Image is not available.')
                continue

            ofnnpy = 'img-ev%0002d.npy'%i
            np.save(ofnnpy, img)
            print('saved image %s' % ofnnpy)

            #print_ndarr(img, 'img')

            axim.clear()
            if imsh is not None: del imsh
            imsh = None

            gg.plot_imgcb(figim, axim, axcb, imsh, img, amin=amin, amax=amax, origin='upper', title='Event %d'%i, cmap='inferno')
            #figim.canvas.draw()
            #gg.save_fig(figim, fname=ofnimg, pbits=0)

        if PLOT_SPE:
            #arrhi = nda_raw
            arrhi = ndarr
            #arrhi = img
            arrhi = arr_sel

            axhi.clear()
            #range_x=(0,(1<<16)-1) # (arrhi.min(), arrhi.max())
            #range_x=(arrhi.min(), arrhi.max())
            range_x=(amin, amax)

            print('range_x:', range_x)
            print_ndarr(arrhi, 'arrhi')

            hi = gr.hist(axhi, arrhi.flatten(), bins=100, amp_range=range_x, weights=None, color=None, log=False)
            gr.add_title_labels_to_axes(axhi, title='Event %d'%i, xlabel='Raw data, ADU',\
                                                                  ylabel='Entries', color='k')
            #gr.save_fig(fig, fname='spec-%02d.png'%i, verb=True)

        if PLOT_GAIN_MAP:

            nda_map = map_pixel_gain_mode_for_raw(det, nda_raw) # + 1

            img2 = det.image(evt, nda_map)

            if img2 is None:
                print('Image of the gain map is not available.')
                continue

            #print_ndarr(img2, 'img2')

            axim2.clear()
            if imsh2 is not None: del imsh2
            imsh2 = None

            gg.plot_imgcb(figim2, axim2, axcb2, imsh2, img2, amin=0, amax=7, origin='upper', title='Event %d'%i, cmap='inferno')
            #figim.canvas.draw()
            #gg.save_fig(figim, fname=ofnimg, pbits=0)

        if PLOT_ANY: gr.show(mode='do_not_hold')

    dt_sec_tot = time()-t0_sec_tot
    print('Loop over %d events time = %.3f sec or %.3f sec/event' % (EVENTS, dt_sec_tot, dt_sec_tot/EVENTS))

    if PLOT_ANY: gg.show()

    sum_nda /= counter
    fname = 'nda-averaged.npy'
    np.save(fname, sum_nda)
    print('saved file %s'%fname)
    sum_nda.shape = (sum_nda.size/sum_nda.shape[-1],sum_nda.shape[-1])
    np.savetxt('nda-averaged.txt', sum_nda, fmt='%.3f')


if __name__ == "__main__":

    import logging
    logger = logging.getLogger(__name__)
    logging.basicConfig(format='%(levelname)s: %(message)s', level=logging.DEBUG) #INFO) #DEBUG)

    tname = sys.argv[1] if len(sys.argv)>1 else '1'
    print('%s\nTest %s' % (80*'_', tname))
    test_epix10ka_methods(tname)
    sys.exit ('End of %s' % sys.argv[0])

# EOF
