#!/usr/bin/env python
import logging
#logger = logging.getLogger(__name__)
logging.basicConfig(format='[%(levelname).1s]: %(message)s', level=logging.INFO)

import sys
SCRNAME = sys.argv[0].rsplit('/')[-1]

def issue_2021_01_12():
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

    from psana import DataSource, Detector
    ds = DataSource('exp=mfxp17218:run=70:smd')
    det = Detector('epix10k2M')
    #det.set_print_bits(0o377)
    for nevent,evt in enumerate(ds.events()):
        if nevent>5: break
        calib_array = det.calib(evt, cmpars=(7,2,20,10))
        print(calib_array.sum())

def issue_2021_01_13():
    """Hi Mikhail,
       I think the script below works in the new release ana-4.0.9 (py2),
       but ana-4.0.9-py3 shows some error messages but then runs (see below).
       chris
    """
    from psana import DataSource, Detector                    
    #ds = DataSource(exp='ueddaq02',run=81)   
    ds = DataSource('exp=xpplv6818:run=166')  
    epix1 = Detector('epix_1')                
    epix2M = Detector('epix10k2M')            
    #for evt in ds.events():                   
    for nevent,evt in enumerate(ds.events()):
        if nevent>5: break
        img1 = epix1.image(evt)               
        if img1 is None:                      
            print('img1 none')                
        else:                                 
            print('img1',img1.shape)          
        img2 = epix2M.image(evt)              
        if img2 is None:                      
            print('img2 none')                
        else:                                 
            print('img2',img2.shape)          

def issue_2021_MM_DD():
    """ docstring
    """
    metname = sys._getframe().f_code.co_name
    print('method: %s' % metname)
    print('docstring:', eval(metname).__doc__)

#---

USAGE = '\nUsage:'\
      + '\n  python %s <test-name>' % SCRNAME\
      + '\n  where test-name: '\
      + '\n    0 - print usage'\
      + '\n    1 - issue_2021_01_12 - valerio, chuck earlier - fixing float index issue as 352/2'\
      + '\n    2 - issue_2021_01_13 - cpo'\
      + '\n   99 - issue_2021_MM_DD - template'\

TNAME = sys.argv[1] if len(sys.argv)>1 else '0'

if   TNAME in  ('1',): issue_2021_01_12()
elif TNAME in  ('2',): issue_2021_01_13()
elif TNAME in ('99',): issue_2021_MM_DD()
else:
    print(USAGE)
    exit('TEST %s IS NOT IMPLEMENTED'%TNAME)

exit('END OF TEST %s'%TNAME)

