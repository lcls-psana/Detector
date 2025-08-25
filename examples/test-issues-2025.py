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


def issue_2025_01_24():
    """ISSUE: strarup time is 15sec?
       REASON: **kwargs
       FIXED:

       datinfo -e xcsx1003522 -r33 -d XcsEndstation.0:Jungfrau.1 # single panel 72257 events
           ievt: 5800 raw shape:(1, 512, 1024) size:524288 dtype:uint16 [2724 2678 2690 2645 2632...]

       datinfo -e cxilx7422 -r232 -d CxiDs1.0:Jungfrau.0 # 8-panel 31652 events
           ievt: 31651 raw shape:(8, 512, 1024) size:4194304 dtype:uint16 [2913 2955 2821 2864 3077...]
       datinfo -e xpply2121 -r400 -d jungfrau1M  # XppEndstation.0:Jungfrau.0
    """
    import psana
    import Detector.GlobalUtils as gu
    import Detector.UtilsGraphics as ug
    from time import time

    flimg = None
    #ds = psana.DataSource('exp=xpply2121:run=400') det = psana.Detector('XppEndstation.0:Jungfrau.0')
    #ds, det  = psana.DataSource('exp=xppl1021222:run=138)', ps.Detector('jungfrau1M')
    #ds, det =  = psana.DataSource('exp=cxilx7422:run=101'), psana.Detector('jungfrau4M')

    #ds, det = psana.DataSource('exp=cxilx7422:run=232'), psana.Detector('CxiDs1.0:Jungfrau.0') # 8-panel 31652 events
    t0_sec = time()
    ds = psana.DataSource('exp=cxilx7422:run=232')
    print('psana.DataSource: time %3f' % (time() - t0_sec))

    t0_sec = time()
    det = psana.Detector('CxiDs1.0:Jungfrau.0') # 8-panel 31652 events
    print('psana.Detector: time %3f' % (time() - t0_sec))

    for i, evt in enumerate(ds.events()):
        if i > 5: break
        print('Ev %03d' % i)
        print(gu.info_ndarr(det.raw(evt),   '  det.raw', last=10))
        #clb = det.calib(evt)
        #img = det.image(evt, nda_in=clb)  ### <<< testing this line for **kwargs passed inside to calib
        #img = det.image(evt, cmpars=(7,7,200,10), edges=True, mrows=10, mcols=10)  ### <<< testing this line for **kwargs passed inside to calib
        t0_sec = time()
        raw = det.raw(evt)
        dt_sec_raw =time() - t0_sec
        t0_sec = time()
        clb = det.calib(evt, nda_in=None, cmpars=(7,0,200,10), edges=True, mrows=10, mcols=10,
                        central=True, wcentral=5)  ### <<< testing this line for **kwargs passed inside to calib
        dt_sec_calib =time() - t0_sec
        t0_sec = time()
        img = det.image(evt, nda_in=clb)
        dt_sec_image =time() - t0_sec
        #print(gu.info_ndarr(clb, '  det.calib', last=5))
        print(gu.info_ndarr(img, '  det.image', last=5))
        print('det.image: time raw/calib/image %3f/%3f/%3f' % (dt_sec_raw, dt_sec_calib, dt_sec_image))

        if flimg is None:
            flimg = ug.fleximage(img, arr=None, h_in=8, nneg=1, npos=3)
        else:
            flimg.update(img, arr=None)
            ug.gr.set_win_title(flimg.fig, titwin='event %d' % i)
            #ug.gr.add_title_labels_to_axes(flimg.ax, title=title, xlabel='record', ylabel='median intensity', fslab=14, fstit=20, color='k')
        ug.gr.show(mode='DO NOT HOLD')
        #break
    ug.gr.show()


def issue_2025_01_28():
    """ISSUE: strarup time is 15sec?
       REASON: **kwargs
       FIXED:

       datinfo -e xcsx1003522 -r33 -d XcsEndstation.0:Jungfrau.1 # single panel 72257 events
           ievt: 5800 raw shape:(1, 512, 1024) size:524288 dtype:uint16 [2724 2678 2690 2645 2632...]

       datinfo -e cxilx7422 -r232 -d CxiDs1.0:Jungfrau.0 # 8-panel 31652 events
           ievt: 31651 raw shape:(8, 512, 1024) size:4194304 dtype:uint16 [2913 2955 2821 2864 3077...]
       datinfo -e xpply2121 -r400 -d jungfrau1M  # XppEndstation.0:Jungfrau.0
    """
    import psana
    import Detector.GlobalUtils as gu
    import Detector.UtilsGraphics as ug
    from time import time

    flimg = None
    t0_sec = time()
    ds = psana.DataSource('exp=cxilx7422:run=232')
    #print('psana.DataSource: time %3f' % (time() - t0_sec))

    t0_sec = time()
    det = psana.Detector('CxiDs1.0:Jungfrau.0') # 8-panel 31652 events
    #print('psana.Detector: time %3f' % (time() - t0_sec))

    evt = next(ds.events())

    t0_sec = time()
    peds = det.pedestals(evt)
    print('det.pedestals(evt): time %.3f' % (time() - t0_sec), gu.info_ndarr(peds, 'peds', last=5))

    t0_sec = time()
    gain = det.gain(evt)
    print('det.gain(evt):      time %.3f' % (time() - t0_sec), gu.info_ndarr(gain, 'gain', last=5))

    fname = '/sdf/data/lcls/ds/cxi/cxilx7422/calib/Jungfrau::CalibV1/CxiDs1.0:Jungfrau.0/pedestals/230-end.data'

    t0_sec = time()
    nda = gu.np.loadtxt(fname, dtype=float, comments='#')
    print('XXX np.loadtxt time = %.3f sec' % (time()-t0_sec))

    t0_sec = time()
    f=open(fname,'r')
    recs = f.readlines()
    f.close()
    print('XXX f.readlines time = %.3f sec' % (time()-t0_sec))

    t0_sec = time()
    f=open(fname, 'r')
    for i,rec in enumerate(f):
        print('rec:', i, end='\r')
        if rec.isspace(): continue # ignore empty lines
        elif rec[0] == '#': print('cmt rec:',i)
        else: continue
        #else: break
    f.close()
    print('XXX nrecs:%d time = %0.3f sec' % (i, time()-t0_sec))

    t0_sec = time()
    f=open(fname, 'r')
    recs = [s for s in f if not(s[0]=='#' or rec.isspace())]
    f.close()

    svals = ''.join(recs).strip().replace('\n',' ').split()
    #vals = [float(s) for s in svals]

    #nda = gu.np.fromstring(s, dtype=float) # , sep, like=None)
    #nda = gu.np.rec.fromrecords(svals, dtype=float) # , sep, like=None)
    nda = gu.np.array(svals, dtype=float)

    print('XXX nrecs:%d time = %0.3f sec' % (len(recs), time()-t0_sec))
    print('XXX data string:\n', svals[0:10])

    print(gu.info_ndarr(nda, 'XXX nda', last=5))



def issue_2025_08_25():
    """ISSUE: Silke Epix10kaQuad2 common mode does not work ???
       REASON: caching of parameters?
       FIXED:

       datinfo -e mec100836224 -r 154 -d Epix10kaQuad2
    """
    import psana
    import Detector.GlobalUtils as gu
    import Detector.UtilsGraphics as ug

    ds = psana.DataSource('exp=mec100836224:run=154:smd')
    det = psana.Detector('Epix10kaQuad2')
    evt = next(ds.events())

    #cmpars = (7,0,10,10)  # nda for cmpars=(7, 0, 10, 10) shape:(4, 352, 384) size:540672 dtype:float32 [ 9.234083 23.731958 13.910359  9.698472 24.742567...]
    #cmpars=(7,2,10,10)    # nda for cmpars=(7, 2, 10, 10) shape:(4, 352, 384) size:540672 dtype:float32 [ 9.234083 23.731958 13.910359  9.698472 24.742567...]
    #cmpars=(7,3,10,10)    # nda for cmpars=(7, 3, 10, 10) shape:(4, 352, 384) size:540672 dtype:float32 [ 9.234083 23.731958 13.910359  9.698472 24.742567...]
    #cmpars=(7,3,100,10)   # nda for cmpars=(7, 3, 100, 10) shape:(4, 352, 384) size:540672 dtype:float32 [ 9.234083 23.731958 13.910359  9.698472 24.742567...]
    #cmpars=(7,3,1000,10)   # nda for cmpars=(7, 3, 1000, 10) shape:(4, 352, 384) size:540672 dtype:float32 [-8.097311    6.85634    -0.50566137 -3.7303126   9.018064  ...]
    #cmpars=(7,3,1000000,1) #nda for cmpars=(7, 3, 1000000, 1) shape:(4, 352, 384) size:540672 dtype:float32 [-2.6022637 11.337061   3.4141989 -0.6704042 14.192256 ...]
    cmpars=(7,7,300,10)   # nda for cmpars=(7, 7, 300, 10) shape:(4, 352, 384) size:540672 dtype:float32 [ -0.9283596  13.569515  -13.185596  -15.412844   -3.3592076...]

    nda = det.calib(evt, cmpars=cmpars)
    print(gu.info_ndarr(nda, 'nda for cmpars=%s' % str(cmpars), last=5))

    if False: # Silke's code
        dat30 = det.calib(evt)
        dat80 = det.calib(evt, cmpars=(7,0,10,10))
        dat84 = det.calib(evt, cmpars=(7,2,10,10))
        dat85 = det.calib(evt, cmpars=(7,3,10,10))
        datAll = det.calib(evt, cmpars=(7,3,1000000,1))
        print((dat30-dat80).std())
        print((dat80-dat84).std())
        print((dat80-dat85).std())
        print((dat80-datAll).std())







    

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
    d_tname   = '0'
    d_dsname  = 'exp=xpplw3319:run=293'  # None
    d_detname = 'epix_alc3'  # None
    d_logmode = 'INFO' # 'DEBUG'  # 'INFO'
    d_addpar  = None
    h_tname   = 'test name, usually numeric number, default = %s' % d_tname
    h_dsname  = 'dataset name, default = %s' % d_dsname
    h_detname = 'input ndarray source name, default = %s' % d_detname
    h_logmode = 'logging mode, one of %s, default = %s' % (STR_LEVEL_NAMES, d_logmode)
    h_addpar  = 'additional parameter, default = %s' % d_addpar
    parser = ArgumentParser(description='%s is a bunch of tests for annual issues' % SCRNAME, usage=USAGE())
    parser.add_argument('tname',            default=d_tname,    type=str,   help=h_tname)
    parser.add_argument('-d', '--dsname',   default=d_dsname,   type=str,   help=h_dsname)
    parser.add_argument('-s', '--detname',  default=d_detname,  type=str,   help=h_detname)
    parser.add_argument('-L', '--logmode',  default=d_logmode,  type=str,   help=h_logmode)
    parser.add_argument('-a', '--addpar',   default=d_addpar,   type=str,   help=h_addpar)
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
    if   TNAME in  ('1',): issue_2025_01_24() # strarup time is 15sec?
    elif TNAME in  ('2',): issue_2025_01_28() # time to access constants
    elif TNAME in  ('3',): issue_2025_08_25() # Silke Epix10kaQuad2 common mode does not work ???

    else:
        print(USAGE())
        sys.exit('TEST %s IS NOT IMPLEMENTED'%TNAME)

    sys.exit('END OF TEST %s'%TNAME)


if __name__ == "__main__":
    selector()
# EOF
