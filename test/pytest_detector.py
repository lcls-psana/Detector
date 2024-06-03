"""
   Usage::
   pytest Detector/test/pytest_detector.py
"""
import sys
import psana
from Detector.GlobalUtils import np, info_ndarr
from data_test_access.absolute_path import os, path_to_xtc_test_file, path_to_calibdir
from PSCalib.GlobalUtils import create_directory

def _stdout(s):
    """replacement of print(s) # WORKS TOO"""
    sys.stdout.write(s)
    sys.stdout.flush()

def path_exists(path, msg='\n  file exists: '):
    assert os.path.exists(path)
    print('%s%s' % (msg, path))

def data_exists(path='/tmp/data_test'):
    """restore data in path if not available"""
    if os.path.exists(path): return
    cmd = 'git clone git@github.com:lcls-psana/data_test %s' % path
    print('execute command: %s' % cmd)
    os.system(cmd)

def logname_prefix(dirwork, prefix='log-subproc-det'):
    create_directory(dirwork, mode=0o775, group='ps-users')
    return os.path.join(dirwork, prefix)

def compare_det_raw(fname_xtc, detname='XppGon.0:Epix100a.1', expected='shape:(704, 768) size:540672 dtype:uint16 [3861 4050 3976 3992 3778...]'):
    ds = psana.DataSource(fname_xtc)
    det = psana.Detector(detname)
    evt = next(ds.events())
    s = info_ndarr(det.raw(evt))
    print('\n  1-st event raw: %s' % s.rstrip('\n'))
    assert s == expected

def compare_det_calib(fname_xtc, detname='XppGon.0:Epix100a.1', expected='shape:(704, 768) size:540672 dtype:uint16 [3861 4050 3976 3992 3778...]', **kwa):
    ds = psana.DataSource(fname_xtc)
    det = psana.Detector(detname)
    evt = next(ds.events())
    s = info_ndarr(det.calib(evt))
    print('\n  1-st event calib: %s' % s.rstrip('\n'))
    assert s == expected

def is_turned_off(turned_off=True):
    if turned_off: print('\nWARNING: TEST IS TURNED OFF')
    return turned_off

def subproc_in_log(command_seq, logname, env=None, shell=False, tmax_sec=500):
    """Incranation of CalibManager.GlobalUtils.subproc_in_log
       execute command_seq in subprocess, output results in log file,
       returns error message or completein message.
       ex: command_seq=['bsub', '-q', cp.batch_queue, '-o', 'log-ls.txt', 'ls -l']
    """
    from time import time, sleep
    import subprocess
    import logging
    logger = logging.getLogger(__name__)
    log = open(logname, 'w')
    p = subprocess.Popen(command_seq, stdout=log, stderr=log, env=env, shell=shell) #, stdin=subprocess.STDIN, stderr=subprocess.PIPE
    #p.wait()
    t0_sec = time()
    _stdout('subprocess is started with tmp log: %s\n' % logname)
    while p.poll() is None:
      sleep(5)
      dt = time()-t0_sec
      _stdout(('\r' if dt>5 else '') + 'subprocess is working for %.0f sec ' % dt)
      if p and dt>tmax_sec:
        _stdout('\nsubprocess is working too long - terminated' % dt)
        break
    log.close()
    err = p.stderr.read() if p and p.stderr is not None else 'subprocess is completed'
    return err

def path_default_geometry(defname='geometry-def-epix100a.data'):
    """Returns path to default geometry
        defname = 'geometry-def-epix100a.data'
             	  'geometry-def-pnccd.data'
             	  'geometry-def-cspad.data'
             	  'geometry-def-cspad2x2.data'
                  'geometry-def-jungfrau05m.data'
                  'geometry-def-jungfrau1m.data'
             	  'geometry-def-jungfrau4m.data'
             	  'geometry-def-epix10ka2m.data'
             	  'geometry-def-epix10kaquad.data'
    """
    import CalibManager.AppDataPath as apputils
    return apputils.AppDataPath('Detector/' + defname).path()


def deploy_constants_from_file(fname, dircalib='./calib', cdtype='Epix100a::CalibV1/XppGon.0:Epix100a.1', ctype='geometry', cfname='0-end.data'):
    from PSCalib.GlobalUtils import deploy_file
    ctypedir = '%s/%s' % (dircalib, cdtype)
    _stdout('\nfname: %s' % fname)
    deploy_file(fname, ctypedir, ctype, cfname, lfname=None, verbos=True)
    ofname = '%s/%s/%s' % (ctypedir, ctype, cfname) # './calib/Epix100a::CalibV1/XppGon.0:Epix100a.1/geometry/0-end.data'
    assert os.path.exists(ofname)
    print('\ndeployed geometry: %s  ' % ofname)


class det_epix100a():

    def __init__(self):
        """
        """
        print('__init__ for %s' % self.__class__.__name__)
        self.fname_xtc = path_to_xtc_test_file(fname='data-xppn4116-r0137-3events-epix100a.xtc')
        #print('\n\n======== %s' % self.__class__.__name__) ##.split('_')[-1])
        #self.dircalib = './calib'
        self.dircalib = path_to_calibdir()
        self.dirwork = './work'
        self.logname = logname_prefix(self.dirwork, prefix='log-subproc-epix100a')
        psana.setOption('psana.calib-dir', self.dircalib)
        self.test_det_completed = False
        self.turn_off = False

    def __del__(self):
        print('__del__ for %s' % self.__class__.__name__)

#    def finish(self):
#        """
#        """
#        if self.test_det_completed:
#            clean_work_space(self.dircalib, self.dirwork)

    def xtc_file_is_available(self):
        """- test that xtc file is available for epix100a"""
        data_exists()
        path_exists(self.fname_xtc)

    def det_raw(self):
        """- test det.raw(evt) for epix100a"""
        print('det_raw uses fname_xtc: %s' % self.fname_xtc)
        compare_det_raw(self.fname_xtc,\
	             detname='XppGon.0:Epix100a.1',\
	             expected='shape:(704, 768) size:540672 dtype:uint16 [3861 4050 3976 3992 3778...]')

    def det_calibrun(self):
        """- test command calibrun for epix100a"""
        if is_turned_off(self.turn_off): return
        fname_peds = '%s/Epix100a::CalibV1/XppGon.0:Epix100a.1/pedestals/137-end.data' % self.dircalib
        cmd = 'calibrun -e xppn4116 -r 137 -x %s -d EPIX100A -c %s -w work -P -D --nrecs1 2 -n 4 -m 4' % (self.fname_xtc, self.dircalib)
        #cmd = 'ls -l'
        #_stdout('\nsubmit in subprocess command:\n  %s\n' % cmd)
        print('submit in subprocess command:\n  %s\n' % cmd)
        err = subproc_in_log(cmd.split(), self.logname, shell=False)
        assert err == 'subprocess is completed', 'error message from subprocess: %s' % err
        #_stdout('\nresponce: %s' % err)
        print('\nresponce: %s\n' % err)
        assert os.path.exists(fname_peds)
        peds = np.loadtxt(fname_peds, dtype=np.float32)
        s = info_ndarr(peds)
        #_stdout('\npedestals: %s' % s)
        print('pedestals: %s\n' % s)
        assert s == 'shape:(704, 768) size:540672 dtype:float32 [3862.  4052.  3975.  3992.5 3776. ...]'

    def det_image(self):
        """- test det.image(evt) for epix100a"""
        if is_turned_off(self.turn_off): return
        fname = path_default_geometry(defname='geometry-def-epix100a.data')
        deploy_constants_from_file(fname, self.dircalib, cdtype='Epix100a::CalibV1/XppGon.0:Epix100a.1', ctype='geometry', cfname='0-end.data')
        ds = psana.DataSource(self.fname_xtc)
        det = psana.Detector('XppGon.0:Epix100a.1')
        evt = next(ds.events())

        print('ds.env().calibDir:', ds.env().calibDir())
        print(info_ndarr(det.raw(evt), name='raw', first=10000, last=10005))
        img = det.image(evt)
        s = info_ndarr(img, first=10000, last=10005)
        print('1-st event det.image: %s' % s.rstrip('\n'))

        assert s == 'shape:(709, 773) size:548057 dtype:float32 [-0.16992188 -0.6699219   2.8300781   1.3300781   0.        ...]'
        self.test_det_completed = True


class det_jungfrau():

    def __init__(self):
        """
        """
        print('__init__ for %s' % self.__class__.__name__)
        self.fname_xtc = path_to_xtc_test_file(fname='data-cxilx7422-r0101-3events-jungfrau4m.xtc')
        print('fname_xtc: %s' % self.fname_xtc)
        #print('\n\n======== %s' % self.__class__.__name__) ##.split('_')[-1])
        #self.dircalib = '/sdf/data/lcls/ds/cxi/cxilx7422/calib'
        #self.dircalib = './calib'
        self.dircalib = path_to_calibdir()
        self.dirwork = './work'
        self.logname = logname_prefix(self.dirwork, prefix='log-subproc-jungfrau')
        psana.setOption('psana.calib-dir', self.dircalib)
        self.test_det_completed = False
        self.turn_off = False

    def __del__(self):
        print('__del__ for %s' % self.__class__.__name__)

    def xtc_file_is_available(self):
        """- test that xtc file is available for jungfrau"""
        data_exists()
        path_exists(self.fname_xtc)

    def det_calib(self):
        """- test command calib.calib for jungfrau"""
        kwa={'mbits':0}
        dataset = 'exp=cxilx7422:run=101' # self.fname_xtc
        #pattern = 'shape:(8, 512, 1024) size:4194304 dtype:float32 [-0.07745222  0.36955786  0.00477444  0.02458291 -0.57804275...]'
        pattern = 'shape:(8, 512, 1024) size:4194304 dtype:float32 [-0.0747131   0.38151434  0.          0.02539831 -0.585139  ...]'
        compare_det_calib(dataset, detname='jungfrau4M', expected=pattern, **kwa)


epix100a = det_epix100a()
jungfrau = det_jungfrau()

""" pytest executes all methods with 'test' in the name
    WORKS FOR COMMAND: pytest Detector/test/pytest_detector.py"""

def test_epix100a_xtc_file_is_available():
    print(sys._getframe().f_code.co_name)
    epix100a.xtc_file_is_available()

def test_epix100a_raw():
    epix100a.det_raw()

def test_epix100a_calibrun():
    epix100a.det_calibrun()

def test_epix100a_image():
    epix100a.det_image()

def test_jungfrau_xtc_file_is_available():
    print(sys._getframe().f_code.co_name)
    jungfrau.xtc_file_is_available()

def test_jungfrau_calib():
    jungfrau.det_calib()


if __name__ == '__main__':
  """DEBUGGING, WORKS ONLY FOR COMMAND: python Detector/test/pytest_detector.py"""
  if False:
    test_epix100a_xtc_file_is_available()
    test_epix100a_raw()
    test_epix100a_calibrun()
    test_epix100a_image()
  if True:
    test_jungfrau_xtc_file_is_available()
    test_jungfrau_calib()

# EOF
