#!/usr/bin/env python

"""Splits epix10ka2m calibration constants (7,16,352,384)
   into 7 per gain mode imaging arrays of shape (16,352,384).
   Created on 2020-08-21 by Mikhail Dubrovin
"""
import os
import sys
import numpy as np

SCRNAME = os.path.basename(sys.argv[0])

import logging
#DICT_NAME_TO_LEVEL = {k:v for k,v in logging._levelNames.iteritems() if isinstance(k, str)}
logging.basicConfig(format='[%(levelname).1s] L%(lineno)04d: %(message)s', level=logging.DEBUG)

logger = logging.getLogger(__name__)
logger.info('start %s' % SCRNAME)

from PSCalib.NDArrIO import save_txt, load_txt
from Detector.GlobalUtils import print_ndarr, info_ndarr
from Detector.UtilsEpix10ka import GAIN_MODES

cfname = 'calib/Epix10ka2M::CalibV1/XcsEndstation.0:Epix10ka2M.0/pedestals/95-end.data'
ofprefix = './xcsc00118-0095-epix10ka2m.0-pedestals'

#shape = (7,16,352,384)
#nda_calib = np.loadtxt(cfname)
#nda_calib.shape = shape

nda_calib = load_txt(cfname)
logger.info(info_ndarr(nda_calib,'nda_calib'))

for igm, gmname in enumerate(GAIN_MODES):
    nda = nda_calib[igm]
    ofname = '%s-%s.txt' % (ofprefix, gmname)
    logger.info(info_ndarr(nda, ofname))

    #cmd = 'plims 
    #os.system(cmd)

    save_txt(ofname, arr=nda, cmts=(), fmt='%.1f', verbos=True, addmetad=True)
