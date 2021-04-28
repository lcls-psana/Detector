#!/usr/bin/env python
#import logging
#logger = logging.getLogger(__name__)
#logging.basicConfig(format='[%(levelname).1s]: %(message)s', level=logging.INFO)

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


def issue_2021_02_22():
    """ISSUE: Silke & Lennart - epix100a geometry missing in calib and can't be loaded from h5 file
       REASON:
    /cds/home/d/dubrovin/LCLS/con-py2/arch/x86_64-rhel7-gcc48-opt/python/PSCalib/DCVersion.py:131: H5pyDeprecationWarning:
    dataset.value has been deprecated. Use dataset[()] instead.
    d = v.value -> v[()]

    print_h5_structure.py <*.h5>
    geometry is missing in
    /reg/d/psdm/mec/meclv2518/calib/epix100a/epix100a-3925999620-0996432897-3590324234-1232100352-1154532875-2654088449-0033554455.h5
    /reg/d/psdm/mec/meclv2518/calib/epix100a/epix100a-3925999620-0996663297-3791650826-1232098304-0953206283-2655595777-0520093719.h5
    geometry available in the same named files under
    /reg/d/psdm/detector/calib/epix100a/...
    """
    #logging.basicConfig(format='[%(levelname).1s] L%(lineno)04d: %(message)s', level=logging.DEBUG)
    import psana
    ds = psana.DataSource('exp=meclv2518:run=100')
    evt = ds.events().next()
    det = psana.Detector('epix100a_1_BXRTS')
    #det.set_print_bits(0o377)
    print('det.raw(evt).shape', det.raw(evt).shape)
    print('det.image(evt).shape', det.image(evt).shape)


def issue_2021_02_23():
    """ISSUE: Hi Mikhail,
    Valerio made ana-4.0.16 (py2 and py3) but it looks like py3 is still broken (see below).
    Now that Valerio has translated the pkl file from py2->py3,
    can you try debugging with a test-release when you have a chance?
    (note that the ued pedestal problem is higher priority, I believe).
    chris
    """
    import psana
    import sys
    ds = psana.DataSource('exp=meclv2518:run=269')
    det = psana.Detector("MecTargetChamber.0:Epix100a.1")
    #det.set_print_bits(0o377)
    for i,evt in enumerate(ds.events()):
        print(i, det.image(evt).shape)
        if i>50: break


def issue_2021_02_28():
    """ISSUE: Nelson, Silke <snelson@slac.stanford.edu>
    Sun 2/28/2021 1:28 AM
    Hi Mikhail,
    The following works in the old analysis release, but not in the new ones (only tried 4.0.12 and 4.0.15)
    In [1]: import psana; ds = psana.DataSource('exp=xcsx39718:run=9')
    In [2]: det = psana.Detector('epix10k135')
    In [3]: for i in range(100): evt = ds.events().next()
    In [4]: det.calib(evt)
    Best,Silke
    """
    logging.basicConfig(format='[%(levelname).1s] L%(lineno)04d: %(message)s', level=logging.DEBUG)
    import psana
    ds = psana.DataSource('exp=xcsx39718:run=9')
    det = psana.Detector('epix10k135')
    for i in range(10):
        evt = ds.events().next()
        calib = det.calib(evt)
        if calib is None: continue
        print('%2d:'%i, ' calib.shape', calib.shape)


def issue_2021_02_28B():
    """ISSUE: Nelson, Silke
    Sun 2/28/2021 1:57 PM
    Hi all,
    I have some trouble running my code on the epix10k135 and have traced it down to the shape of the data returned by det.coords_x(evt/run#).
    This is a gain switching detectors with a single ?tile?, but with a geometry file.
    I would have expected it to behave like the jungfrau512k which returns a pedestal of shape (3, 1, 512, 1024)
    and a geometry of shape (1, 512, 1024) and data of shape  (1, 512, 1024).
    The epix10k135 return pedestals of shape  (7, 1, 352, 384), data of shape  (1, 352, 384),
    but coordinate arrays of shape  (352, 384). In an attempt to be generic, my code chokes on this.
    It?s not like I can?t code around this, but I feel I should not have to and that the coordinate functions should return arrays of the same shape as the data.
    Please let me know if this could be done and what, if any, arguments speak against that.
    Thank you,Silke
    REASON: in AreaDetector.py _shaped_array_ did not resaped EPIX10KA
    FIXED: for EPIX10KA auto-reshape all 2d to 3d
    """
    import psana
    runnum = 9
    ds = psana.DataSource('exp=xcsx39718:run=%d'%runnum)
    d1 = psana.Detector('epix10k135')
    print('d1.pedestals(9).shape', d1.pedestals(runnum).shape) # (7, 1, 352, 384)
    print('d1.coords_x(9).shape', d1.coords_x(runnum).shape) # (352, 384)
    for i in range(10):
        evt = ds.events().next()
        calib = d1.calib(evt)
        if calib is None: continue
        print('%2d:'%i, ' calib.shape', calib.shape)


def issue_2021_03_01():
    """ISSUE: Nelson, Silke <snelson@slac.stanford.edu>
    Mon 3/1/2021 9:59 PM
    Hi Mikhail,
    I would  like to explicitly code up the common mode algorithm for the jungfrau that currently corresponds to ?calib?.
    For the epxi10k2m, using (7.2.10.10) did give me the same result as calib which corresponds to what you state on the common modeled page.
    For the Jungfrau, I can?t quite figure out how to get to the same result. Can you help me?
    Thank you,
    Silk
    xpplw0018, run 130 I think. Might have been xpplv0918, run 30, but the latter is likely only noise
    """
    from Detector.GlobalUtils import info_ndarr
    import psana
    runnum = 130
    ds = psana.DataSource('exp=xpplw0018:run=%d'%runnum)
    det = psana.Detector('XppEndstation.0:Jungfrau.0')
    print(info_ndarr(det.pedestals(runnum),'  det.pedestals(run=%d)'%runnum))
    print(info_ndarr(det.coords_x(runnum),'  det.coords_x (run=%d)'%runnum))
    for i in range(2):
        evt = ds.events().next()
        calib = det.calib(evt)
        print('==== Event %d' % i)
        if calib is None:
            print('  det.calib(evt) is None')
            continue
        print(info_ndarr(calib,'  calib      '))
        calib701010 = det.calib(evt, cmpars=(7,0,10,10))
        calib731010 = det.calib(evt, cmpars=(7,3,10,10))
        calib721010 = det.calib(evt, cmpars=(7,2,10,10))
        calib73100  = det.calib(evt, cmpars=(7,3,100))
        calib701000 = det.calib(evt, cmpars=(7,1,100,0))
        print(info_ndarr(calib731010,'  calib731010'))
        print('  calib-calib701010', (calib-calib701010).sum()) #-260670.42 event 0
        print('  calib-calib721010', (calib-calib721010).sum()) #-208380.22
        print('  calib-calib731010', (calib-calib731010).sum()) #-181821.19
        print('  calib-calib73100 ', (calib-calib73100).sum())  # 4698.788
        print('  calib-calib701000', (calib-calib701000).sum()) # 0?


def issue_2021_03_17():
    """ISSUE: Nelson, Silke <snelson@slac.stanford.edu>
    jungfrau calibration using evcode
    """
    from Detector.GlobalUtils import info_ndarr
    import psana

    runnum = 238 #244
    evcode = '162' #'120,162,-137' # None
    counter = 0

    from Detector.EvrDetector import EvrDetector
    from Detector.EventCodeManager import EventCodeManager
    ecm = EventCodeManager(evcode, 0o1)

    ds = psana.DataSource('exp=cxilu9218:run=%d'%runnum)
    det = psana.Detector('CxiDs1.0:Jungfrau.0')
    #evrdet = EvrDetector(':Evr')

    for i in range(1000):
        evt = ds.events().next()
        #raw = det.raw(evt)
        #if raw is None: continue
        #print('==== Event %2d '%i)
        #print(info_ndarr(raw, '  raw '))
        #if not ecm.select(evt): continue 
        #evt_codes = evrdet.eventCodes(evt)
        select = ecm.select(evt)
        #evt_codes = ecm.event_codes(evt)
        #print('==== Event %3d' % i, end='\r')
        if i < 6 \
        or i < 51 and not i%10 \
        or not i%100: print('==== Event %3d   selected: %s evt_codes: %s' % (i, select, str(ecm.event_codes(evt))))
        if not select: continue
        counter += 1
        raw = det.raw(evt)
        print('==== Event %3d   selected: %s evt_codes: %s' % (i, select, str(ecm.event_codes(evt))))
        print(info_ndarr(raw, '  raw %03d '%counter))


def issue_2021_03_18():
    """ISSUE:
    pcds-ana-l@SLAC.STANFORD.EDU on behalf of Nelson, Silke <000001b5861c978b-dmarc-request@LISTSERV.SLAC.STANFORD.EDU>
    Wed 3/17/2021 8:57 PM
    Hi Chris & Mikhail,

    We have an issue with the small epix10k in psana: 
    The pedestal is the right shape and so is the raw data. 
    In this experiment, I have both a 2M and a 135k. When my first call to calib(evt) goes out to the 135k, everthing looks fine. 
    If I ask for the 2M first, calib(evt) for the 135k returns data of the 2M shape where the data for the first tiles is repeated 16 times. 
    Something must be going wrong with the caching.
    Best,
    Silke

    WORKS:
    """
    import logging
    logger = logging.getLogger(__name__)
    logging.basicConfig(format='[%(levelname).1s] L%(lineno)04d: %(filename)s %(message)s', level=logging.INFO)

    import psana
    ds = psana.DataSource('exp=xcsx39718:run=222')
    det2M = psana.Detector('epix10k2M')
    det135k = psana.Detector('epix10k135')
    evt = ds.events().next()
    print('135k ped   shape: ', det135k.pedestals(evt).shape)
    print('135k raw   shape: ', det135k.raw(evt).shape)
    print('2M   ped   shape: ', det2M.pedestals(evt).shape)
    print('2M   raw   shape: ', det2M.raw(evt).shape)
    print('\nXXX NO problem below VVVVVV')
    print('135k calib shape: ', det135k.calib(evt).shape)
    print('\nXXX NO problem above ^^^^^^')
    print('2M   calib shape: ', det2M.calib(evt).shape)


def issue_2021_03_18B():
    """
    CONTINUE issue_2021_03_18
    DID NOT WORK:
    TESTED:
    /reg/d/psdm/xcs/xcsx39718/calib
    /reg/d/psdm/xcs/xcsx39718/calib/Epix10ka2M::CalibV1/XcsEndstation.0:Epix10ka2M.0/pedestals/167-end.data - ok
    /reg/d/psdm/xcs/xcsx39718/calib/Epix10ka::CalibV1/XcsEndstation.0:Epix10ka.1/pedestals/167-end.data - ok
    /reg/d/psdm/xcs/xcsx39718/calib/Epix10ka::CalibV1/XcsEndstation.0:Epix10ka.1/pedestals/223-end.data - ok
    /reg/d/psdm/xcs/xcsx39718/calib/Epix10ka::CalibV1/XcsEndstation.0:Epix10ka.1/pixel_gain/167-end.data - ok
    /reg/d/psdm/xcs/xcsx39718/calib/Epix10ka::CalibV1/XcsEndstation.0:Epix10ka.1/pixel_status/167-end.data - ok

    REASON: store = Storage() # singleton is used for all detectors
    FIXED: dic_store = {} # {detname:Storage()}
    """
    import logging
    logger = logging.getLogger(__name__)
    logging.basicConfig(format='[%(levelname).1s] L%(lineno)04d: %(filename)s %(message)s', level=logging.INFO)

    import psana
    ds = psana.DataSource('exp=xcsx39718:run=222')
    det2M = psana.Detector('epix10k2M')
    det135k = psana.Detector('epix10k135')
    evt = ds.events().next()
    print('2M   ped   shape: ', det2M.pedestals(evt).shape)
    print('2M   raw   shape: ', det2M.raw(evt).shape)
    print('135k ped   shape: ', det135k.pedestals(evt).shape)
    print('135k raw   shape: ', det135k.raw(evt).shape)
    print('2M   calib shape: ', det2M.calib(evt).shape)
    print('\nXXX problem is coming ======')
    print('135k calib shape: ', det135k.calib(evt).shape) # RETURNED shape:(16, 352, 384)
    #c135 = det135k.calib(evt)
    #for tile in c135:
    #    print(tile.sum())


def issue_2021_03_24():
    """Not predictable detector name in Detector('ControlData')().pvLabels()

    OUTPUT:

    det2M   name: XcsEndstation-0|Epix10ka2M-0
    det135k name: XcsEndstation-0|Epix10ka-1
    == run 4  step 00
    cc_name: Epix10ka2M-0 scan cc_value: dark Fixed High Gain
    cc_name: XcsEndstation-0|Epix10ka-1 scan cc_value: dark Fixed High Gain
    cc_name: XcsEndstation-1|Opal1000-1 scan cc_value: pedestal

    REASON: no matching between XcsEndstation-0|Epix10ka2M-0 and Epix10ka2M-0
    """
    from psana import DataSource, Detector
    ds = DataSource('exp=xcslv9718:run=4:smd')
    det2M   = Detector('epix10k2M')
    det135k = Detector('epix10k135')
    cd      = Detector('ControlData')

    print('det2M   name: %s' % str(det2M.name).replace(':','|').replace('.','-'))
    print('det135k name: %s' % str(det135k.name).replace(':','|').replace('.','-'))

    for orun in ds.runs():
      for istep, step in enumerate(orun.steps()): #(loop through calyb cycles, using only the first):
        print('== run %d  step %02d' % (orun.run(), istep))

        for pv in cd().pvLabels():
            print('cc_name: %s cc_value: %s' % (pv.name(), pv.value()))


def issue_2021_04_08():
    """too long run loop
    """
    from time import time
    from psana import DataSource
    ds = DataSource('exp=cxilu9218:run=238:smd')
    t0_sec = time()
    for irun, orun in enumerate(ds.runs()):
        print('run[%d] %d' % (irun, orun.run()))
    print('run empty loop takes %.3f sec' % (time()-t0_sec)) # 88 sec in smd


def issue_2021_04_27():
    """Nelson, Silke <snelson@slac.stanford.edu>
       Tue 4/27/2021 9:10 PM
       Hi, I am looking at old epix100 data to prepare for the upcoming MEC experiment.
       I have noticed that the ?geometry? for the epix100 is currently broken
       and have determined that this change from ana-4.0.16 to ana-4.0.17.
       Calls to e.g. det.coords_x(evt/run) currently return an error and det.image no longer works
       (it is supposed to change the geometry in a predefined way for the epix100.
       Can you look at this?
       Thank you,
       Silke
       (ana-4.0.16) snelson@psanagpu106:/reg/d/psdm/mec/meclq8515/results/smalldata_tools$ python junk.py
       ...

    REASON: GeometryAccess.load_pars_from_str(s) began receive str s as unicode...
    FIXED:  if isinstance(s, unicode): s = s.encode('utf-8') #str(s)
    """
    #import logging
    #logger = logging.getLogger(__name__)
    #logging.basicConfig(format='[%(levelname).1s] L%(lineno)04d: %(filename)s %(message)s', level=logging.DEBUG)

    import psana
    ds = psana.DataSource('exp=meclq8515:run=266')
    det = psana.Detector('epix100a')
    #det.set_print_bits(0o377) # add for debugging
    evt = ds.events().next()
    print('calib')
    print(det.calib(evt).shape)
    print('image')
    img = det.image(evt)
    print(img.shape)


def issue_2021_MM_DD():
    """ISSUE:
       REASON:
       FIXED:
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
      + '\n    4 - issue_2021_02_16 - Silke - exp=xpplw0018:run=7 - common mode correction for the jungfrau'\
      + '\n    5 - issue_2021_02_22 - Silke & Lennart exp=meclv2518:run=100- epix100a geometry'\
      + '\n    6 - issue_2021_02_23 - cpo - exp=meclv2518:run=269 - Epix100a'\
      + '\n    7 - issue_2021_02_28 - Silke - exp=xcsx39718:run=9 - epix10k135 - calib'\
      + '\n    8 - issue_2021_02_28B- Silke - exp=xcsx39718:run=9 - epix10k135 - shape '\
      + '\n    9 - issue_2021_03_01 - Silke - exp=xpplv0918:run=30 - default c ommon mode for Jungfrau'\
      + '\n   10 - issue_2021_03_17 - Silke - exp=cxilu9218:run=240 - Jungfrau dark processing using evcode'\
      + '\n   11 - issue_2021_03_18 - Silke - exp=xcsx39718:run=222 epix10k135 and epix10k2M'\
      + '\n   12 -                                                  epix10k2M and epix10k135'\
      + '\n   13 - issue_2021_03_24 - Silke - exp=xcsx39718:run=222 epix10k135 and epix10k2M configuration issue'\
      + '\n   14 - issue_2021_04_08 - my - exp=xcsx39718:run=222 too lonng run loop'\
      + '\n   15 - issue_2021_04-27 - Silke - exp=meclq8515:run=266 epix100a - det.image does not work'\
      + '\n   99 - issue_2021_MM_DD - template'\

TNAME = sys.argv[1] if len(sys.argv)>1 else '0'

if   TNAME in  ('1',): issue_2021_01_12()
elif TNAME in  ('2',): issue_2021_01_13()
elif TNAME in  ('3',): issue_2021_02_02()
elif TNAME in  ('4',): issue_2021_02_16()
elif TNAME in  ('5',): issue_2021_02_22()
elif TNAME in  ('6',): issue_2021_02_23()
elif TNAME in  ('7',): issue_2021_02_28()
elif TNAME in  ('8',): issue_2021_02_28B()
elif TNAME in  ('9',): issue_2021_03_01()
elif TNAME in ('10',): issue_2021_03_17()
elif TNAME in ('11',): issue_2021_03_18()
elif TNAME in ('12',): issue_2021_03_18B()
elif TNAME in ('13',): issue_2021_03_24()
elif TNAME in ('14',): issue_2021_04_08()
elif TNAME in ('15',): issue_2021_04_27()
elif TNAME in ('99',): issue_2021_MM_DD()
else:
    print(USAGE)
    exit('TEST %s IS NOT IMPLEMENTED'%TNAME)

exit('END OF TEST %s'%TNAME)

