#!/usr/bin/env python

"""Intended to hack epix10ka2m calibration constants in DIR_REPO.
   Replaces panel 0-s by median for list of ctypes.
   Created on 2020-08-20 by Mikhail Dubrovin
"""

import os
import sys
import numpy as np

SCRNAME = os.path.basename(sys.argv[0])

import logging
logging.basicConfig(format='[%(levelname).1s] L%(lineno)04d: %(message)s', level=logging.DEBUG)

logger = logging.getLogger(__name__)
logger.info('start %s' % SCRNAME)

from Detector.GlobalUtils import info_ndarr, print_ndarr


def replace_zeros(ifname, cfname, ofname):

    # save original file *.dat as *.orig if it does not exist
    if os.path.exists(cfname):
        logger.info('exists: %s' % cfname)
    else:
        cmd = 'cp %s %s' % (ifname,cfname)
        logger.info(cmd)
        os.system(cmd)

    # load constants from original file
    logger.info('    load file: ' + cfname)
    arr = np.loadtxt(cfname)
    logger.info(info_ndarr(arr,'    arr'))

    # evaluate median value for selected pixels
    med = np.median(arr[arr>0])
    logger.info('    median(arr[arr>0]): %.3f' % med)

    inds = arr==0
    nselpix = np.sum(inds)
    logger.info('    number of selected pixels in array %d' % nselpix)
    if nselpix == 0:
        logger.info('    nothing to correct')
        return

    # substitute median value for selected pixels
    logger.info(info_ndarr(arr[inds],'    non-corrected arr[inds]'))
    arr[inds] = med
    logger.info(info_ndarr(arr[inds],'    corrected     arr[inds]'))

    # save calibration file
    np.savetxt(ofname,arr, fmt='%.3f')
    logger.info('    saved: %s'% ofname)


CTYPES=(\
  ('gain',      'gainci_AML-M'),\
  ('gain',      'gainci_AML-L'),\
  ('gain',      'gainci_AHL-H'),\
  ('gain',      'gainci_AHL-L'),\
  ('offset',    'offset_AML-M'),\
  ('offset',    'offset_AML-L'),\
  ('offset',    'offset_AHL-H'),\
  ('offset',    'offset_AHL-L'),\
  ('pedestals', 'pedestals_FH'),\
  ('pedestals', 'pedestals_FM'),\
  ('pedestals', 'pedestals_FL'),\
  ('pedestals', 'pedestals_AML-M'),\
  ('pedestals', 'pedestals_AML-L'),\
  ('pedestals', 'pedestals_AHL-H'),\
  ('pedestals', 'pedestals_AHL-L'),\
)


def do_work():

    #work/0000000001-0173621761-3221225494-1014046789-0019435010-0000000000-0000000000/gain/epix10ka_0034_20200819112113_xcsc00118_r0095_gainci_AML-L.dat
    #work/0000000001-0173621761-3221225494-1014046789-0019435010-0000000000-0000000000/offset/epix10ka_0034_20200819112113_xcsc00118_r0095_offset_AHL-H.dat
    #work/0000000001-0173621761-3221225494-1014046789-0019435010-0000000000-0000000000/pedestals/epix10ka_0034_20200819112113_xcsc00118_r0095_pedestals_FM.dat
    #work/0000000001-0173621761-3221225494-1014046789-0019435010-0000000000-0000000000/pedestals/epix10ka_0034_20200819112113_xcsc00118_r0095_pedestals_AML-L.dat
    #panels/0000000001-0174306561-0234881046-0630252037-0016939401-0000000000-0000000000/pedestals/epix10ka_0038_20200819112113_xcsc00118_r0095_pedestals_AML-L.dat
    #DIR_REPO = '/reg/g/psdm/detector/gains/epix10k/panels'
    DIR_REPO = 'panels'
    #DIR_REPO = 'work'

    PANEL_ID = '0000000001-0173621761-3221225494-1014046789-0019435010-0000000000-0000000000' # epix10ka2m.0 panel 7
    FNAME_PTRN = 'epix10ka_0034_20200819112113_xcsc00118_r0095_%s.dat'

    #PANEL_ID = '0000000001-0174306561-0234881046-0630252037-0016939401-0000000000-0000000000' # epix10ka2m.0 panel 12
    #FNAME_PTRN = 'epix10ka_0038_20200819112113_xcsc00118_r0095_%s.dat'
    for ctype,suffix in CTYPES:

        logger.info('%s\nreplace 0-s by median for ctype %s' % (50*'_', suffix))

        dname = '%s/%s/%s' % (DIR_REPO, PANEL_ID, ctype)
        fname = FNAME_PTRN % suffix
        ifname = '%s/%s' % (dname, fname)
        cfname = ifname.rstrip('.dat') + '.orig'
        ofname = ifname
        replace_zeros(ifname, cfname, ofname)


if __name__ == "__main__":
    do_work()
    sys.exit('EXIT %s' % SCRNAME)

# EOF
