#!/usr/bin/env python

import sys
from time import time
import psana
from Detector.GlobalUtils import print_ndarr
import PSCalib.GlobalUtils as gu

#------------------------------

def dsname_source(tname) :
    if   tname=='1': return 'exp=mecls3216:run=2',   'MecTargetChamber.0:Jungfrau.0' # 170505-149520170815-3d00b0_170505-149520170815-3d00f7 -> M068, M088
    elif tname=='2': return 'exp=mfxls0816:run=193', 'MfxEndstation.0:Jungfrau.1' # 171113-154920171025-3d00fb                            -> M044
    elif tname=='3': return 'exp=mfxlr1716:run=1',   'MfxEndstation.0:Jungfrau.0' # 171113-154920171025-3d00b0_171113-154920171025-3d00f7
    else :
        print 'Example for\n dataset: %s\n source : %s \nis not implemented' % (dsname, src)
        sys.exit(0)

    
def test_jungfrau_methods(tname) :

    dsname, src = dsname_source(tname)

    psana.setOption('psana.calib-dir', './calib')
    ds  = psana.DataSource(dsname)
    evt = ds.events().next()
    env = ds.env()
    nrun = evt.run()
    
    print 'experiment %s' % env.experiment()
    print 'Run number %d' % nrun
    print 'dataset exp=%s:run=%d' % (env.experiment(),nrun) 
    print 'calibDir:', env.calibDir()
    
    for key in evt.keys() : print key

    ##-----------------------------
    par = nrun # evt or nrun
    par = evt
    det = psana.Detector(src, env)
    
    ins = det.instrument()
    print 80*'_', '\nInstrument: ', ins
    print 'src:', src    

    det.set_print_bits(0)

    #det.set_print_bits(511)
    #det.set_def_value(-5.)
    #det.set_mode(1)
    #det.set_do_offset(True) # works for ex. Opal1000
    #det.print_attributes()
    print 'det.source:', det.source
    
    shape_nda = det.shape(par)
    print_ndarr(shape_nda, 'shape of ndarray')
    
    print 'size of ndarray: %d' % det.size(par)
    print 'ndim of ndarray: %d' % det.ndim(par)
    
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
    
    ######################
    sys.exit ('TEST EXIT')
    ######################

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
   
    i=0
    nda_raw = None
    evt = None
    for i, evt in enumerate(ds.events()) :
        t0_sec = time()
        nda_raw = det.raw(evt)
        if nda_raw is not None :
            dt_sec = time()-t0_sec
            print 'Detector data found in event %d'\
                  ' consumed time for det.raw(evt) = %7.3f sec' % (i, time()-t0_sec)
            break
    
    print_ndarr(nda_raw, 'raw data')
        
    if nda_raw is None :
        print 'Detector data IS NOT FOUND in %d events' % i
        sys.exit('FURTHER TEST IS TERMINATED')

    nda_cdata = nda_raw
        
    ##-----------------------------
    #sys.exit('TEST EXIT')
    ##-----------------------------

    #if peds is not None and nda_raw is not None : peds.shape = nda_raw.shape 
    #data_sub_peds = nda_raw - peds if peds is not None else nda_raw
    #print_ndarr(data_sub_peds, 'data - peds')
    
#    nda_cdata = det.calib(evt)
#    print_ndarr(nda_cdata, 'calibrated data')
    
#    mask_geo = det.mask_geo(par, mbits=3, width=1)
#    print_ndarr(mask_geo, 'mask_geo')

#    nda_cdata*=mask_geo
    
    #mask_geo.shape = (32,185,388)
    #print mask_geo
    
    pixel_size = det.pixel_size(par)
    print '%s\npixel size: %s' % (80*'_', str(pixel_size))
    
#    ipx, ipy = det.point_indexes(par) # , pxy_um=(0,0)) 
#    print 'Detector origin indexes: ix, iy:', ipx, ipy
    ##-----------------------------
    
    #img_arr = data_sub_peds
    img_arr = nda_cdata
    #img_arr = nda_cdata if nda_cdata is not None else nda_raw
    img = None
    
    # Image producer is different for 3-d and 2-d arrays 
    if len(nda_raw.shape) > 2 or det.dettype == gu.EPIX100A :
        #img = det.image(evt)
        
        t0_sec = time()
        #img = det.image(evt)
        img = det.image(evt, img_arr)
        print 'Consumed time for det.image(evt) = %7.3f sec (for 1st event!)' % (time()-t0_sec)
    else :
        img = img_arr
        img.shape = nda_raw.shape
    
    print_ndarr(img, 'image (calibrated data or raw)')
    
    print 80*'_'

    ##-----------------------------
    
    if img is None :
        sys.exit('Image is not available. FURTHER TEST IS TERMINATED')
    
    import pyimgalgos.GlobalGraphics as gg
    
    ave, rms = img.mean(), img.std()
    gg.plotImageLarge(img, amp_range=None, figsize=(13,12)) # amp_range=(ave-1*rms, ave+2*rms))
    
    ##-----------------------------
    hnda = nda_raw 

    range_x = (0,(1<<16)-1) # (hnda.min(), hnda.max()) # (0,(2<<16)-1)
    fighi, axhi, hi = gg.hist1d(hnda.flatten(), bins=256, amp_range=range_x,\
                              weights=None, color=None, show_stat=True, log=True, \
                              figsize=(6,5), axwin=(0.15, 0.12, 0.78, 0.80), \
                              title='Image spectrum', xlabel='ADU', ylabel=None, titwin=None) 

    gg.show()

    ##-----------------------------
    
    print_ndarr(det.image_xaxis(par), 'image_xaxis')
    print_ndarr(det.image_yaxis(par), 'image_yaxis')
    
    ##-----------------------------

#------------------------------

if __name__ == "__main__" :
    tname = sys.argv[1] if len(sys.argv)>1 else '1'
    print '%s\nTest %s' % (80*'_', tname)
    if tname in ('1', '2', '3') : test_jungfrau_methods(tname)
    else : sys.exit ('Not recognized test name: "%s"' % tname)
    sys.exit ('End of %s' % sys.argv[0])

#------------------------------
