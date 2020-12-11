from time import time
from Detector.GlobalUtils import print_ndarr

#--------------------

def test_01(): 
    print 'get calib constants using Detector'

    t0_sec = time()

    import psana

    ds  = psana.DataSource('exp=xcsx35617:run=394')
    evt = ds.events().next()
    env = ds.env()
    nrun = evt.run()

    par=nrun

    #from Detector.AreaDetector import AreaDetector
    #det = AreaDetector('XcsEndstation.0:Epix10ka2M.0', env, pbits=0)

    det = psana.Detector('XcsEndstation.0:Epix10ka2M.0', env)

    print 'Detector initialized, time = %.3f sec' % (time() - t0_sec)

    t0_sec = time()
    peds = det.pedestals(par)
    print_ndarr(peds, 'pedestals time = %.3f sec' % (time() - t0_sec))

    t0_sec = time()
    gain = det.gain(par)
    print_ndarr(gain, 'pixel_gain time = %.3f sec' % (time() - t0_sec))

    t0_sec = time()
    coords_x = det.coords_x(par)
    print_ndarr(coords_x, 'coords_x time = %.3f sec' % (time() - t0_sec))

#--------------------

def test_02(): 
    print 'get calib constants using PSCalib.NDArrIO load_txt'
    from PSCalib.NDArrIO import load_txt # save_txt

    dir_ctype = '/reg/d/psdm/xcs/xcsx35617/calib/Epix10ka2M::CalibV1/XcsEndstation.0:Epix10ka2M.0/'
    peds = load_txt(dir_ctype + 'pedestals/394-end.data')   
    print_ndarr(peds, 'pedestals')
    gain = load_txt(dir_ctype + 'pixel_gain/394-end.data')   
    print_ndarr(gain, 'pixel_gain')

#--------------------

def test_03(): 
    print 'get calib constants using PSCalib.CalibParsStore'

    from PSCalib.CalibParsStore import cps
    calibdir = '/reg/d/psdm/xcs/xcsx35617/calib'
    group = None
    source = 'XcsEndstation.0:Epix10ka2M.0'
    runnum = 394
    o = cps.Create(calibdir, group, source, runnum, pbits=0) # 0377)
    peds = o.pedestals()
    print_ndarr(peds, 'pedestals')
    gain = o.pixel_gain()
    print_ndarr(gain, 'pixel_gain')


#--------------------
if __name__ == "__main__" :

    import sys
    #import logging
    #logger = logging.getLogger(__name__)
    #logging.basicConfig(format='%(levelname)s:  %(name)s %(message)s', level=logging.DEBUG)

    tname = sys.argv[1] if len(sys.argv)>1 else '1'
    print '%s\nTest %s' % (80*'_', tname)
    if   tname == '1' : test_01()
    elif tname == '2' : test_02()
    elif tname == '3' : test_03()
    else : sys.exit('Test %s is not implemented' % tname)
    sys.exit('End of %s' % sys.argv[0])

#--------------------

