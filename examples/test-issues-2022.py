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

TNAME = sys.argv[1] if len(sys.argv)>1 else '0'

if   TNAME in  ('1',): issue_2022_01_03()
elif TNAME in  ('2',): issue_2022_01_04()
elif TNAME in  ('3',): issue_2022_01_05()

else:
    print(USAGE)
    exit('TEST %s IS NOT IMPLEMENTED'%TNAME)

exit('END OF TEST %s'%TNAME)

# EOF
