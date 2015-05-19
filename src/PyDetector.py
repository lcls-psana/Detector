#--------------------------------------------------------------------------
# File and Version Information:
#  $Id$
#
# Description:
#  class Detector
#
#------------------------------------------------------------------------

"""Class contains a collection of access methods to detector associated information.

Access method to calibration and geometry parameters, raw data, etc.
Low level implementation is done on C++ or python.

This software was developed for the LCLS project.
If you use all or part of it, please give an appropriate acknowledgment.

@version $Id$

@author Mikhail S. Dubrovin
"""
#------------------------------
__version__ = "$Revision$"
# $Source$
##-----------------------------

import sys
import psana
import Detector

##-----------------------------

class PyDetector :
    """Brief description of a class.

    Full description of this class.

    @see BaseClass
    @see OtherClass
    """

##-----------------------------

    def __init__(self, source, pbits=0) :
        """Constructor.
        @param source - data source, ex: psana.Source('DetInfo(CxiDs2.0:Cspad.0)')
        @param pbits  - print control bit-word
        """

        #print 'In c-tor DetPyAccess'

        self.source = source
        self.pbits = pbits
        #self.dettype = ImgAlgos::detectorTypeForSource(m_source);
        #self.cgroup  = ImgAlgos::calibGroupForDetType(m_dettype); // for ex: "PNCCD::CalibV1";

        self.da = Detector.DetectorAccess(source, pbits) # , 0xffff) C++ access methods

##-----------------------------

    def pedestals(self, evt, env) :
        print 'In pedestals'
        return self.da.pedestals(evt,env)

##-----------------------------

    def pixel_rms(self, evt, env) :
        return self.da.pixel_rms(evt,env)

##-----------------------------

    def pixel_gain(self, evt, env) :
        return self.da.pixel_gain(evt,env)

##-----------------------------

    def pixel_mask(self, evt, env) :
        return self.da.pixel_mask(evt,env)

##-----------------------------

    def pixel_bkgd(self, evt, env) :
        return self.da.pixel_bkgd(evt,env)

##-----------------------------

    def pixel_status(self, evt, env) :
        return self.da.pixel_status(evt,env)

##-----------------------------

    def common_mode(self, evt, env) :
        return self.da.common_mode(evt,env)

##-----------------------------

    def inst(self, env) :
        return self.da.inst(env)

##-----------------------------

    def print_config(self, evt, env) :
        self.da.print_config(evt,env)

##-----------------------------

    def set_print_bits(self, pbits) :
        self.da.set_print_bits(pbits)

##-----------------------------

    def raw_data(self, evt, env) :
        return self.da.data_uint16_2(evt,env)

##-----------------------------

if __name__ == "__main__" :

    ds = psana.DataSource('exp=cxif5315:run=169')

    env = ds.env()
    cls = env.calibStore()
    eviter = ds.events()
    evt = eviter.next()

    for key in evt.keys() : print key

    src = psana.Source('DetInfo(CxiDs2.0:Cspad.0)')
    #src = psana.Source('DetInfo(CxiDs2.0:Cspad.0)')

    det = PyDetector(src)

    det.set_print_bits(255)

    nda = det.pedestals(evt,env)
    print '\nnda:\n', nda
    print 'nda.dtype: %s nda.shape: %s' % (nda.dtype, nda.shape)


    #d = evt.get(psana.CsPad.DataV2, src)
    #print 'd.TypeId: ', d.TypeId

    #q0 = d.quads(0)
    #q0_data = q0.data()
    #print 'q0_data.shape: ', q0_data.shape

    sys.exit ('Self test is done')

##-----------------------------
