#--------------------------------------------------------------------------
# File and Version Information:
#  $Id$
#
# Description:
#  class PyDetector
#--------------------------------------------------------------------------
""" Class contains factory method create(...), returning instance of different detector data accessor 
    Method create(...) switches between classes depending on detector type defined from source.
    Currently implemented detector data access classes:
    \n :py:class:`Detector.AreaDetector` - access to area detector data
    \n :py:class:`Detector.WFDetector`  - access to waveform detector data

Usage::

    # !!! NOTE: None is returned whenever requested information is missing.

    # import
    import psana
    from Detector.PyDetector import PyDetector    

    # retreive parameters from psana etc.
    # source can be retreived from its full name
    src = psana.Source('DetInfo(CxiDs2.0:Cspad.0)')

    # or source contracted name
    src = psana.Source('CxiDs2.0:Cspad.0')

    # or source alias
    src = psana.Source('DsaCsPad')

    # dataset is specified by the experiment and run number
    ds  = psana.DataSource('exp=cxif5315:run=169')
    # extra parameters can be used to switch between data acess modes, ex.: ':idx', ':smd', etc.

    env = ds.env()
    evt = ds.events().next()
    runnum = evt.run()

    # parameret par can be either runnum or evt    
    par = runnum
    # or
    par = evt

    # create object using direct import:
    det = PyDetector(src, env, pbits=0)

    # or via psana namespace:
    det = psana.PyDetector(src, env, pbits=0)

    # Then use DETECTOR-SPECIFIC!!! methods defined in relevant class AreaDetector or WFDetector, for example 
    # AreaDetector has methods:
    nda = det.pedestals(par)
    ix, iy = det.indexes_xy(par)
    coords_x = det.coords_x(par)
    nda = det.raw(par)
    nda = det.calib(par)
    img = det.image(evt, nda)
    ...

    # WFDetector has methods:
    nda = det.raw(par)
    wf = det.waveform(par)
    wt = det.wftime(par)
    ...

This software was developed for the LCLS project.
If you use all or part of it, please give an appropriate acknowledgment.

@version $Id$

@author Mikhail S. Dubrovin
"""
#------------------------------
__version__ = "$Revision$"
##-----------------------------

import _psana
import PSCalib.GlobalUtils as gu
from Detector.AreaDetector import AreaDetector
from Detector.WFDetector import WFDetector

##-----------------------------

class DetectorFactory :
    """Python access to detector data.

    @see :py:class:`Detector.AreaDetector` - access to area detector data
    @see :py:class:`Detector.WFDetector` - access to waveform detector data
    """
##-----------------------------

    def __init__(self) :
        """Constructor
        """
        #print 'c-tor %s - make empty object' % self.__class__.__name__
        pass

##-----------------------------

    def create(self, src, env, pbits=0, iface='P') :
        """Returns instance of the class selected by dettype defined from src.
        @param src    - data source, ex: _psana.Source('DetInfo(CxiDs2.0:Cspad.0)')
        @param env    - environment, ex: env=ds.env(), where ds=_psana.DataSource('exp=cxif5315:run=169')
        @param pbits  - print control bit-word, ex: pbits=255 (for test purpose)
        @param iface  - preferable interface: 'C' - C++ or 'P' - Python based (for test purpose)
        """
        self.env = env
        self.pbits = pbits

        self._set_source(src, set_sub=False)
        self.dettype = gu.det_type_from_source(self.source)

        if self.pbits & 256 : print 'Initialization for %s' % gu.dic_det_type_to_name[self.dettype]

        if self.dettype == gu.ACQIRIS \
        or self.dettype == gu.IMP :
            return WFDetector(src, env, pbits, iface)

        else :
            return AreaDetector(src, env, pbits, iface)

##-----------------------------

    def _set_source(self, srcpar, set_sub=True) :
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
            print '%s: input source: %s' % (self.__class__.__name__, src),\
                  '\n  string source: %s' % (str_src),\
                  '\n  source object: %s of type: %s' % (self.source, type(self.source))

        #if set_sub :
        #    self.pyda.set_source(self.source)
        #    self.da.set_source(self.source)

##-----------------------------

PyDetector = DetectorFactory().create

##-----------------------------

if __name__ == "__main__" :

    import sys
    from time import time
    import psana

    ntest = int(sys.argv[1]) if len(sys.argv)>1 else 1
    print 'Test # %d' % ntest
    dsname, src                  = 'exp=cxif5315:run=169', psana.Source('DetInfo(CxiDs2.0:Cspad.0)')
    if   ntest==2  : dsname, src = 'exp=meca1113:run=376', psana.Source('DetInfo(MecTargetChamber.0:Cspad2x2.1)')
    elif ntest==3  : dsname, src = 'exp=amob5114:run=403', psana.Source('DetInfo(Camp.0:pnCCD.0)')
    elif ntest==4  : dsname, src = 'exp=xppi0614:run=74',  psana.Source('DetInfo(NoDetector.0:Epix100a.0)')
    elif ntest==5  : dsname, src = 'exp=sxri0414:run=88',  psana.Source('DetInfo(SxrEndstation.0:Acqiris.2)')
    elif ntest==6  : dsname, src = 'exp=cxii0215:run=49',  psana.Source('DetInfo(CxiEndstation.0:Imp.1)')
    print 'Example for\n  dataset: %s\n  source : %s' % (dsname, src)

    ds = psana.DataSource(dsname)
    env = ds.env()
    cls = env.calibStore()
    eviter = ds.events()
    evt = eviter.next()
    rnum = evt.run()

    for key in evt.keys() : print key

    det = PyDetector(src, env, pbits=0)

    try :
        nda = det.pedestals(rnum)
        print '\nnda:\n', nda
        print 'nda.dtype: %s nda.shape: %s' % (nda.dtype, nda.shape)
    except :
        print 'WARNING: det.pedestals(rnum) is not available for dataset: %s and source : %s' % (dsname, src) 

    try :
        t0_sec = time()
        nda = det.raw(evt)
        print '\nConsumed time to get raw data (sec) =', time()-t0_sec
        print 'nda:\n', nda.flatten()[0:10]
    except :
        print 'WARNING: det.raw(evt) is not available for dataset: %s and source : %s' % (dsname, src) 

    sys.exit ('Self test is done')

##-----------------------------
