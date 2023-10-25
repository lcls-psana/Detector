#!/usr/bin/env python
"""
USAGE: <python> Detector/examples/test-issues-2023.py 1
"""
from Detector.UtilsLogging import sys, logging, STR_LEVEL_NAMES, basic_config
logger = logging.getLogger(__name__)
SCRNAME = sys.argv[0].rsplit('/')[-1]


def test_dsname_detname_shape(kw):
    """
    datinfo -e xpptut15 -r 380 -d CxiDs1.0:Cspad.0
    """
    return {
       'rayonix'       : ('exp=xpptut15:run=240', 'XppEndstation.0:Rayonix.0', (1920, 1920)),
       'cspad2x2'      : ('exp=xpptut15:run=460', 'XcsEndstation.0:Cspad2x2.3', (2, 185, 388)),
       'cspad2x2.3'    : ('exp=xpptut15:run=260', 'MecTargetChamber.0:Cspad2x2.3', (2, 185, 388)),
       'cspad'         : ('exp=xpptut15:run=380', 'CxiDs1.0:Cspad.0', (32, 185, 388)),
       'cspad2'        : ('exp=xpptut15:run=380', 'CxiDs2.0:Cspad.0', (32, 185, 388)),
       'cspad_xpp'     : ('exp=xpptut15:run=320', 'XppGon.0:Cspad.0', (32, 185, 388)),
       'opal1000'      : ('exp=xpptut15:run=310', 'XrayTransportDiagnostic.0:Opal1000.0', (1024, 1024)),
       'pnccd'         : ('exp=xpptut15:run=450', 'Camp.0:pnCCD.1', (4, 512, 512)),
       'epix100a'      : ('exp=xpptut15:run=260', 'XcsEndstation.0:Epix100a.1', (704, 768)),
       'epix_alc3'     : ('exp=xpptut15:run=630', 'epix_alc3', (704, 768)),
       'epix10ka2m'    : ('exp=xpptut15:run=540', 'epix10ka2m', (16, 352, 384)),
       'epix10ka2m.0'  : ('exp=xpptut15:run=570', 'MfxEndstation.0:Epix10ka2M.0', (16, 352, 384)),
       'epix10kaquad'  : ('exp=xpptut15:run=590', 'Epix10kaQuad0', (4, 352, 384)),
       'epix10kaquad.1': ('exp=xpptut15:run=590', 'Epix10kaQuad1', (4, 352, 384)),
       'epix10kaquad.2': ('exp=xpptut15:run=590', 'Epix10kaQuad2', (4, 352, 384)),
       'epix10kaquad.3': ('exp=xpptut15:run=590', 'Epix10kaQuad3', (4, 352, 384)),
       'jungfrau512k'  : ('exp=xpptut15:run=410', 'Jungfrau512k', (1, 512, 1024)),
       'jungfrau1m'    : ('exp=xpptut15:run=430', 'Jungfrau1M', (2, 512, 1024)),
       'jungfrau4m'    : ('exp=xpptut15:run=580', 'jungfrau4M', (8, 512, 1024)),
       'jungfrau4m.2'  : ('exp=xpptut15:run=530', 'DetLab.0:Jungfrau.2', (8, 512, 1024)),
    }[kw]


FNAME_STATUS = '/cds/data/psdm/XPP/xpptut15/calib/Epix100a::CalibV1/XcsEndstation.0:Epix100a.1/status_extra/0-end.data'


def test_status_extra(shape=(704, 768)):
    import numpy as np
    fname = FNAME_STATUS
    a = np.zeros(shape, dtype=np.uint16)
    for i in range(12): a[50*i:50*i+20, :] = i
    np.savetxt(fname, a, fmt='%d')
    print('saved test calibration constants:\n  %s' % fname)
    return a


def test_status_data(shape=(704, 768)):
    import numpy as np
    fname = FNAME_STATUS
    a = np.zeros(shape, dtype=np.uint16)
    for i in range(12): a[:, 50*i:50*i+20] = i
    np.savetxt(fname, a, fmt='%d')
    print('saved test calibration constants:\n  %s' % fname)
    return a


def test_status_array(shape=(704, 768)):
    import numpy as np
    a = np.zeros(shape, dtype=np.uint16)
    for i in range(12): a[50*i:50*i+20, :] = i
    return a


def issue_2023_03_14():
    """status_as_mask for epix100a
       datinfo -e xpptut15 -r 260 -d XcsEndstation.0:Epix100a.1
    """
    import Detector.GlobalUtils as gu
    import pyimgalgos.GlobalGraphics as gg
    import psana

    runnum = 260

    ds = psana.DataSource('exp=xpptut15:run=%d' % runnum)
    det = psana.Detector('XcsEndstation.0:Epix100a.1')
    print('calibDir:', ds.env().calibDir())

    #Deploy test constants to the calib directory
    arr1 = test_status_extra()
    arr2 = test_status_data()

    print('test access')
    status = det.status(runnum)
    status_extra = det.status_extra(runnum)
    status_data = det.status_data(runnum)
    print(gu.info_ndarr(status,       'pixel_status:', last=10))
    print(gu.info_ndarr(status_extra, 'status_extra:', last=10))
    print(gu.info_ndarr(status_data,  'status_data: ', last=10))

    mask = det.status_as_mask(runnum, mstcode=0xffff, mstextra=0xffff, mstdata=0xffff)

    gg.plotImageLarge(status, amp_range=(-1, 4), title='pixel_status')
    gg.plotImageLarge(status_extra, amp_range=(-1, 12), title='status_extra')
    gg.plotImageLarge(status_data, amp_range=(-1, 12), title='status_data')
    gg.plotImageLarge(mask, amp_range=(-1, 4), title='status_as_mask')
    gg.show()


def issue_2023_03_23():
    """test save_status_array_in_repository
       datinfo -e xpptut15 -r 260 -d XcsEndstation.0:Epix100a.1
    """
    import numpy as np
    a = np.zeros((704, 768), dtype=np.uint64)
    a[200:400, 300:500] = 1

    import Detector.GlobalUtils as gu
    print(gu.info_ndarr(a, 'test status array:', last=10))

    import Detector.UtilsRawPixelStatus as us
    #kwa = {'dsname':'exp=xpplw3319:run=293', 'detname':'XppGon.0:Epix100a.3', 'ctype':'status_user'}
    kwa = {\
      'dsname':'exp=xpptut15:run=260',\
      'detname':'XcsEndstation.0:Epix100a.1',\
      'ctype':'status_user',\
      'gmodes':None,\
    }
    us.save_constants_in_repository(a, **kwa)


def issue_2023_03_28():
    """The same as issue_2023_03_23, but for epix10kaquad

    from psana import Detector, DataSource
    ds = DataSource('exp=xpptut15:run=590')
    det = Detector('Epix10kaQuad0')

    import Detector.UtilsDeployConstants as udc

    udc.id_det(det, ds.env())
    """

    # 'exp=xpptut15:run=590', 'Epix10kaQuad0', (4, 352, 384)
    dsname, detname, shape_raw = test_dsname_detname_shape('epix10kaquad')
    shape = (7,) + tuple(shape_raw)

    import numpy as np
    a = np.zeros(shape, dtype=np.uint64)
    a[:, :, 150:200, 200:250] = 1

    import Detector.GlobalUtils as gu
    print(gu.info_ndarr(a, 'test status array:', last=10))

    import Detector.UtilsRawPixelStatus as us
    kwa = {\
      'dsname' : dsname,\
      'detname': detname,\
      'ctype'  : 'status_user',\
       'gmodes' : ('FH', 'FM', 'FL', 'AHL-H','AML-H', 'AHL-L','AML-L'),\
    }
    us.save_constants_in_repository(a, **kwa)


def issue_2023_10_12():
    """access to test data from file for epix100a
    #event_keys -d /sdf/group/lcls/ds/ana/detector/data_test/xtc/mecdaq115-e993-r0174-s00-c00.xtc -m2
    event_keys -d /sdf/group/lcls/ds/ana/detector/data_test/xtc/xppn4116-e851-r0137-s00-c00.xtc -n 10 -s -1 -m 1 -p EventKey
    """
    from psana import Detector, DataSource
    ds = DataSource('/sdf/group/lcls/ds/ana/detector/data_test/xtc/mecdaq115-e993-r0174-s00-c00.xtc')
    #ds = DataSource('/sdf/group/lcls/ds/ana/detector/data_test/xtc/xppn4116-e851-r0137-s00-c00.xtc')
    #det = Detector('XppGon.0:Epix100a.1')
    for i, evt in enumerate(ds.events()):
        if i>0: break
        print('dir(evt)', dir(evt))
        print('\nXXX evt.keys():')
        for k in evt.keys():
           print(k)
    env = ds.env()
    print('dir(env)', dir(env))
    print('env.experiment() "%s"' % str(env.experiment()))


def issue_2023_10_18():
    """ISSUE: UXI was not seen in data exp=xcsl1004621:run=2
       REASON: Dan've made changes in daq not available in ana-4.0.53-py3
       FIXED: fixed in ana-4.0.54-py3
    """
    import Detector.GlobalUtils as gu
    import psana
    ds = psana.DataSource('exp=xcsl1004621:run=2')
    det = psana.Detector('XcsEndstation.0:Uxi.1')
    for i, evt in enumerate(ds.events()):
        if i < 1:
          print('\nEv %03d keys():' % i)
          for k in evt.keys():
            s = str(k)
            print(s)
            #if 'Uxi' in s: break
        print(gu.info_ndarr(det.raw(evt), 'Ev %03d det.raw' % i, last=10))

    print('\n\nds.env().configStore().keys():')
    for k in ds.env().configStore().keys():
        print(k)


def issue_2023_MM_DD():
    """ISSUE:
       REASON:
       FIXED:
    """
    metname = sys._getframe().f_code.co_name
    print('method: %s' % metname)
    print('docstring:', eval(metname).__doc__)


USAGE = '\n  python %s <test-name>' % SCRNAME\
      + '\n  where test-name: '\
      + '\n    0 - print usage'\
      + '\n    1 - issue_2023_03_14 - status_as_mask for epix100a'\
      + '\n    2 - issue_2023_03_23 - save_constants_in_repository for epix100a'\
      + '\n    3 - issue_2023_03_28 - save_constants_in_repository for epix10kaquad'\
      + '\n    4 - issue_2023_10_12 - access to test data from file for epix100a'\
      + '\n    5 - issue_2023_10_18 - philip issue with uxi'\


def argument_parser():
    from argparse import ArgumentParser
    d_tname = '0'
    d_dsname = 'exp=xpplw3319:run=293'  # None
    d_detname = 'epix_alc3'  # None
    d_logmode = 'INFO'
    h_tname  = 'test name, usually numeric number, default = %s' % d_tname
    h_dsname  = 'dataset name, default = %s' % d_dsname
    h_detname  = 'input ndarray source name, default = %s' % d_detname
    h_logmode = 'logging mode, one of %s, default = %s' % (STR_LEVEL_NAMES, d_logmode)
    parser = ArgumentParser(description='%s is a bunch of tests for annual issues' % SCRNAME, usage=USAGE)
    parser.add_argument('tname',            default=d_tname,    type=str,   help=h_tname)
    parser.add_argument('-d', '--dsname',   default=d_dsname,   type=str,   help=h_dsname)
    parser.add_argument('-s', '--detname',  default=d_detname,  type=str,   help=h_detname)
    parser.add_argument('-L', '--logmode',  default=d_logmode,  type=str,   help=h_logmode)
    return parser


parser = argument_parser()
args = parser.parse_args()
basic_config(format='[%(levelname).1s] L%(lineno)04d: %(filename)s %(message)s', int_loglevel=None, str_loglevel=args.logmode)


TNAME = args.tname  # sys.argv[1] if len(sys.argv)>1 else '0'
if   TNAME in  ('1',): issue_2023_03_14()
elif TNAME in  ('2',): issue_2023_03_23()
elif TNAME in  ('3',): issue_2023_03_28()
elif TNAME in  ('4',): issue_2023_10_12()
elif TNAME in  ('5',): issue_2023_10_18()
else:
    print(USAGE)
    sys.exit('TEST %s IS NOT IMPLEMENTED'%TNAME)

sys.exit('END OF TEST %s'%TNAME)

# EOF
