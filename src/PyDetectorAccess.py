#--------------------------------------------------------------------------
# File and Version Information:
#  $Id$
#
# Description:
#  class PyDetectorAccess
#------------------------------------------------------------------------

"""Class contains a collection of direct python access methods to detector associated information.

Access method to calibration and geometry parameters, raw data, etc.
Low level implementation is done on python.

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

##-----------------------------

class PyDetectorAccess :
    """Direct python access to detector data.

    @see PyDetector
    @see DetectorAccess
    """

##-----------------------------

    def __init__(self, source, env, pbits=0) :
        """Constructor.
        @param source - data source, ex: psana.Source('DetInfo(CxiDs2.0:Cspad.0)')
        @param env    - environment
        @param pbits  - print control bit-word
        """

        #print 'In c-tor DetPyAccess'

        self.source = source
        self.env    = env
        self.pbits  = pbits
        #self.dettype = ImgAlgos::detectorTypeForSource(m_source);
        #self.cgroup  = ImgAlgos::calibGroupForDetType(m_dettype); // for ex: "PNCCD::CalibV1";

        self.da = Detector.DetectorAccess(source, pbits) # , 0xffff) C++ access methods

##-----------------------------

    def set_env(self, env) :
        self.env = env

##-----------------------------

    def pedestals(self, evt) :
        return None
        #return self.da.pedestals(evt, self.env)
    
##-----------------------------

    def pixel_rms(self, evt) :
        return None
        #return self.da.pixel_rms(evt, self.env)

##-----------------------------

    def pixel_gain(self, evt) :
        return None
        #return self.da.pixel_gain(evt, self.env)

##-----------------------------

    def pixel_mask(self, evt) :
        return None
        #return self.da.pixel_mask(evt, self.env)

##-----------------------------

    def pixel_bkgd(self, evt) :
        return None
        #return self.da.pixel_bkgd(evt, self.env)

##-----------------------------

    def pixel_status(self, evt) :
        return None
        #return self.da.pixel_status(evt, self.env)

##-----------------------------

    def common_mode(self, evt) :
        return None
        #return self.da.common_mode(evt, self.env)

##-----------------------------

    def inst(self) :
        return None
        #return self.da.inst(self.env)

##-----------------------------

    def print_config(self, evt) :
        pass
        #self.da.print_config(evt, self.env)

##-----------------------------

    def set_print_bits(self, pbits) :
        pass
        #self.da.set_print_bits(pbits)

##-----------------------------

    def raw_data(self, evt) :
        return None
        #return self.da.data_uint16_2(evt, self.env)

##-----------------------------

if __name__ == "__main__" :

    ds, src = psana.DataSource('exp=cxif5315:run=169'), psana.Source('DetInfo(CxiDs2.0:Cspad.0)')

    env = ds.env()
    cls = env.calibStore()
    itr = ds.events()
    evt = itr.next()

    for key in evt.keys() : print key

    det = PyDetectorAccess(src, env)

    det.set_print_bits(255)

    nda = det.pedestals(evt)
    print '\nnda:\n', nda
    print 'nda.dtype: %s nda.shape: %s' % (nda.dtype, nda.shape)


    #d = evt.get(psana.CsPad.DataV2, src)
    #print 'd.TypeId: ', d.TypeId

    #q0 = d.quads(0)
    #q0_data = q0.data()
    #print 'q0_data.shape: ', q0_data.shape

    sys.exit ('Self test is done')

##-----------------------------
