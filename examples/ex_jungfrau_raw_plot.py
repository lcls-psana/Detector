#!/usr/bin/env python

import sys
import psana
import numpy as np
from time import time
from Detector.GlobalUtils import print_ndarr
import pyimgalgos.GlobalGraphics as gg

from Detector.UtilsJungfrau import calib_jungfrau

#------------------------------

class Store :
    def __init__(self) : 
        self.hwin_x0y0 = (100,10)
        self.do_save = True
        self.prefix = 'test'
        pass

sp = Store()

#------------------------------

def get_jungfrau_data_object(evt, src) :
    """get jungfrau data object
    """
    o = evt.get(psana.Jungfrau.ElementV1, src)
    if o is not None : return o
    return None

def get_jungfrau_config_object(env, src) :
    cfg = env.configStore()
    o = cfg.get(psana.Jungfrau.ConfigV1, src)
    if o is not None : return o
    return None

#------------------------------
#------------------------------

def h1d(hlst, bins=None, amp_range=None, weights=None, color=None, show_stat=True, log=False,\
        figsize=(6,5), axwin=(0.16, 0.12, 0.78, 0.80), title='Title', xlabel='x', ylabel='y', titwin=None, fnm='fnm.png') :
    """Wrapper for hist1d, move, and save methods, using common store parameters
    """
    fig, axhi, hi = gg.hist1d(np.array(hlst), bins, amp_range, weights, color, show_stat,\
                           log, figsize, axwin, title, xlabel, ylabel, titwin)

    gg.move(sp.hwin_x0y0[0], sp.hwin_x0y0[1])
    gg.save('%s-%s' % (sp.prefix, fnm), sp.do_save)
    return fig, axhi, hi

#------------------------------

def test_jungfrau(tname) :

    """The data is in cxi11216.  There is one tile.  I appear to be using 
       runs 9, 11, and 12 as pedestals for gain 0, 1, 2.  Runs 18-22 have some data,
       which is highly non-optimal; we have better stuff but in a painful format.
    """
    #/reg/d/psdm/cxi/cxi11216/xtc/
    #/reg/d/psdm/cxi/cxi11216/calib/Jungfrau::CalibV1/CxiEndstation.0:Jungfrau.0/

    exp = 'cxi11216'
    nrun = 9 # 9 11 12
    dsname = 'exp=%s:run=%d' % (exp, nrun) # (1, 512, 1024)
    #sp.prefix = 'fig-%s-r%04d-%s' % (exp, nrun, tname) 
    sp.prefix = 'fig-%s-r%04d-%s-cm' % (exp, nrun, tname) 
    #dsname = 'exp=cxi11216:run=40' # (1, 512, 1024)
    #dsname = '/reg/g/psdm/detector/data_test/types/0024-CxiEndstation.0-Jungfrau.0.xtc'
    src = 'CxiEndstation.0:Jungfrau.0'

    print 'Example for\n  dataset: %s\n  source : %s' % (dsname, src)
    #psana.setOption('psana.calib-dir', './calib')
    #psana.setOption('psana.calib-dir', './empty/calib')

    ds  = psana.DataSource(dsname)
    env = ds.env()

    source = psana.Source(src)
    #do = get_jungfrau_data_object(evt, src) # cfg.get(psana.Jungfrau.ConfigV1, src)
    co = get_jungfrau_config_object(env, source)
    gm = co.gainMode()

    print '  env.calibDir: %s' % env.calibDir()

    from Detector.AreaDetector import AreaDetector

    par = nrun # evt or nrun
    det = AreaDetector(src, env, pbits=0)

    t0_sec = time()
    i=0
    evt = None
    nda = None

    #nda = det.raw(evt)
    #print_ndarr(nda, 'nda')
    cmp = det.common_mode(9)
    print_ndarr(cmp, 'common_mode')

    if nda is None :
        for i, evt in enumerate(ds.events()) :
            nda = det.raw(evt) if tname=='0' else\
                  det.calib(evt, cmpars=(7,1,100)) # cmpars=(7,0,100)
                  #calib_jungfrau(det, evt, source)

            print 'Event %d' % i
            ###===============
            if i<10 : continue
            ###===============
            if nda is not None :
                print 'Detector data found in event %d' % i
                break

    #for key in evt.keys() : print key

    print_ndarr(nda, 'raw data')

    if nda is None :
        print 'Detector data IS NOT FOUND in %d events' % i
        sys.exit('FURTHER TEST IS TERMINATED')

    img = nda
    img.shape = (512, 1024)
    img = img[:,:512]

    print_ndarr(img, 'img')
    print 80*'_'

    if img is None :
        print 'Image is not available'
        sys.exit('FURTHER TEST IS TERMINATED')

    import pyimgalgos.GlobalGraphics as gg

    ave, rms = img.mean(), img.std()
    gg.plotImageLarge(img, amp_range=(ave-1*rms, ave+2*rms))
    gg.save(fname='%s-%s'%(sp.prefix, 'img.png'), do_save=True, pbits=1)

    if True :
    #---------
        h1d(img.flatten(), bins=200, amp_range=(ave-4*rms,img.max()), \
           title ='Image spectrum', xlabel='Intensity, ADU', ylabel='Pixels',\
           fnm='his.png')
    #---------

    gg.show()

    print '1<<14 = ', 1<<14
    print '2<<14 = ', 2<<14
    print '3<<14 = ', 3<<14
    print 'gm.name', gm.name
    print 'gm.names:\n', gm.names
    for k,v in gm.names.iteritems() : print k,v 

#------------------------------
#------------------------------
#------------------------------
#------------------------------
#------------------------------

if __name__ == "__main__" :
    import sys; global sys
    tname = sys.argv[1] if len(sys.argv) > 1 else '0'
    print 50*'_', '\nTest %s:' % tname
    if   tname == '0' : test_jungfrau(tname)
    elif tname == '1' : test_jungfrau(tname)
    else : print 'Test %s is not implemented' % tname
    sys.exit('End of test %s' % tname)

#------------------------------
