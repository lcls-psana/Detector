"""
2021-01-12 valerio, chuck earlier - fix is losed due to transition to py3
Traceback (most recent call last):
  File "test.py", line 6, in <module>
    calib_array = det.calib(evt)
  File "/cds/sw/ds/ana/conda1/inst/envs/ana-4.0.7-py3/lib/python3.7/site-packages/Detector/AreaDetector.py", line 998, in calib
    return calib_epix10ka_any(self, evt, cmpars, **kwargs)
  File "/cds/sw/ds/ana/conda1/inst/envs/ana-4.0.7-py3/lib/python3.7/site-packages/Detector/UtilsEpix10ka.py", line 429, in calib_epix10ka_any
    common_mode_2d_hsplit_nbanks(arrf[s,:hrows,:], mask=gmask[s,:hrows,:], nbanks=8, cormax=cormax, npix_min=npixmin)
TypeError: slice indices must be integers or None or have an __index__ method

REASON: it was float index: hrows = 176 # int(352/2)
"""
import logging
logger = logging.getLogger(__name__)
logging.basicConfig(format='[%(levelname).1s] L%(lineno)04d: %(message)s', level=logging.DEBUG)

from psana import *
ds = DataSource('exp=mfxp17218:run=70:smd')
det = Detector('epix10k2M')
#det.set_print_bits(0o377)
for nevent,evt in enumerate(ds.events()):
    if nevent>5: break
    calib_array = det.calib(evt, cmpars=(7,2,20,10))
    print(calib_array.sum())
