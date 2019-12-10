#--------------------------------------------------------------------------
"""
Class :py:class:`WFDetector` contains a collection of access methods to waveform detector data
==============================================================================================

Usage::

    # !!! NOTE: None is returned whenever requested information is missing.

    # import
    import psana
    from Detector.WFDetector import WFDetector    

    # retreive parameters from psana etc.
    dsname = 'exp=sxri0414:run=88'
    src = 'SxrEndstation.0:Acqiris.2' # or its alias 'acq02'

    ds  = psana.DataSource(dsname)
    env = ds.env()
    evt = ds.events().next()
    runnum = evt.run()

    # parameret par can be either runnum or evt    
    par = runnum
    # or
    par = evt

    det = WFDetector(src, env, pbits=0, iface='P') # iface='P' or 'C' - preferable low level interface (not used in this class)

    # set parameters, if changed
    det.set_env(env)
    det.set_source(source)
    det.set_print_bits(pbits)
 
    # print info
    det.print_attributes()    
    det.print_config(evt)

    instrument = det.instrument()

    # get array with waveforms
    wf = det.waveform(evt)

    # get array with waveform sample times
    wt = det.wftime(evt)

    #--------------------------- 
    # Detector-specific methods
    #---------------------------
    
    # access to Acqiris data
    det.set_correct_acqiris_time(correct_time=True) # (by default)
    wf, wt = det.raw(evt)
    # returns two np.array-s with shape = (nbrChannels, nbrSamples) for waveform and associated timestamps or (single) None.
    
    # access to Imp data
    det.set_calib_imp(do_calib_imp=True) # Imp calibration will subtract base level with changing dtype to np.int32
    wf = det.raw(evt)
    # returns numpy array with shape=(4, 1023) - samples for 4 channels or None if unavailable.

See classes
  - :py:class:`PyDetector` - factory for different detectors
  - :py:class:`PyDetectorAccess` - Python access interface to data
  - :py:class:`AreaDetector`  - access to area detector data
  - :py:class:`PyDetector` - factory for different detectors
  - :py:class:`WFDetector` - access waveform detector data ACQIRIS and IMP

This software was developed for the LCLS project.
If you use all or part of it, please give an appropriate acknowledgment.

Author Mikhail Dubrovin
"""
from __future__ import print_function
#------------------------------

import sys
import _psana
import numpy as np
import PSCalib.GlobalUtils as gu
from   Detector.PyDetectorAccess import PyDetectorAccess

##-----------------------------

class WFDetector :
    """Python access to wave-form detector data.
    """
##-----------------------------

    def __init__(self, src, env, pbits=0, iface='P') :
        """Parameters:
           src  [str]       - data source, ex: 'CxiDs2.0:Cspad.0'
           env  [psana.Env] - environment, ex: env=ds.env(), where ds=_psana.DataSource('exp=sxri0414:run=88')
           pbits[int]       - print control bit-word
           iface[char]      - preferable interface: 'C' - C++ (everything) or 'P' - Python based (not used in this class) 
        """
        #print 'In c-tor WFDetector'

        self.env     = env
        self.pbits   = pbits
        self.iscpp   = True if iface=='C' else False
        self.ispyt   = True if iface=='P' else False
        self.set_source(src, set_sub=False)
        self.dettype = gu.det_type_from_source(self.source)

        self.pyda = PyDetectorAccess(self.source, self.env, pbits) # Python data access methods
        #self.da   = Detector.DetectorAccess(self.source, self.env, pbit) # C++ access methods

        if self.pbits & 1 : self.print_members()

##-----------------------------

    def set_source(self, srcpar, set_sub=True) :
        """Accepts regular source or alias
        """
        #print 'type of srcpar: ', type(srcpar)
        
        src = srcpar if isinstance(srcpar, _psana.Source) else _psana.Source(srcpar)
        str_src = gu.string_from_source(src)

        # in case of alias convert it to _psana.Src
        amap = self.env.aliasMap()
        psasrc = amap.src(str_src)
        self.source  = src if amap.alias(psasrc) == '' else amap.src(str_src)

        if not isinstance(self.source, _psana.Source) : self.source = _psana.Source(self.source)

        if self.pbits & 16 :
            print('%s: input source: %s' % (self.__class__.__name__, src),\
                  '\n  string source: %s' % (str_src),\
                  '\n  source object: %s of type: %s' % (self.source, type(self.source)))

        if set_sub :
            self.pyda.set_source(self.source)

##-----------------------------

    def print_attributes(self) :
        print('%s object attributes:' % self.__class__.__name__, \
              '\n  source : %s' % self.source, \
              '\n  dettype: %d' % self.dettype, \
              '\n  detname: %s' % gu.dic_det_type_to_name[self.dettype], \
              '\n  pbits  : %d' % self.pbits, \
              '\n  iscpp  : %d' % self.iscpp, \
              '\n  ispyt  : %d' % self.ispyt)
        self.pyda.print_attributes()

##-----------------------------

    def set_print_bits(self, pbits) :
        self.pbits = pbits
        self.pyda.set_print_bits(pbits)
        #self.da.set_print_bits(pbits)

##-----------------------------

    def set_env(self, env) :
        self.env = env
        self.pyda.set_env(env)
        #self.da.set_env(env) # is not implemented and is not used this way

##-----------------------------

    def runnum(self, par) :
        """ Returns run number for parameter par which can be evt or runnum(int)
        """
        return par if isinstance(par, int) else par.run()

##-----------------------------

    def instrument(self) :
        return self.pyda.inst()

##-----------------------------

    def print_config(self, evt) :
        self.pyda.print_config(evt)

##-----------------------------

    def set_correct_acqiris_time(self, correct_time=True) :
        """On/off correction of time for acqiris
        """
        self.pyda.set_correct_acqiris_time(correct_time)

##-----------------------------

    def set_calib_imp(self, do_calib_imp=False) :
        """On/off imp calibration
        """
        self.pyda.set_calib_imp(do_calib_imp)

##-----------------------------

    def raw(self, evt) :
        """Returns np.array with raw data
        """
        return self.pyda.raw_data(evt, self.env)

##-----------------------------

    def waveform(self, evt) :
        """Returns np.array with waveforms
        """
        rdata = self.raw(evt)

        if self.dettype == gu.ACQIRIS :
            if rdata is None : return None
            wf, wt = rdata
            return wf

        elif self.dettype == gu.IMP :
            return rdata # returns np.array with shape=(4,1023) or None
        
        print('WARNING! %s: data for source %s is not found'%\
              (self.__class__.__name__, self.source))
        return None

##-----------------------------

    def wftime(self, evt) :
        """Returns np.array with waveform sample time
        """
        rdata = self.raw(evt)
        if rdata is None : return None

        if self.dettype == gu.ACQIRIS :
            wf, wt = rdata
            return wt

        elif self.dettype == gu.IMP :
            return range(rdata.shape[1]) # returns list of integer numbers from 0 to 1022 for wf shape=(4,1023)
        
        print('WARNING! %s: data for source %s is not found'%\
              (self.__class__.__name__, self.source))
        return None

##-----------------------------

    def __call__(self, evt) :
        """Alias for self.raw(evt)"""
        return self.raw(evt)

##-----------------------------

if __name__ == "__main__" :

    import psana
    from time import time
    from Detector.GlobalUtils import print_ndarr

    ntest = int(sys.argv[1]) if len(sys.argv)>1 else 1
    print('Test # %d' % ntest)

    dsname, src                = 'exp=sxri0414:run=88', psana.Source('DetInfo(acq02)')
    if ntest==2  : dsname, src = 'exp=sxri0414:run=88', psana.Source('DetInfo(SxrEndstation.0:Acqiris.2)')
    if ntest==3  : dsname, src = 'exp=cxii0215:run=49', psana.Source('DetInfo(CxiEndstation.0:Imp.1)')
    print('Example for\n  dataset: %s\n  source : %s' % (dsname, src))

    ds  = psana.DataSource(dsname)
    env = ds.env()
    cls = env.calibStore()
    eviter = ds.events()
    evt = eviter.next()
    rnum = evt.run()

    for key in evt.keys() : print(key)

    det = WFDetector(src, env, pbits=0)

    det.print_attributes()    
    det.print_config(evt)

    print('Instrument: %s' % det.instrument())
    print_ndarr(det.waveform(evt), 'test det.waveform(evt)')
    print_ndarr(det.wftime(evt), 'test det.wftime(evt)')

    data=None
    while data is None :
        t0_sec = time()
        data = det.raw(evt)
        print('\nConsumed time to get raw data (sec) =', time()-t0_sec)

 
    import pyimgalgos.GlobalGraphics as gg

    wf, wt = None, None

    if ntest<3 :
        wf, wt = data if data is not None else (None,None) 

        fig, ax = gg.plotGraph(wt[0,:-1], wf[0,:-1], figsize=(15,5))
        ax.plot(wt[1,:-1], wf[1,:-1], 'r-')
        ax.plot(wt[2,:-1], wf[2,:-1], 'g-')
        ax.plot(wt[3,:-1], wf[3,:-1], 'm-')

    if ntest==3 : 
        wf = data
        wt = range(wf.shape[1])

        fig, ax = gg.plotGraph(wt, wf[0], figsize=(15,5))
        ax.plot(wt, wf[1],'r-')
        ax.plot(wt, wf[2],'g-')
        ax.plot(wt, wf[3],'m-')

    print_ndarr(wf, 'wf')
    print_ndarr(wt, 'wt')

    print('wf:\n', wf)

    gg.show()

    sys.exit ('Self test is done')

##-----------------------------
