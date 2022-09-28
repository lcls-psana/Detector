#!/usr/bin/env python
"""
USAGE: <python> Detector/examples/test-issues-2022.py 9
"""

#import logging
#logger = logging.getLogger(__name__)
#logging.basicConfig(format='[%(levelname).1s]: %(message)s', level=logging.DEBUG)



import sys
SCRNAME = sys.argv[0].rsplit('/')[-1]


def issue_2022_01_03():
    """ISSUE: Roberto Alvarez <rcalvar2@asu.edu>
       Mon 1/3/2022 11:45 AM
       Thank you for all the assistance you have provided us, we really appreciate it.
       I have not been able to retrieve the geometry in PSF format with the new interface.
       What I do is:...
       REASON: in py3 division is not int...
       FIXED in ana-4.0.35: V02-00-23 - src/UtilsPSF.py - fix py3 issue - use int for devision
    """
    import psana
    import PSCalib.UtilsPSF as ups
    runnum = 312
    #ds = psana.DataSource(f'exp=mfxlv1218:run={runnum}') # py3
    ds = psana.DataSource('exp=mfxlv1218:run=%d'%runnum)
    det = psana.Detector('epix10k2M')
    geom = det.geometry(runnum)
    psf, sego, geo = ups.psf_from_geo(geom, cframe=1)  # this line fails
    print('psf', psf)


def issue_2022_01_04():
    """ISSUE: inducted by issue_2022_01_03 - psf from GeometryAccess
       REASON: because users use Detector object
       FIXED: in GeometryAccess added methods psf() and data_psf(data)
    """
    import psana
    runnum = 312
    ds = psana.DataSource('exp=mfxlv1218:run=%d'%runnum)
    det = psana.Detector('epix10k2M')
    geom = det.geometry(runnum)
    psf = geom.psf(cframe=1)
    print('psf:\n%s' % geom.info_psf())

    xarr, yarr, zarr = geom.pixel_coords_psf(cframe=1)
    from Detector.GlobalUtils import info_ndarr
    print(info_ndarr(xarr,'geom.pixel_coords_psf xarr:'))
    print(info_ndarr(yarr,'geom.pixel_coords_psf yarr:'))
    print(info_ndarr(zarr,'geom.pixel_coords_psf zarr:'))

def issue_2022_01_05():
    """ISSUE: the same as issue_2022_01_04 - psf from Detector
       REASON: because users use Detector object
       FIXED: in AreaDetectr added methods psf(par, cframe=1) and data_psf(par, data)
    """
    import psana
    runnum = 312
    ds = psana.DataSource('exp=mfxlv1218:run=%d'%runnum)
    det = psana.Detector('epix10k2M')
    psf = det.psf(runnum, cframe=1)

    import PSCalib.UtilsPSF as ups
    print('psf:\n%s' % ups.info_psf(psf))

    from Detector.GlobalUtils import np, info_ndarr
    a = np.ones((16, 352, 384))
    print(info_ndarr(a,'psana shaped data'))
    dpsf = det.data_psf(runnum, a)
    print(info_ndarr(dpsf,'PSF shaped data'))

    xarr, yarr, zarr = det.pixel_coords_psf(runnum, cframe=1)
    print(info_ndarr(xarr,'geom.pixel_coords_psf xarr:'))
    print(info_ndarr(yarr,'geom.pixel_coords_psf yarr:'))
    print(info_ndarr(zarr,'geom.pixel_coords_psf zarr:'))


def issue_2022_02_09():
    """ISSUE: Philip - jungfrau may have not switching pixels
       REASON: ???
       FIXED:
    """
    from time import time
    import numpy as np
    from psana import DataSource, Detector
    import PSCalib.GlobalUtils as gu
    from Detector.GlobalUtils import info_ndarr

    #exp, run = 'cxilu7619', 168
    exp, run = 'cxilv1019', 142
    ds = DataSource('exp=%s:run=%d:smd' %(exp, run))
    jf= Detector('jungfrau4M', ds.env())

    g0cut = 1<<14
    g1cut = 2<<14
    g2cut = 3<<14
    modes = ['Normal-00', 'Med-01', 'Low-11', 'UNKNOWN-10']

    bad_tot = None
    for istep, step in enumerate(ds.steps()):
      print('%s mode %s' %(20*'==', modes[istep]))
      #evt = ds.events().next()
      for ievt, evt in enumerate(step.events()):

        if ievt % 20 != 0: continue
        raw = jf.raw(evt)
        t0_sec = time()
        #fg0 = raw<g0cut
        #fg1 = (raw>=g0cut) & (raw<g1cut)
        #fg2 = raw>=g2cut
        #bad = (fg1+fg2, fg0+fg2, fg0+fg1)[istep]

        gbits = raw>>14 # 00/01/11 - gain bits for mode 0,1,2
        fg0, fg1, fg2, fgx = gbits==0, gbits==1, gbits==3, gbits==2

        bad = (np.logical_not(fg0),\
               np.logical_not(fg1),\
               np.logical_not(fg2))[istep]

        dt_sec = time()-t0_sec

        sums = [fg0.sum(), fg1.sum(), fg2.sum(), fgx.sum()]
        s = ' '.join(['%s:%d' % (modes[i], sums[i]) for i in range(4)])
        print('Ev: %4d found pixels %s gain definition time: %.6f sec' % (ievt, s, dt_sec))

        if bad_tot is None: bad_tot = bad
        else: np.logical_or(bad_tot, bad, bad_tot)

        #print(info_ndarr(raw,     '  raw'))
        #print(info_ndarr(fg0,     '  fg0'))
        #print(info_ndarr(bad,     '  bad'))
        #print(info_ndarr(bad_tot, '  bad_tot'))

    print('Total number of bad pixels %d' % bad_tot.sum())

    zeros = np.zeros_like(bad_tot, dtype=np.uint16)

    mask = np.select((bad_tot,), (zeros,), default=1)
    fname = '%s_r%d_bad_tot.npy' %(exp, run)
    np.save(fname, mask+1)
    print('saved file: %s' % fname)


def issue_2022_04_20():
    """datinfo -e mecly4720 -r834 -d MecTargetChamber.0:Epix100a.0
    """
    #import logging
    #logger = logging.getLogger(__name__)
    #logging.basicConfig(format='[%(levelname).1s]: %(message)s', level=logging.DEBUG)

    from Detector.GlobalUtils import np, info_ndarr
    import psana
    runnum = 834
    ds = psana.DataSource('exp=mecly4720:run=%d'%runnum)
    det = psana.Detector('MecTargetChamber.0:Epix100a.0')
    det.set_print_bits(0o177777)

    print(info_ndarr(det.gain(runnum), 'gain:'))


def issue_2022_04_26():
    """ISSUE: Nelson, Silke <snelson@slac.stanford.edu>
    common mode turn off?
    datinfo -e xpptut15 -r 580 -d jungfrau4M
    """
    from time import time
    import psana
    from Detector.GlobalUtils import np, info_ndarr

    #runnum = 580
    #ds = psana.DataSource('exp=xpptut15:run=%d'%runnum)
    #det = psana.Detector('jungfrau4M')

    expname='cxilx8720'
    runnum=6
    #ds = psana.DataSource('exp=%s:run=%d:dir=/cds/data/drpsrcf/%s/%s/xtc'%(expname,runnum,expname[:3],expname))
    ds = psana.DataSource('exp=%s:run=%d'%(expname,runnum))
    det = psana.Detector('jungfrau4M')
    cmpars=(7,1,10,10)

    print(info_ndarr(det.pedestals(runnum),'  det.pedestals(%d)'%runnum))
    print(info_ndarr(det.common_mode(runnum),'  det.common_mode(%d)'%runnum))
    print(info_ndarr(cmpars,' cmpars'))

    for i in range(10):
        evt = ds.events().next()
        t0_sec = time()
        #calib = det.raw(evt)
        calib = det.calib(evt, cmpars=cmpars)
        dt_sec = time()-t0_sec
        print(info_ndarr(calib,'Event %d det.calib(evt,...) dt=%.3f sec' % (i, dt_sec)))


def issue_2022_05_02():
    """O'Grady, Paul Christopher Fri 4/29/2022 5:55 PM
       Hi Mikhail,I think Silke?s code is highlighting an issue in 4.0.39 when cmpars is passed to det.calib
       for epix100 (perhaps others too?). Short script is below. For the weekend the experimenters are working
       around it by using 4.0.36.  Can you have a look on Monday?
       Thanks, and have a good weekend?
       chris

       export PATH=/cds/sw/ds/ana/conda1/inst/envs/ana-4.0.39-py3/bin:$PATH
    """

    #from psana import *
    import psana
    ds = psana.DataSource('exp=xcslx6920:run=2')
    det = psana.Detector('epix_1')
    evt = next(ds.events())
    det.calib(evt)
    print('done det.calib')
    det.calib(evt, cmpars=[6])
    print('done det.calib with cmpars')


def issue_2022_05_16():
    """Frederic P Poitevin <frederic.poitevin@stanford.edu>
    Hi Mikhail, sorry I did not come back to you yet about this.
    It would be interesting to check what the actual pixel size is: 44um or 44.5um?
    The only source I could find was the following where it says 44um: https://lcls.slac.stanford.edu/detectors/rayonix
    So for some reason, `psana` reports 89.0mm no matter what...
    """
    import psana
    #ds = psana.DataSource('exp=mfxlx5520:run=100')
    #det = psana.Detector('Rayonix', ds.env())
    ds = psana.DataSource('exp=xpptut15:run=240')  # MX340-HS:125 'pixel size det value:', 89.0, ' vs cfg value:', 176
    det = psana.Detector('XppEndstation.0:Rayonix.0', ds.env())
    print('dict_rayonix_config:', det.pyda.dict_rayonix_config())  # dict

    cfg = ds.env().configStore()
    #rayonix_cfg = cfg.get(psana.Rayonix.ConfigV2, psana.Source('Rayonix'))
    #import Detector.PyDataAccess as pda
    #co = pda.get_rayonix_config_object(ds.env(), det.source)
    co = det.pyda.det_config_object(ds.env())
    print('dir(rayonix_cfg)', dir(co))
    print('pixel size det value:', det.pixel_size(ds.env), ' vs cfg value:', co.pixelWidth())
    print('Addition from Dan - Device ID:', co.deviceID())
    print('numPixels:', co.numPixels()) # 3686400
    print('pixelWidth:', co.pixelWidth())  # 176
    print('pixelHeight:', co.pixelHeight())  # 176
    print('height:', co.height())  # 1920
    print('width:', co.width())  # 1920

def issue_2022_06_14():
    """Chuck: it would be nice to check rayonix segment geometry for consistency with config.
    """
    import psana
    #ds, runnum = psana.DataSource('exp=mfxlx5520:run=100'), 100
    #det = psana.Detector('Rayonix', ds.env())
    ds, runnum = psana.DataSource('exp=xpptut15:run=240'), 240  # MX340-HS:125 'pixel size det value:', 89.0, ' vs cfg value:', 176
    det = psana.Detector('XppEndstation.0:Rayonix.0', ds.env())
    #print('dict_rayonix_config:', det.pyda.dict_rayonix_config())  # dict
    geom = det.geometry(runnum)


def issue_2022_06_16():
    """/reg/d/psdm/xpp/xpply9820/calib
    """
    import psana
    runnum = 25
    ds = psana.DataSource('exp=xpply9820:run=%d' % runnum)
    det = psana.Detector('XppGon.0:Epix100a.1', ds.env())
    det.set_print_bits(0o377)
    evt = next(ds.events())
    arr = det.calib(evt)
    from Detector.GlobalUtils import info_ndarr
    print(info_ndarr(arr,'det.calib:'))


def issue_2022_09_01():
    """for Philip return file name of the gain file in repository for epix100a
    """
    from Detector.UtilsDeployConstants import file_name_in_repo
    exp = 'xpptut15'
    run = 260
    det = 'XcsEndstation.0:Epix100a.1'
    ctype = 'gain'
    #tstamp = None
    #rundepl = None
    tstamp = '20220901120000'  # or None
    rundepl = '123'  # or None
    print('File name in repository: %s' %\
          file_name_in_repo(exp, run, det, ctype, tstamp=tstamp, rundepl=rundepl)
    )


def issue_2022_09_02():
    """for Philip save file in repository for epix100a
    """
    import logging
    logger = logging.getLogger(__name__)
    logging.basicConfig(format='[%(levelname).1s]: %(message)s', level=logging.DEBUG) #INFO)

    from Detector.UtilsDeployConstants import save_epix100a_ctype_in_repo
    import numpy as np

    arr2d = 0.061*np.ones((704,768))
    exp = 'xpptut15'
    run = 260
    det = 'XcsEndstation.0:Epix100a.1'
    ctype = 'gain'
    tstamp = '20220901120000' # or None
    rundepl = '123' # or None
    save_epix100a_ctype_in_repo(arr2d, exp, run, det, ctype, tstamp=tstamp, rundepl=rundepl, fmt='%.4f')


def issue_2022_09_19():
    """py3 is default sinse 2022-09-15 need to fix DICT_NAME_TO_LEVEL dependence on py2/3
    """
    from time import time
    t0_sec = time()
    from Detector.UtilsLogging import logging, DICT_NAME_TO_LEVEL, STR_LEVEL_NAMES, init_logger, PYTHON_VERSION_MAJOR
    print('import Detector.UtilsLogging time: %.6f sec' % (time()-t0_sec))  # 0.266221 sec !!!!!
    print('DICT_NAME_TO_LEVEL', DICT_NAME_TO_LEVEL)
    print('STR_LEVEL_NAMES', STR_LEVEL_NAMES)
    print('PYTHON_VERSION_MAJOR', PYTHON_VERSION_MAJOR)


def issue_2022_09_26():
    """
       datinfo -e xpptut15 -r 260 -d XcsEndstation.0:Epix100a.1
       datinfo -e xpptut15 -r 260 -d XcsEndstation.0:Cspad2x2.3
       datinfo -e xpptut15 -r 240 -d XppEndstation.0:Rayonix.0
       datinfo -e cxic00318 -r 123 -d jungfrau4M # CxiDs1.0:Jungfrau.0
    """
    import psana
    #ds = psana.DataSource('exp=xpptut15:run=260:smd')
    #det = psana.Detector('XcsEndstation.0:Epix100a.1', ds.env())
    ds = psana.DataSource('exp=cxic00318:run=123:smd')
    #det = psana.Detector('jungfrau4M', ds.env())
    epics = ds.env().epicsStore()
    #epics methods: 'alias', 'aliases', 'getPV', 'names', 'pvName', 'pvNames', 'status', 'value'

    varnames = ['CXI:DS1:MMS:06.RBV', 'CXI:DS2:MMS:06.RBV', 'MFX:DET:MMS:04.RBV',
                'XPP:ROB:POS:Z', 'AMO:LMP:MMS:10.RBV']
    print('epics.names():', epics.names())
    print('epics.pvNames():', epics.pvNames())
    vfound = None
    for vname in varnames:
        if vname in epics.pvNames():
            print('found name:', vname)
            vfound = vname

    print('epics.value("DscCsPad_z"):', epics.value('DscCsPad_z'))  # -424.9936
    print('epics.value("CXI:DS1:MMS:06.RBV"):', epics.value('CXI:DS1:MMS:06.RBV'))  # -424.9936
    print('dir(epics):', dir(epics))
    print('epics.aliases():', epics.aliases())
    print('epics.alias("CXI:DS1:MMS:06.RBV"):', epics.alias('CXI:DS1:MMS:06.RBV'))  # DscCsPad_z
    print('epics.alias("DscCsPad_z"):', epics.alias('DscCsPad_z')) # empty
    print('epics.status():', epics.status('CXI:DS1:MMS:06.RBV'))  # (0, 0, 0.0)
    print('epics.pvName("CXI:DS1:MMS:06.RBV"):', epics.pvName('CXI:DS1:MMS:06.RBV'))
    print('epics.getPV("CXI:DS1:MMS:06.RBV"):', epics.getPV('CXI:DS1:MMS:06.RBV'))  # <psana.Epics.EpicsPvCtrlDouble object at 0x7fe1863349f0>


def issue_2021_MM_DD():
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
      + '\n    1 - issue_2022_01_03 - Roberto Alvarez - issue with psana-to-psf converter in py3'\
      + '\n    2 - issue_2022_01_04 - psf() from GeometryAccess'\
      + '\n    3 - issue_2022_01_05 - psf() from Detector -> AreaDetector -> GeometryAccess'\
      + '\n    4 - issue_2022_02_09 - Philip - catch not switching pixels in jungfrau'\
      + '\n    5 - issue_2022_04_20 - Philip - epix100 default gain'\
      + '\n    6 - issue_2022_04_26 - Silke - how to turn off common mode for jungfrau'\
      + '\n    7 - issue_2022_05_02 - Silke - pbits?'\
      + '\n    8 - issue_2022_05_16 - Frederic - Rayonix pixel size'\
      + '\n    9 - issue_2022_06_14 - Me - Rayonix geometry consistency check'\
      + '\n   10 - issue_2022_06_16 - Vincent - why it is looking for *.h5?'\
      + '\n   11 - issue_2022_09_01 - Philip - file name of the gain file in repository for epix100a'\
      + '\n   12 - issue_2022_09_02 - Philip - save file with gains in repository for epix100a'\
      + '\n   13 - issue_2022_09_19 - py3 is default sinse 2022-09-15 fix DICT_NAME_TO_LEVEL dependence on py2/3'\
      + '\n   14 - issue_2022_09_26 - Chuck - request to access geometry correction z'\

TNAME = sys.argv[1] if len(sys.argv)>1 else '0'

if   TNAME in  ('1',): issue_2022_01_03()
elif TNAME in  ('2',): issue_2022_01_04()
elif TNAME in  ('3',): issue_2022_01_05()
elif TNAME in  ('4',): issue_2022_02_09()
elif TNAME in  ('5',): issue_2022_04_20()
elif TNAME in  ('6',): issue_2022_04_26()
elif TNAME in  ('7',): issue_2022_05_02()
elif TNAME in  ('8',): issue_2022_05_16()
elif TNAME in  ('9',): issue_2022_06_14()
elif TNAME in ('10',): issue_2022_06_16()
elif TNAME in ('11',): issue_2022_09_01()
elif TNAME in ('12',): issue_2022_09_02()
elif TNAME in ('13',): issue_2022_09_19()
elif TNAME in ('14',): issue_2022_09_26()

else:
    print(USAGE)
    exit('TEST %s IS NOT IMPLEMENTED'%TNAME)

exit('END OF TEST %s'%TNAME)

# EOF
