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
import numpy as np
import Detector.GlobalUtils as gu

##-----------------------------

class PyDetector :
    """Python access to detector data.

    Low level access is implemented on C++ through boost::python wrapper or direct python

    @see DetectorAccess
    @see PyDetectorAccess
    """

##-----------------------------

    def __init__(self, source, env, pbits=0) :
        """Constructor.
        @param source - data source, ex: psana.Source('DetInfo(CxiDs2.0:Cspad.0)')
        @param pbits  - print control bit-word
        """

        #print 'In c-tor DetPyAccess'

        self.source  = source
        self.dettype = gu.det_type_from_source(source)
        self.env     = env
        self.pbits   = pbits
        #self.dettype = ImgAlgos::detectorTypeForSource(m_source);
        #self.cgroup  = ImgAlgos::calibGroupForDetType(m_dettype); // for ex: "PNCCD::CalibV1";

        self.da = Detector.DetectorAccess(source, pbits) # , 0xffff) C++ access methods

        if pbits : self.print_members()

##-----------------------------

    def print_members(self) :
        print 'Members of the class: PyDetector', \
              '\n  source : %s' % self.source, \
              '\n  dettype: %d' % self.dettype, \
              '\n  detname: %s' % gu.det_name_from_type(self.dettype), \
              '\n  pbits  : %d\n' % self.pbits

##-----------------------------

    def set_env(self, env) :
        self.env    = env

##-----------------------------

    def ndim(self, evt) :
        """ Returns ndarray number of dimensions. If ndim>3 then returns 3.
        """
        nd = self.da.ndim(evt, self.env)
        return nd if nd<4 else 3

##-----------------------------

    def size(self, evt) :
        return self.da.size(evt, self.env)

##-----------------------------

    def shape(self, evt) :
        """ Returns ndarray shape. If ndim>3 shape is reduced to 3-d.
            Example: the shepe like [4,8,185,388] is reduced to [32,185,388]
        """
        sh = self.da.shape(evt, self.env)
        return sh if len(sh)<4 else np.array((self.size(evt)/sh[-1]/sh[-2], sh[-2], sh[-1]))

##-----------------------------

    def shaped_array(self, evt, arr, calibtype) :
        """ Returns shaped np.array if shape is defined and constants are loaded from file, None othervise.
        """
        if self.da.status(evt, self.env, calibtype) != gu.LOADED : return None
        if self.size(evt) > 0 : arr.shape = self.shape(evt)
        return arr

##-----------------------------

    def pedestals(self, evt) :
        return self.shaped_array(evt, self.da.pedestals(evt, self.env), gu.PEDESTALS)

##-----------------------------

    def rms(self, evt) :
        return self.shaped_array(evt, self.da.pixel_rms(evt, self.env), gu.PIXEL_RMS)

##-----------------------------

    def gain(self, evt) :
        return self.shaped_array(evt, self.da.pixel_gain(evt, self.env), gu.PIXEL_GAIN)

##-----------------------------

    def mask(self, evt) :
        return self.shaped_array(evt, self.da.pixel_mask(evt, self.env), gu.PIXEL_MASK)

##-----------------------------

    def bkgd(self, evt) :
        return self.shaped_array(evt, self.da.pixel_bkgd(evt, self.env), gu.PIXEL_BKGD)

##-----------------------------

    def status(self, evt) :
        return self.shaped_array(evt, self.da.pixel_status(evt, self.env), gu.PIXEL_STATUS)

##-----------------------------

    def common_mode(self, evt) :
        return self.da.common_mode(evt, self.env)

##-----------------------------

    def instrument(self) :
        return self.da.instrument(self.env)

##-----------------------------

    def print_config(self, evt) :
        self.da.print_config(evt, self.env)

##-----------------------------

    def set_print_bits(self, pbits) :
        self.da.set_print_bits(pbits)

##-----------------------------

    def raw_data(self, evt) :

        rdata = None
        if self.dettype == gu.CSPAD \
        or self.dettype == gu.CSPAD2X2 : rdata = self.da.data_int16_3 (evt, self.env)
        elif self.dettype == gu.PNCCD  : rdata = self.da.data_uint16_3(evt, self.env)
        else :                           rdata = self.da.data_uint16_2(evt, self.env)

        return rdata if rdata.size else None

##-----------------------------
# Geometry info

    def coords_x(self, evt) :
        nda = self.da.pixel_coords_x(evt, self.env)
        return nda if nda.size else None

    def coords_y(self, evt) :
        nda = self.da.pixel_coords_y(evt, self.env)
        return nda if nda.size else None

    def coords_z(self, evt) :
        nda = self.da.pixel_coords_z(evt, self.env)
        return nda if nda.size else None

    def area(self, evt) :
        nda = self.da.pixel_area(evt, self.env)
        return nda if nda.size else None

    def mask(self, evt) :
        nda = self.da.pixel_mask(evt, self.env)
        return nda if nda.size else None

    def indexes_x(self, evt) :
        nda = self.da.pixel_indexes_x(evt, self.env)
        return nda if nda.size else None

    def indexes_y(self, evt) :
        nda = self.da.pixel_indexes_y(evt, self.env)
        return nda if nda.size else None

    def pixel_size(self, evt) :
        psize = self.da.pixel_scale_size(evt, self.env) # Ex: 109.92 [um]
        return psize if psize != 1 else None

    def image(self, evt, nda) :
        if nda is None : return None
        nda_img = np.array(nda, dtype=np.double).flatten()
        img = self.da.get_image(evt, self.env, nda_img)
        return img if img.size else None
        

##-----------------------------

if __name__ == "__main__" :

    ds, src = psana.DataSource('exp=cxif5315:run=169'), psana.Source('DetInfo(CxiDs2.0:Cspad.0)')

    env = ds.env()
    cls = env.calibStore()
    eviter = ds.events()
    evt = eviter.next()

    for key in evt.keys() : print key

    det = PyDetector(src, env, pbits=0)

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
