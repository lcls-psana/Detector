#!/usr/bin/env python

from __future__ import print_function
import sys
from time import time
import psana
from Detector.GlobalUtils import print_ndarr
import PSCalib.GlobalUtils as gu


def test_jungfrau_methods(dsname, src):

    #psana.setOption('psana.calib-dir', './calib')
    #/reg/d/psdm/xpp/xpptut13/calib/Jungfrau::CalibV1/DetLab.0:Jungfrau.2/geometry/1-end.data
    #/reg/d/psdm/det/detdaq17/calib/Jungfrau::CalibV1/DetLab.0:Jungfrau.2/geometry/1-end.data

    ds  = psana.DataSource(dsname)
    evt = next(ds.events())
    env = ds.env()
    nrun = evt.run()

    print('experiment %s' % env.experiment())
    print('Run number %d' % nrun)
    print('dataset exp=%s:run=%d' % (env.experiment(),nrun))
    print('calibDir:', env.calibDir())

    for key in evt.keys(): print(key)

    par = nrun # evt or nrun
    par = evt
    det = psana.Detector(src, env)

    ins = det.instrument()
    print(80*'_', '\nInstrument: ', ins)
    print('src:', src)

    #det.set_print_bits(0)
    det.set_print_bits(1023)
    #det.set_def_value(-5.)
    #det.set_mode(1)
    #det.set_do_offset(True) # works for ex. Opal1000
    #det.print_attributes()
    print('det.source:', det.source)

    shape_nda = det.shape(par)
    print_ndarr(shape_nda, 'shape of ndarray')

    print('size of ndarray: %d' % det.size(par))
    print('ndim of ndarray: %d' % det.ndim(par))

    #peds = det.pedestals(par)
    #print_ndarr(peds, 'pedestals')

    #rms = det.rms(par)
    #print_ndarr(rms, 'rms')

    #mask = det.mask(par, calib=False, status=True,\
    #       edges=False, central=False, unbond=False, unbondnbrs=False)
    #print_ndarr(mask, 'mask')

    gain = det.gain(par)
    print_ndarr(gain, 'gain')

    offset = det.offset(par)
    print_ndarr(offset, 'offset')

    bkgd = det.bkgd(par)
    print_ndarr(bkgd, 'bkgd')

    datast = det.status_data(par)
    print_ndarr(datast, 'datast')

    status = det.status(par)
    print_ndarr(status, 'status')

    if False:

        statmask = det.status_as_mask(par)
        print_ndarr(statmask, 'statmask')
        print('number of bad status pixels: %d' % (len(statmask[statmask==0])))

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

    i=0
    nda_raw = None
    evt = None
    for i, evt in enumerate(ds.events()):
        t0_sec = time()
        nda_raw = det.raw(evt)
        if nda_raw is not None:
            dt_sec = time()-t0_sec
            print('Detector data found in event %d'\
                  ' consumed time for det.raw(evt) = %7.3f sec' % (i, time()-t0_sec))
            break

    print_ndarr(nda_raw, 'raw data')

    if nda_raw is None:
        print('Detector data IS NOT FOUND in %d events' % i)
        sys.exit('FURTHER TEST IS TERMINATED')

    print('>>> is_jungfrau: %s' % det.is_jungfrau())

    nda_cdata = nda_raw

    pixel_size = det.pixel_size(par)
    print('%s\npixel size: %s' % (80*'_', str(pixel_size)))

    img_arr = nda_cdata
    #img_arr = nda_cdata if nda_cdata is not None else nda_raw
    img = None

    # Image producer is different for 3-d and 2-d arrays
    if len(nda_raw.shape) > 2 or det.dettype == gu.EPIX100A:
        #img = det.image(evt)

        t0_sec = time()
        #img = det.image(evt)
        img = det.image(evt, img_arr)
        print('Consumed time for det.image(evt) = %7.3f sec (for 1st event!)' % (time()-t0_sec))
    else:
        img = img_arr
        img.shape = nda_raw.shape

    print_ndarr(img, 'image (calibrated data or raw)')

    print(80*'_')

    if img is None:
        sys.exit('Image is not available. FURTHER TEST IS TERMINATED')

    import pyimgalgos.GlobalGraphics as gg

    ave, rms = img.mean(), img.std()
    amprange=None
    amprange=(ave-1*rms, ave+2*rms)
    amprange=(57000, 58000)
    gg.plotImageLarge(img, amp_range=amprange, figsize=(11.5,12))

    gg.save('img.png', True)

    hnda = nda_raw

    range_x = (0,(1<<16)-1) # (hnda.min(), hnda.max()) # (0,(2<<16)-1)
    fighi, axhi, hi = gg.hist1d(hnda.flatten(), bins=256, amp_range=range_x,\
                              weights=None, color=None, show_stat=True, log=True, \
                              figsize=(6,5), axwin=(0.15, 0.12, 0.78, 0.80), \
                              title='Image spectrum', xlabel='ADU', ylabel=None, titwin=None)

    gg.show()

    print_ndarr(det.image_xaxis(par), 'image_xaxis')
    print_ndarr(det.image_yaxis(par), 'image_yaxis')


if __name__ == "__main__":
    tname = sys.argv[1] if len(sys.argv)>1 else '1'
    print('%s\nTest %s' % (80*'_', tname))

    if   tname=='1': test_jungfrau_methods('exp=xpptut15:run=410', 'Jungfrau512k')
    elif tname=='2': test_jungfrau_methods('exp=xpptut15:run=430', 'Jungfrau1M')
    elif tname=='3': test_jungfrau_methods('/reg/d/psdm/xpp/xpptut13/scratch/cpo/e968-r0177-s01-c00.xtc', 'DetLab.0:Jungfrau.2') # OR:
    #elif tname=='4': test_jungfrau_methods('/reg/d/psdm/det/detdaq17/xtc/e968-r0177-s01-c00.xtc',         'DetLab.0:Jungfrau.2')
    elif tname=='4': test_jungfrau_methods('/sdf/group/lcls/ds/ana/detector/data_test/xtc/detdaq17-e968-r0127-s00-c00.xtc', 'DetLab.0:Epix10ka2M.0')
    # MISSING DATA
    #elif tname=='3': test_jungfrau_methods('exp=xpptut13:run=177', 'DetLab.0:Jungfrau.2') # OR:
    #elif tname=='1': test_jungfrau_methods('exp=mecls3216:run=2',   'MecTargetChamber.0:Jungfrau.0')
    #elif tname=='2': test_jungfrau_methods('exp=mfxls0816:run=193', 'MfxEndstation.0:Jungfrau.1')
    #elif tname=='3': test_jungfrau_methods('exp=mfxlr1716:run=1',   'MfxEndstation.0:Jungfrau.0')
    else: sys.exit('Not recognized test name: "%s"' % tname)
    sys.exit ('End of %s' % sys.argv[0])

# EOF
