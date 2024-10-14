#!/usr/bin/env python
"""
USAGE: <python> Detector/examples/test-issues-2023.py 1
"""
from Detector.UtilsLogging import sys, logging, STR_LEVEL_NAMES, basic_config
logger = logging.getLogger(__name__)
SCRNAME = sys.argv[0].rsplit('/')[-1]


def test_dsname_detname_shape(kw):
    """
    datinfo -e xpptut15 -r 380 -d CxiDs1.0:Cspad.0
    """
    return {
       'rayonix'       : ('exp=xpptut15:run=240', 'XppEndstation.0:Rayonix.0', (1920, 1920)),
       'cspad2x2'      : ('exp=xpptut15:run=460', 'XcsEndstation.0:Cspad2x2.3', (2, 185, 388)),
       'cspad2x2.3'    : ('exp=xpptut15:run=260', 'MecTargetChamber.0:Cspad2x2.3', (2, 185, 388)),
       'cspad'         : ('exp=xpptut15:run=380', 'CxiDs1.0:Cspad.0', (32, 185, 388)),
       'cspad2'        : ('exp=xpptut15:run=380', 'CxiDs2.0:Cspad.0', (32, 185, 388)),
       'cspad_xpp'     : ('exp=xpptut15:run=320', 'XppGon.0:Cspad.0', (32, 185, 388)),
       'opal1000'      : ('exp=xpptut15:run=310', 'XrayTransportDiagnostic.0:Opal1000.0', (1024, 1024)),
       'pnccd'         : ('exp=xpptut15:run=450', 'Camp.0:pnCCD.1', (4, 512, 512)),
       'epix100a'      : ('exp=xpptut15:run=260', 'XcsEndstation.0:Epix100a.1', (704, 768)),
       'epix_alc3'     : ('exp=xpptut15:run=630', 'epix_alc3', (704, 768)),
       'epix10ka2m'    : ('exp=xpptut15:run=540', 'epix10ka2m', (16, 352, 384)),
       'epix10ka2m.0'  : ('exp=xpptut15:run=570', 'MfxEndstation.0:Epix10ka2M.0', (16, 352, 384)),
       'epix10kaquad'  : ('exp=xpptut15:run=590', 'Epix10kaQuad0', (4, 352, 384)),
       'epix10kaquad.1': ('exp=xpptut15:run=590', 'Epix10kaQuad1', (4, 352, 384)),
       'epix10kaquad.2': ('exp=xpptut15:run=590', 'Epix10kaQuad2', (4, 352, 384)),
       'epix10kaquad.3': ('exp=xpptut15:run=590', 'Epix10kaQuad3', (4, 352, 384)),
       'jungfrau512k'  : ('exp=xpptut15:run=410', 'Jungfrau512k', (1, 512, 1024)),
       'jungfrau1m'    : ('exp=xpptut15:run=430', 'Jungfrau1M', (2, 512, 1024)),
       'jungfrau4m'    : ('exp=xpptut15:run=580', 'jungfrau4M', (8, 512, 1024)),
       'jungfrau4m.2'  : ('exp=xpptut15:run=530', 'DetLab.0:Jungfrau.2', (8, 512, 1024)),
    }[kw]


#FNAME_STATUS = '/cds/data/psdm/XPP/xpptut15/calib/Epix100a::CalibV1/XcsEndstation.0:Epix100a.1/status_extra/0-end.data'
FNAME_STATUS = '/sdf/data/lcls/ds/XPP/xpptut15/calib/Epix100a::CalibV1/XcsEndstation.0:Epix100a.1/status_extra/0-end.data'




def issue_2024_03_08():
    """ISSUE: Vincent: det.image does not pass parameters to det.calib
              Esposito, Vincent <espov@slac.stanford.edu>
              Dubrovin, Mikhail, Damiani, Daniel S.
              Hi Mikhail,
              Here is an example of the image method not passing any argument to calib:
              Jungfrau1M in exp = 'xpply2121'; run = 400
              Basically what I see is in the AreaDetector file(
              /sdf/group/lcls/ds/ana/sw/conda1/inst/envs/ana-4.0.59-py3/lib/python3.9/site-packages/Detector/AreaDetector.py)
              The way the image method handles calib is on line 1625: nda = nda_in if nda_in is not None else self.calib(evt),
              where there is no options to pass extra kwargs to the calib call.
              I think this should be a relatively easy thing to implement, but I am maybe overlooking something.
              Cheers,
              Vincent
       REASON: **kwargs
       FIXED:

       datinfo -e xpply2121 -r400 -d jungfrau1M  # XppEndstation.0:Jungfrau.0
    """
    import psana
    import Detector.GlobalUtils as gu
    import Detector.UtilsGraphics as ug
    flimg = None
    ds = psana.DataSource('exp=xpply2121:run=400')
    det = psana.Detector('XppEndstation.0:Jungfrau.0')
    for i, evt in enumerate(ds.events()):
        if i > 2: break
        print('Ev %03d' % i)
        print(gu.info_ndarr(det.raw(evt),   '  det.raw', last=10))
        #clb = det.calib(evt)
        #img = det.image(evt, nda_in=clb)  ### <<< testing this line for **kwargs passed inside to calib
        #img = det.image(evt, cmpars=(7,7,200,10), edges=True, mrows=10, mcols=10)  ### <<< testing this line for **kwargs passed inside to calib
        img = det.image(evt, nda_in=None, cmpars=(7,0,200,10), edges=True, mrows=10, mcols=10,
                        central=True, wcentral=5)  ### <<< testing this line for **kwargs passed inside to calib
        #print(gu.info_ndarr(clb, '  det.calib', last=5))
        print(gu.info_ndarr(img, '  det.image', last=5))

        if flimg is None:
            flimg = ug.fleximage(img, arr=None, h_in=8, nneg=1, npos=3)
        else:
            flimg.update(img, arr=None)
        ug.gr.show(mode='DO NOT HOLD')
        #break
    ug.gr.show()


def issue_2024_03_12():
    """ISSUE: test det.calib call to new calib_jungfrau_v2
       REASON: new calib_jungfrau_v2
       FIXED:

       datinfo -e xcsx1003522 -r33 -d XcsEndstation.0:Jungfrau.1 # single panel 72257 events
           ievt: 5800 raw shape:(1, 512, 1024) size:524288 dtype:uint16 [2724 2678 2690 2645 2632...]

       datinfo -e cxilx7422 -r232 -d CxiDs1.0:Jungfrau.0 # 8-panel 31652 events
           ievt: 31651 raw shape:(8, 512, 1024) size:4194304 dtype:uint16 [2913 2955 2821 2864 3077...]
    """
    import Detector.GlobalUtils as gu
    import psana
    ds, det = psana.DataSource('exp=cxilx7422:run=232'), psana.Detector('CxiDs1.0:Jungfrau.0') # 8-panel 31652 events
    #ds, det = psana.DataSource('exp=xcsx1003522:run=33'), psana.Detector('XcsEndstation.0:Jungfrau.1') # single panel 72257 events
    for i, evt in enumerate(ds.events()):
        if i > 4: break
        print('Ev %03d' % i)
        print(gu.info_ndarr(det.raw(evt),   '  det.raw  ', last=10))
        print(gu.info_ndarr(det.calib(evt), '  det.calib', last=5))
        #print(gu.info_ndarr(det.image(evt), '  det.image', last=5))


def issue_2024_05_16():
    """ISSUE: test of epix10ka2m scaling
       REASON:
       FIXED:
       datinfo -e xcsl1030422 -r 237 -d XcsEndstation.0:Epix10ka2M.0
    """
    import psana
    import Detector.GlobalUtils as gu
    import Detector.UtilsGraphics as ug
    flimg = None
    ds = psana.DataSource('exp=xcsl1030422:run=237')
    det = psana.Detector('XcsEndstation.0:Epix10ka2M.0')
    for i, evt in enumerate(ds.events()):
        if i > 10: break
        print('Ev %03d' % i)
        print(gu.info_ndarr(det.raw(evt),   '  det.raw', last=10))
        clb = det.calib(evt)
        img = det.image(evt, nda_in=clb, cmpars=(7,0,200,10), edges=True, mrows=10, mcols=10,
                        central=True, wcentral=5)
        print(gu.info_ndarr(clb, '  det.calib', last=5))
        print(gu.info_ndarr(img, '  det.image', last=5))

        if flimg is None:
            flimg = ug.fleximage(img, arr=None, h_in=8, nneg=1, npos=3)
        else:
            flimg.update(img, arr=None)
        ug.gr.show(mode='DO NOT HOLD')
        #break
    ug.gr.show()


def issue_2024_05_18():
    """ISSUE: Silke: jungfrau det.caliib does not work in ana-4.0.61, works in ana-4.0.60
       REASON:
       FIXED:
       datinfo -e cxilx7422 -r 101 -d jungfrau4M # WORKS in ana-4.0.61 and ana-4.0.60
    """
    import psana
    ds = psana.DataSource('exp=cxilx7422:run=101')
    det = psana.Detector('jungfrau4M')
    evt = next(ds.events())
    clb = det.calib(evt, cmpars=(7,0,10), mbits=0) # .shape
    import Detector.GlobalUtils as gu
    print(gu.info_ndarr(clb, 'det.calib'))  #last=5


def issue_2024_06_13():
    """ISSUE: Vincent: det.calib(evt, cmpars=(7,0,10), mbits=0) DOES NOT WORK in ana-4.0.62! AGAIN???
       REASON:
       FIXED:
    """
    import Detector.GlobalUtils as gu
    import psana as ps
    ds_str = 'exp=xppl1021222:run=138'
    ds = ps.MPIDataSource(ds_str)
    det = ps.Detector('jungfrau1M')
    ds.break_after(5)
    for nevt, evt in enumerate(ds.events()):
        # img = det.calib(evt) # works fine
        img = det.calib(evt, cmpars=(7,0,10), mbits=0)
        print(gu.info_ndarr(img, 'evt:%03d  det.calib' % nevt, last=5))


def issue_2024_07_18():
    """ISSUE: test det.calib_epix10ka_v2
       REASON: add loop over segments in the algorithm of _v2
       FIXED:
       datinfo -e cxilx7422 -r 101 -d jungfrau4M # WORKS in ana-4.0.61 and ana-4.0.60
    ds = MPIDataSource('exp=xcsl1030422:run=237')
    det = Detector('XcsEndstation.0:Epix10ka2M.0')
    """
    import numpy as np
    import psana
    import Detector.GlobalUtils as gu
    from time import time
    ds = psana.DataSource('exp=xcsl1030422:run=237')
    det = psana.Detector('XcsEndstation.0:Epix10ka2M.0')
    nevents = 100
    arrts = np.zeros(nevents, dtype=np.float64)
    for nevt, evt in enumerate(ds.events()):
        # img = det.calib(evt) # works fine
        t0_sec = time()
        img = det.calib(evt, cmpars=(7,7,200,10)) # loop_segs=True or False (df)
        arrts[nevt] = dt = time()-t0_sec
        print(gu.info_ndarr(img, 'evt:%03d  dt(sec)=%.3f det.calib' % (nevt, dt), last=4))
        if nevt > nevents-2: break

    print(gu.info_ndarr(arrts, 'array of times', last=nevents))
    tmed = np.median(arrts) # , axis=0)
    print('median time: %.3f sec' % tmed)


def issue_2024_10_08():
    import psana
    from Detector.UtilsEpix10ka2M import id_epix10ka2m_for_env_det

    #ds, det = psana.DataSource('exp=xppl1002323:run=50'), psana.Detector('XppGon.0:Epix10ka2M.0')
    #ds, det = psana.DataSource('exp=xcsl1036223:run=50'), psana.Detector('XcsEndstation.0:Epix10ka2M.0')
    #ds, det = psana.DataSource('exp=mfxp1003323:run=8'), psana.Detector('MfxEndstation.0:Epix10ka2M.0')
    #ds, det = psana.DataSource('exp=mfxp1003323:run=16'), psana.Detector('MfxEndstation.0:Epix10ka2M.0')
    ds, det = psana.DataSource('exp=mfxp1003323:run=24'), psana.Detector('MfxEndstation.0:Epix10ka2M.0')
    print('id_epix10ka2m:', id_epix10ka2m_for_env_det(ds.env(), det))


def issue_2024_MM_DD():
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
    d_logmode = 'INFO' # 'DEBUG'  # 'INFO'
    h_tname  = 'test name, usually numeric number, default = %s' % d_tname
    h_dsname  = 'dataset name, default = %s' % d_dsname
    h_detname  = 'input ndarray source name, default = %s' % d_detname
    h_logmode = 'logging mode, one of %s, default = %s' % (STR_LEVEL_NAMES, d_logmode)
    parser = ArgumentParser(description='%s is a bunch of tests for annual issues' % SCRNAME, usage=USAGE())
    parser.add_argument('tname',            default=d_tname,    type=str,   help=h_tname)
    parser.add_argument('-d', '--dsname',   default=d_dsname,   type=str,   help=h_dsname)
    parser.add_argument('-s', '--detname',  default=d_detname,  type=str,   help=h_detname)
    parser.add_argument('-L', '--logmode',  default=d_logmode,  type=str,   help=h_logmode)
    return parser


def USAGE():
    import inspect
    return '\n  %s <TNAME>\n' % sys.argv[0].split('/')[-1]\
    + '\n'.join([s for s in inspect.getsource(selector).split('\n') if "TNAME in" in s])


def selector():
    parser = argument_parser()
    args = parser.parse_args()
    basic_config(format='[%(levelname).1s] L%(lineno)04d: %(filename)s %(message)s', int_loglevel=None, str_loglevel=args.logmode)
    logging.getLogger('matplotlib.font_manager').setLevel(logging.WARNING) # get rid of messages

    TNAME = args.tname  # sys.argv[1] if len(sys.argv)>1 else '0'
    if   TNAME in  ('1',): issue_2024_03_08() # Vincent: det.image does not pass parameters to det.calib
    elif TNAME in  ('2',): issue_2024_03_12() # test det.calib > new calib_jungfrau_v2
    elif TNAME in  ('3',): issue_2024_05_16() # test of epix10ka2m scaling
    elif TNAME in  ('4',): issue_2024_05_18() # Silke: jungfrau det.caliib does not work in ana-4.0.61, works in ana-4.0.60
    elif TNAME in  ('5',): issue_2024_06_13() # Vincent: det.calib(evt, cmpars=(7,0,10), mbits=0) DOES NOT WORK in ana-4.0.62! AGAIN???
    elif TNAME in  ('6',): issue_2024_07_18() # Me: det.calib(evt, cmpars=(7,0,10)) > det.calib_epix10ka_v2
    elif TNAME in  ('7',): issue_2024_10_08() # Me: test epix10ka2m panel ids
    else:
        print(USAGE())
        sys.exit('TEST %s IS NOT IMPLEMENTED'%TNAME)

    sys.exit('END OF TEST %s'%TNAME)


if __name__ == "__main__":
    selector()
# EOF
