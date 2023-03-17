#!/usr/bin/env python
"""
USAGE: <python> Detector/examples/test-issues-2022.py 9
"""
#import logging
#logger = logging.getLogger(__name__)
#logging.basicConfig(format='[%(levelname).1s]: %(message)s', level=logging.DEBUG)

import sys
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


def issue_2023_MM_DD():
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
      + '\n    1 - issue_2023_03_14 - status_as_mask for epix100a'\

TNAME = sys.argv[1] if len(sys.argv)>1 else '0'

if   TNAME in  ('1',): issue_2023_03_14()
elif TNAME in  ('2',): issue_2023_03_14()
else:
    print(USAGE)
    exit('TEST %s IS NOT IMPLEMENTED'%TNAME)

exit('END OF TEST %s'%TNAME)

# EOF
