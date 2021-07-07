#!/usr/bin/env python
# README-2021-07-01-philip-epix10ka-gains-for-mfxlx4219
#datinfo -e mfxlx4219 -r 356 -d MfxEndstation.0:Epix10ka2M.0
#epix10ka_id exp=mfxlx4219:run=356 MfxEndstation.0:Epix10ka2M.0

from Detector.UtilsEpix10kaCalib import sys, np, info_ndarr, save_epix10ka_ctype_in_repo

import logging
logger = logging.getLogger(__name__)
logging.basicConfig(format='[%(levelname).1s] L%(lineno)04d: %(message)s', level=logging.INFO)

#nda = np.load('/reg/d/psdm/mfx/mfxlx4219/results/ePix10k2m/hockey/FL/hockeyOffsetInAdu.npy')
nda = np.load('/reg/g/psdm/detector/data_test/npy/offsetph-mfxlx4219-r0356-epix10ka2m-16-352-384.npy')
logging.info(info_ndarr(nda, 'nda'))

exp = 'mfxlx4219'
detname = 'MfxEndstation.0:Epix10ka2M.0'
runnum = 356
rundepl = 111
tstamp = '20210516000000'
ctype, gmode, fmt = 'offsetph', 'AML', '%.6f'
#ctype, gmode, fmt = 'pedestals', 'FL', '%.3f'
dirrepo = './panels'

save_epix10ka_ctype_in_repo(nda, exp, runnum, detname, gmode, ctype=ctype, dirrepo=dirrepo, fmt=fmt, rundepl=rundepl, tstamp=tstamp)

sys.exit('END OF TEST')
