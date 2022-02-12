#!/usr/bin/env python
#import logging
#logger = logging.getLogger(__name__)
#logging.basicConfig(format='[%(levelname).1s]: %(message)s', level=logging.DEBUG)

import sys
SCRNAME = sys.argv[0].rsplit('/')[-1]


def issue_2022_01_03():
    """ISSUE: Roberto Alvarez <rcalvar2@asu.edu>
       Mon 1/3/2022 11:45 AM
       Thank you for all the assistance you have provided us, we really appreciate it.
       I have not been able to retrieve the geometry in PSF format with the new interface.
       What I do is:...
       REASON: in py3 division is not int...
       FIXED in ana-4.0.35: V02-00-23 - src/UtilsPSF.py - fix py3 issue - use int for devision
    """
    import psana
    import PSCalib.UtilsPSF as ups
    runnum = 312
    #ds = psana.DataSource(f'exp=mfxlv1218:run={runnum}') # py3
    ds = psana.DataSource('exp=mfxlv1218:run=%d'%runnum)
    det = psana.Detector('epix10k2M')
    geom = det.geometry(runnum)
    psf, sego, geo = ups.psf_from_geo(geom, cframe=1)  # this line fails
    print('psf', psf)


def issue_2022_01_04():
    """ISSUE: inducted by issue_2022_01_03 - psf from GeometryAccess
       REASON: because users use Detector object
       FIXED: in GeometryAccess added methods psf() and data_psf(data)
    """
    import psana
    runnum = 312
    ds = psana.DataSource('exp=mfxlv1218:run=%d'%runnum)
    det = psana.Detector('epix10k2M')
    geom = det.geometry(runnum)
    psf = geom.psf(cframe=1)
    print('psf:\n%s' % geom.info_psf())

    xarr, yarr, zarr = geom.pixel_coords_psf(cframe=1)
    from Detector.GlobalUtils import info_ndarr
    print(info_ndarr(xarr,'geom.pixel_coords_psf xarr:'))
    print(info_ndarr(yarr,'geom.pixel_coords_psf yarr:'))
    print(info_ndarr(zarr,'geom.pixel_coords_psf zarr:'))

def issue_2022_01_05():
    """ISSUE: the same as issue_2022_01_04 - psf from Detector
       REASON: because users use Detector object
       FIXED: in AreaDetectr added methods psf(par, cframe=1) and data_psf(par, data)
    """
    import psana
    runnum = 312
    ds = psana.DataSource('exp=mfxlv1218:run=%d'%runnum)
    det = psana.Detector('epix10k2M')
    psf = det.psf(runnum, cframe=1)

    import PSCalib.UtilsPSF as ups
    print('psf:\n%s' % ups.info_psf(psf))

    from Detector.GlobalUtils import np, info_ndarr
    a = np.ones((16, 352, 384))
    print(info_ndarr(a,'psana shaped data'))
    dpsf = det.data_psf(runnum, a)
    print(info_ndarr(dpsf,'PSF shaped data'))

    xarr, yarr, zarr = det.pixel_coords_psf(runnum, cframe=1)
    print(info_ndarr(xarr,'geom.pixel_coords_psf xarr:'))
    print(info_ndarr(yarr,'geom.pixel_coords_psf yarr:'))
    print(info_ndarr(zarr,'geom.pixel_coords_psf zarr:'))


def issue_2022_02_09():
    """ISSUE: Philip - jungfrau may have not switching pixels
       REASON: ???
       FIXED:
    """
    from time import time
    import numpy as np
    from psana import DataSource, Detector
    import PSCalib.GlobalUtils as gu
    from Detector.GlobalUtils import info_ndarr

    #exp, run = 'cxilu7619', 168
    exp, run = 'cxilv1019', 142
    ds = DataSource('exp=%s:run=%d:smd' %(exp, run))
    jf= Detector('jungfrau4M', ds.env())

    g0cut = 1<<14
    g1cut = 2<<14
    g2cut = 3<<14
    modes = ['Normal-00', 'Med-01', 'Low-11', 'UNKNOWN-10']

    bad_tot = None
    for istep, step in enumerate(ds.steps()):
      print '%s mode %s' %(20*'==', modes[istep])
      #evt = ds.events().next()
      for ievt, evt in enumerate(step.events()):

        if ievt % 20 != 0: continue
        raw = jf.raw(evt)
        t0_sec = time()
        #fg0 = raw<g0cut
        #fg1 = (raw>=g0cut) & (raw<g1cut)
        #fg2 = raw>=g2cut
        #bad = (fg1+fg2, fg0+fg2, fg0+fg1)[istep]

        gbits = raw>>14 # 00/01/11 - gain bits for mode 0,1,2
        fg0, fg1, fg2, fgx = gbits==0, gbits==1, gbits==3, gbits==2

        bad = (np.logical_not(fg0),\
               np.logical_not(fg1),\
               np.logical_not(fg2))[istep]

        dt_sec = time()-t0_sec

        sums = [fg0.sum(), fg1.sum(), fg2.sum(), fgx.sum()]
        s = ' '.join(['%s:%d' % (modes[i], sums[i]) for i in range(4)])
        print('Ev: %4d found pixels %s gain definition time: %.6f sec' % (ievt, s, dt_sec))

        if bad_tot is None: bad_tot = bad
        else: np.logical_or(bad_tot, bad, bad_tot)

        #print(info_ndarr(raw,     '  raw'))
        #print(info_ndarr(fg0,     '  fg0'))
        #print(info_ndarr(bad,     '  bad'))
        #print(info_ndarr(bad_tot, '  bad_tot'))

    print('Total number of bad pixels %d' % bad_tot.sum())

    zeros = np.zeros_like(bad_tot, dtype=np.uint16)

    mask = np.select((bad_tot,), (zeros,), default=1)
    fname = '%s_r%d_bad_tot.npy' %(exp, run)
    np.save(fname, mask+1)
    print('saved file: %s' % fname)


def issue_2021_MM_DD():
    """ISSUE:
       REASON:
       FIXED:
    """
    metname = sys._getframe().f_code.co_name
    print('method: %s' % metname)
    print('docstring:', eval(metname).__doc__)


USAGE = '\nUsage:'\
      + '\n  python %s <test-name>' % SCRNAME\
      + '\n  where test-name: '\
      + '\n    0 - print usage'\
      + '\n    1 - issue_2022_01_03 - Roberto Alvarez - issue with psana-to-psf converter in py3'\
      + '\n    2 - issue_2022_01_04 - psf() from GeometryAccess'\
      + '\n    3 - issue_2022_01_05 - psf() from Detector -> AreaDetector -> GeometryAccess'\
      + '\n    4 - issue_2022_02_09 - Philip - catch not switching pixels in jungfrau'\

TNAME = sys.argv[1] if len(sys.argv)>1 else '0'

if   TNAME in  ('1',): issue_2022_01_03()
elif TNAME in  ('2',): issue_2022_01_04()
elif TNAME in  ('3',): issue_2022_01_05()
elif TNAME in  ('4',): issue_2022_02_09()

else:
    print(USAGE)
    exit('TEST %s IS NOT IMPLEMENTED'%TNAME)

exit('END OF TEST %s'%TNAME)

# EOF
