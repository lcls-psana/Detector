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


def id_epix10ka(co, ielem=0) :
    """Returns Epix10ka2M Id as a string,
       e.g., 3925999616-0996663297-3791650826-1232098304-0953206283-2655595777-0520093719
       co is psana.Epix.Config10kaQuadV1 or psana.Epix.Config10ka2MV1
    """
    quad_shape = getattr(co, "quad_shape", None)
    eco = co.elemCfg(ielem)
    qco = co.quad() if quad_shape is None else co.quad(ielem//4)

    fmt2 = '%010d-%010d'
    zeros = fmt2 % (0,0)
    version = '%010d' % (co.Version) if getattr(co, "Version", None) is not None else '%010d' % 0
    carrier = fmt2 % (eco.carrierId0(), eco.carrierId1())\
              if getattr(eco, "carrierId0", None) is not None else zeros
    digital = fmt2 % (qco.digitalCardId0(), qco.digitalCardId1())\
              if getattr(qco, "digitalCardId0", None) is not None else zeros
    #analog  = fmt2 % (qco.analogCardId0(), qco.analogCardId1())\
    #          if getattr(o, "analogCardId0", None) is not None else zeros
    analog  = zeros
    return '%s-%s-%s-%s' % (version, carrier, digital, analog)


def issue_2021_02_02():
    """Bhavna Nayak reported that order of epix10ka2m panels is changing from exp to exp...
    epix10ka_id exp=xcsx39618:run=10 epix10k2M
    epix10ka_id exp=xpplv6818:run=10 epix10k2M
    epix10ka_id exp=xpplu9818:run=10 epix10k2M
    epix10ka_id exp=detdaq18:run=222 epix10k2M
    """
    #from Detector.AreaDetector import AreaDetector
    #det = AreaDetector('XcsEndstation.0:Epix10ka2M.0', env)
    #from Detector.UtilsEpix10ka2M import ids_epix10ka2m #, get_epix10ka_any_config_object
    #from psana import DataSource, Detector #, Source
    #import _psana

    import psana
    detname = 'epix10k2M' # 'XcsEndstation.0:Epix10ka2M.0'
    for dsname in ('exp=xcsx39618:run=10',\
                   'exp=xpplv6818:run=10',\
                   'exp=xpplu9818:run=10'):
        print('%s\n%s' % (50*'_',dsname))

        ds = psana.DataSource(dsname)
        env = ds.env()
        det = psana.Detector(detname)
        co = env.configStore().get(psana.Epix.Config10ka2MV1, det.source) # get_epix10ka_any_config_object(env, det.source)
        ids = [id_epix10ka(co, ielem=i) for i in range(co.numberOfElements())] # ids_epix10ka2m(co)
        msg = 'Config object: %s' % str(co)
        for i,id in enumerate(ids) : msg += '\nelem %2d: %s' % (i,id)
        print(msg)


def issue_2021_02_16():
    """ISSUE:

       Hi Mikhail,
       I was looking into using the common mode correction for the jungfrau1M ini XPP.
       I wanted to start by comparing no common mode (7,0,10,10) to the ?optimum? (7,3,10,10).
       This common mode works in the old psana, but not the new one. 
       Can you look into this? Am I calling this wrong?
       Best,
       Silke

       REASON:
       in Python 2.7.15 a devision 512/2 returns float / not int
    """
    import psana
    ds = psana.DataSource('exp=xpplw0018:run=7')
    det = psana.Detector('jungfrau1M')
    evt = ds.events().next()
    p = det.calib(evt, cmpars=(7,3,10,10))
    print('det.calib(evt,...):\n%s' % str(p))


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
      + '\n    3 - issue_2021_02_02 - Bhavna Nayak'\
      + '\n    4 - issue_2021_02_16 - Silke'\
      + '\n   99 - issue_2021_MM_DD - template'\

TNAME = sys.argv[1] if len(sys.argv)>1 else '0'

if   TNAME in  ('1',): issue_2021_01_12()
elif TNAME in  ('2',): issue_2021_01_13()
elif TNAME in  ('3',): issue_2021_02_02()
elif TNAME in  ('4',): issue_2021_02_16()
elif TNAME in ('99',): issue_2021_MM_DD()
else:
    print(USAGE)
    exit('TEST %s IS NOT IMPLEMENTED'%TNAME)

exit('END OF TEST %s'%TNAME)

