#!/usr/bin/env python
"""
USAGE: <python> Detector/examples/test-issues-2023.py 1
"""
from Detector.UtilsLogging import sys, logging, STR_LEVEL_NAMES, basic_config
logger = logging.getLogger(__name__)
SCRNAME = sys.argv[0].rsplit('/')[-1]


def test_status_extra(shape=(704, 768)):
    import numpy as np
    fname = '/cds/data/psdm/XPP/xpptut15/calib/Epix100a::CalibV1/XcsEndstation.0:Epix100a.1/status_extra/0-end.data'
    a = np.zeros(shape, dtype=np.uint16)
    for i in range(12): a[50*i:50*i+20, :] = i
    np.savetxt(fname, a, fmt='%d')
    print('saved test calibration constants:\n  %s' % fname)
    return a


def test_status_data(shape=(704, 768)):
    import numpy as np
    fname = '/cds/data/psdm/XPP/xpptut15/calib/Epix100a::CalibV1/XcsEndstation.0:Epix100a.1/status_data/0-end.data'
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
    }
    us.save_constants_in_repository(a, **kwa)


def issue_2023_MM_DD():
    """ISSUE:
       REASON:
       FIXED:
    """
    metname = sys._getframe().f_code.co_name
    print('method: %s' % metname)
    print('docstring:', eval(metname).__doc__)


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


USAGE = '\nUsage:'\
      + '\n  python %s <test-name>' % SCRNAME\
      + '\n  where test-name: '\
      + '\n    0 - print usage'\
      + '\n    1 - issue_2023_03_14 - status_as_mask for epix100a'\
      + '\n    2 - issue_2023_03_23 - save_status_array_in_repository'\


TNAME = args.tname  # sys.argv[1] if len(sys.argv)>1 else '0'
if   TNAME in  ('1',): issue_2023_03_14()
elif TNAME in  ('2',): issue_2023_03_23()
else:
    print(USAGE)
    sys.exit('TEST %s IS NOT IMPLEMENTED'%TNAME)

sys.exit('END OF TEST %s'%TNAME)

# EOF
