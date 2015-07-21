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

Usage::

    # !!! None is returned everywhere when requested information is missing.

    import psana
    from Detector.PyDetector import PyDetector    

    dsname = 'exp=cxif5315:run=169'
    src = psana.Source('DetInfo(CxiDs2.0:Cspad.0)')

    ds  = psana.DataSource(dsname)
    env = ds.env()
    evt = ds.events().next()

    det = PyDetector(src, env, pbits=0)

    # set parameters, if changed
    det.set_env(env)
    det.set_source(source)
    det.set_print_bits(pbits)
    det.set_do_offset(do_offset=False)

    det.print_attributes()    
    det.print_config(evt)

    # get pixel array shape, size, and nomber of dimensions
    shape = det.shape(evt)
    size  = det.size(evt)
    ndim  = det.ndim(evt)
    instrument = det.instrument()

    # access intensity calibration parameters
    peds   = det.pedestals(evt)
    rms    = det.rms(evt)
    gain   = det.gain(evt)
    bkgd   = det.bkgd(evt)
    status = det.status(evt)
    stmask = det.status_as_mask(evt)
    mask   = det.mask_calib(evt)
    cmod   = det.common_mode(evt)

    # get raw data
    nda_raw = det.raw(evt)

    # get calibrated data (applied corrections: pedestals, pixel status mask, common mode)
    nda_cdata = det.calib(evt)

    # common mode correction for pedestal-subtracted numpy array nda:
    det.common_mode_apply(evt, nda)
    cm_corr_nda = det.common_mode_correction(self, evt, nda)

    # access geometry information
    coords_x   = det.coords_x(evt)
    coords_y   = det.coords_y(evt)
    coords_z   = det.coords_z(evt)
    areas      = det.areas(evt)
    mask_geo   = det.mask_geo(evt, mbits=15) # mbits = +1-edges; +2-wide central cols; +4-non-bound; +8-non-bound neighbours
    ind_x      = det.indexes_x(evt)
    ind_y      = det.indexes_y(evt)
    pixel_size = det.pixel_size(evt)

    # access to combined mask
    NOTE: by default none of mask keywords is set to True, returns None.
    mask = det.mask(evt, calib=False, status=False, edges=False, central=False, unbond=False, unbondnbrs=False)

    # reconstruct image
    img = det.image(evt) # uses calib(...) by default
    img = det.image(evt, img_nda)

    # access Acqiris data
    det.set_correct_acqiris_time(correct_time=True) # (by default)
    wf, wt = det.raw(evt)
    returns two np.array-s with shape = (nbrChannels, nbrSamples) for waveform and associated timestamps.
    

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
from Detector.PyDetectorAccess import PyDetectorAccess

##-----------------------------

def merge_masks(mask1=None, mask2=None) :
    """Merging masks using rule: (0,1,0,1)^(0,0,1,1) = (0,0,0,1) 
    """
    if mask1 is None : return mask2
    if mask2 is None : return mask1

    shape1 = mask1.shape
    shape2 = mask2.shape

    if shape1 != shape2 :
        if len(shape1) > len(shape2) : mask2.shape = shape1
        else                         : mask1.shape = shape2

    return np.logical_and(mask1, mask2)

##-----------------------------

class PyDetector :
    """Python access to detector data.

    Low level access is implemented on C++ through boost::python wrapper or direct python

    @see DetectorAccess - c++ access interface to data
    @see PyDetectorAccess - Python access interface to data
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

        self.da   = Detector.DetectorAccess(source, pbits) # , 0xffff) C++ access methods
        self.pyda = PyDetectorAccess(self.source, self.env, pbits) # Python data access methods

        if pbits : self.print_members()

##-----------------------------

    def print_members(self) :
        """Depricated method renamed to print_attributes() 
        """
        self.print_attributes()

##-----------------------------

    def print_attributes(self) :
        print 'PyDetector object attributes:', \
              '\n  source : %s' % self.source, \
              '\n  dettype: %d' % self.dettype, \
              '\n  detname: %s' % gu.det_name_from_type(self.dettype), \
              '\n  pbits  : %d\n' % self.pbits
        self.pyda.print_attributes()

##-----------------------------

    def set_print_bits(self, pbits) :
        self.da.set_print_bits(pbits)

##-----------------------------

    def set_env(self, env) :
        self.env    = env
        self.pyda.set_env(env)
        #self.da.set_env(env)

##-----------------------------

    def set_source(self, source) :
        self.source = source
        self.pyda.set_source(source)
        #self.da.set_source(source)

##-----------------------------

    def set_do_offset(self, do_offset=False) :
        """On/off application of offset in raw_data_camera(...)
        """
        self.pyda.set_do_offset(do_offset)

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

    def _shaped_array_(self, evt, arr, calibtype) :
        """ Returns shaped np.array if shape is defined and constants are loaded from file, None othervise.
        """
        if self.da.status(evt, self.env, calibtype) != gu.LOADED : return None
        if self.size(evt) > 0 : arr.shape = self.shape(evt)
        return arr

##-----------------------------

    def _nda_or_none_(self, nda) :
        """Returns  ndarray or None
        """
        return nda if nda.size else None

##-----------------------------

    def pedestals(self, evt) :
        return self._shaped_array_(evt, self.da.pedestals(evt, self.env), gu.PEDESTALS)

##-----------------------------

    def rms(self, evt) :
        return self._shaped_array_(evt, self.da.pixel_rms(evt, self.env), gu.PIXEL_RMS)

##-----------------------------

    def gain(self, evt) :
        return self._shaped_array_(evt, self.da.pixel_gain(evt, self.env), gu.PIXEL_GAIN)

##-----------------------------

    def mask_calib(self, evt) :
        return self._shaped_array_(evt, self.da.pixel_mask(evt, self.env), gu.PIXEL_MASK)

##-----------------------------

    def bkgd(self, evt) :
        return self._shaped_array_(evt, self.da.pixel_bkgd(evt, self.env), gu.PIXEL_BKGD)

##-----------------------------

    def status(self, evt) :
        return self._shaped_array_(evt, self.da.pixel_status(evt, self.env), gu.PIXEL_STATUS)

##-----------------------------

    def status_as_mask(self, evt) :
        """Returns 1/0 for status 0/>0.
        """
        stat = self.status(evt)
        if stat is None : return None
        return np.select([stat==0, stat>0], [1, 0])

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

    def raw_data(self, evt) :
        """Depricated method renamed to raw(evt) 
        """
        return self.raw(evt)

##-----------------------------

    def raw(self, evt) :
        """Returns np.array with raw data
        """
        # get data using python methods
        rdata = self.pyda.raw_data(evt, self.env)
        if rdata is not None : return rdata

        if self.pbits :
            print '!!! PyDetector: Data for source %s is not found in python interface, trying C++' % self.source,

        # get data using C++ methods
        if   self.dettype == gu.CSPAD    : rdata = self.da.data_int16_3 (evt, self.env)
        elif self.dettype == gu.CSPAD2X2 : rdata = self.da.data_int16_3 (evt, self.env)
        elif self.dettype == gu.PNCCD    : rdata = self.da.data_uint16_3(evt, self.env)
        else :                             rdata = self.da.data_uint16_2(evt, self.env)
        return self._nda_or_none_(rdata)

##-----------------------------

    def common_mode_apply(self, evt, nda) :
        """Apply common mode correction to nda (assuming that nda is data ndarray with subtracted pedestals)
           nda.dtype = np.float32 (or 64) is considered only, because common mode does not make sense for int data.
        """
        shape0 = nda.shape
        nda.shape = (nda.size,)
        if nda.dtype == np.float64 : self.da.common_mode_double(evt, self.env, nda)
        if nda.dtype == np.float32 : self.da.common_mode_float (evt, self.env, nda)
        nda.shape = shape0

##-----------------------------

    def common_mode_correction(self, evt, nda) :
        """ Returns ndarray with common mode correction offsets. Assumes that nda is data ndarray with subtracted pedestals. 
        """
        nda_cm_corr = np.array(nda, dtype=np.float32, copy=True)
        self.common_mode_apply(evt, nda)
        return nda_cm_corr - nda

##-----------------------------

    def calib_data(self, evt) :
        """Depricated method renamed to calib(evt) 
        """
        return self.calib(evt)

##-----------------------------

    def _print_warning(self, msg='') :
        print '\nWARNING! %s: %s' % (self.__class__.__name__, msg)

##-----------------------------

    def calib(self, evt) :
        """ Gets raw data ndarray, Applys baic corrections and return thus calibrated data.
            Applied corrections:
            - pedestal subtraction
            - apply mask generated from pixel status
            - apply common mode correction
        """

        raw = self.raw(evt) 
        if raw is None :
            if self.pbits & 32 : self._print_warning('calib(...) - raw data are missing.')
            return None

        peds  = self.pedestals(evt)
        if peds is None :
            if self.pbits & 32 : self._print_warning('calib(...) - pedestals are missing.')
            return None
        
        if raw.shape != peds.shape :
            if self.pbits & 32 :
                msg = 'calib(...) - raw.shape = %s is different from peds.shape = %s' \
                      % (str(raw.shape), str(peds.shape))
                self._print_warning(msg)
            return None

        cdata = np.array(raw, dtype=np.float32, copy=True)
        cdata -= peds

        smask = self.status_as_mask(evt)

        if smask is None :
            if self.pbits & 32 : self._print_warning('calib(...) - mask is missing.')
        else :
            cdata *= smask        

        self.common_mode_apply(evt, cdata)
        return cdata

        #nda_cmcorr = self.common_mode_correction(evt, cdata)
        #print 'nda_cmcorr[1:5] = ', nda_cmcorr.flatten()[1:5]
        #return nda_cmcorr

##-----------------------------

    def mask(self, evt, calib=False, status=False, edges=False, central=False, unbond=False, unbondnbrs=False) :
        """Returns combined mask
        """
        mask_nda = None
        if calib  : mask_nda = self.mask_calib(evt)
        if status : mask_nda = merge_masks(mask_nda, self.status_as_mask(evt)) 

        mbits = 0
        if edges      : mbits += 1
        if central    : mbits += 2
        if unbond     : mbits += 4
        if unbondnbrs : mbits += 8

        if mbits      : mask_nda = merge_masks(mask_nda, self.mask_geo(evt, mbits)) 
        return mask_nda

##-----------------------------
# Geometry info

    def coords_x(self, evt) :
        return self._nda_or_none_(self.da.pixel_coords_x(evt, self.env))

    def coords_y(self, evt) :
        return self._nda_or_none_(self.da.pixel_coords_y(evt, self.env))

    def coords_z(self, evt) :
        return self._nda_or_none_(self.da.pixel_coords_z(evt, self.env))

    def areas(self, evt) :
        return self._nda_or_none_(self.da.pixel_areas(evt, self.env))

    def mask_geo(self, evt, mbits=255) :
        return self._nda_or_none_(self.da.pixel_mask_geo(evt, self.env, mbits))

    def indexes_x(self, evt) :
        return self._nda_or_none_(self.da.pixel_indexes_x(evt, self.env))

    def indexes_y(self, evt) :
        return self._nda_or_none_(self.da.pixel_indexes_y(evt, self.env))

    def pixel_size(self, evt) :
        psize = self.da.pixel_scale_size(evt, self.env) # Ex: 109.92 [um]
        return psize if psize != 1 else None

    def image(self, evt, nda_in=None) :
        nda = nda_in if nda_in is not None else self.calib(evt)
        nda_img = np.array(nda, dtype=np.double).flatten()
        return self._nda_or_none_(self.da.get_image(evt, self.env, nda_img))
        
##-----------------------------

from time import time

if __name__ == "__main__" :

    ds, src = psana.DataSource('exp=cxif5315:run=169'), psana.Source('DetInfo(CxiDs2.0:Cspad.0)')
    #ds, src = psana.DataSource('exp=xcsi0112:run=15'),  psana.Source('DetInfo(XcsBeamline.0:Princeton.0)')

    env = ds.env()
    cls = env.calibStore()
    eviter = ds.events()
    evt = eviter.next()

    for key in evt.keys() : print key

    det = PyDetector(src, env, pbits=0)

    nda = det.pedestals(evt)
    print '\nnda:\n', nda
    print 'nda.dtype: %s nda.shape: %s' % (nda.dtype, nda.shape)

    t0_sec = time()
    nda = det.raw(evt)
    print '\nC++ consumed time to get raw data (sec) =', time()-t0_sec
    print '\nnda:\n', nda.flatten()[0:10]

    sys.exit ('Self test is done')

##-----------------------------
