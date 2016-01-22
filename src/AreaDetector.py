#--------------------------------------------------------------------------
# File and Version Information:
#  $Id$
#
# Description:
#  class AreaDetector
#--------------------------------------------------------------------------
""" Class contains a collection of access methods to detector data and meta-data.

Access method to calibration and geometry parameters, raw data, etc.
Low level implementation is done on C++ or python.

Usage::

    # !!! NOTE: None is returned whenever requested information is missing.

    # import
    import psana

    # retreive parameters from psana etc.
    dsname = 'exp=xpptut15:run=54'
    src = 'XppGon.0:Cspad.0' # or its alias 'cspad'

    ds  = psana.DataSource(dsname)
    env = ds.env()
    evt = ds.events().next()
    runnum = evt.run()

    # parameter par can be either runnum or evt    
    par = runnum # or = evt
    cmpars=(1,25,10,91) # custom tuple of common mode parameters

    det = psana.Detector(src, env, pbits=0, iface='P') # iface='P' or 'C' - preferable low level interface (for test perp.)

    # or directly
    from Detector.AreaDetector import AreaDetector    
    det = AreaDetector(src, env, pbits=0, iface='P')

    # set parameters, if changed
    det.set_env(env)
    det.set_source(source)
    det.set_print_bits(pbits)
    det.set_do_offset(do_offset=False) # NOTE: should be called right after det object is created, before getting data

    # print info
    det.print_attributes()    
    det.print_config(evt)

    # get pixel array shape, size, and nomber of dimensions
    shape = det.shape(par)
    size  = det.size(par)
    ndim  = det.ndim(par)
    instrument = det.instrument()

    # access intensity calibration parameters
    peds   = det.pedestals(par)
    rms    = det.rms(par)
    gain   = det.gain(par)
    bkgd   = det.bkgd(par)
    status = det.status(par)
    stmask = det.status_as_mask(par)
    mask   = det.mask_calib(par)
    cmod   = det.common_mode(par)

    # per-pixel gain mask from configuration data; 1/0 for low/high gain pixels
    gmap = det.gain_mask() # gain=6.789 - optional parameter 

    # get raw data
    nda_raw = det.raw(evt)

    # get calibrated data (applied corrections: pedestals, pixel status mask, common mode)
    nda_cdata = det.calib(evt)
    # or with custom common mode parameter sequence
    nda_cdata = det.calib(evt, cmpars=(1,25,10,91)) # see description of common mode algorithms in confluence

    # common mode correction for pedestal-subtracted numpy array nda:
    det.common_mode_apply(par, nda)
    cm_corr_nda = det.common_mode_correction(par, nda)
    # or with custom common mode parameter sequence
    det.common_mode_apply(par, nda, cmpars)
    cm_corr_nda = det.common_mode_correction(par, nda, cmpars)

    # access geometry information
    geo        = det.geometry(par)
    coords_x   = det.coords_x(par)
    coords_y   = det.coords_y(par)
    coords_z   = det.coords_z(par)
    areas      = det.areas(par)
    mask_geo   = det.mask_geo(par, mbits=15) # mbits = +1-edges; +2-wide central cols; +4-non-bound; +8-non-bound neighbours
    ix         = det.indexes_x(par)
    iy         = det.indexes_y(par)
    ix, iy     = det.indexes_xy(par)
    pixel_size = det.pixel_size(par)

    # change geometry object parameters
    det.move_geo(par, dx, dy, dz)    # move detector it 3-d space
    det.tilt_geo(par, dtx, dty, dtz) # tilt detector around 3 axes

    # access to combined mask
    # NOTE: by default none of mask keywords is set to True, returns None.
    mask = det.mask(par, calib=False, status=False, edges=False, central=False, unbond=False, unbondnbrs=False)

    # reconstruct image
    img = det.image(evt) # uses calib() by default
    img = det.image(evt, img_nda)
    img = det(evt, img_nda) # alias for det.image(evt, img_nda)

    # special case of indexing using non-default pixel scale size and x, y coordinate offset
    ix     = det.indexes_x(par, pix_scale_size_um=110, xy0_off_pix=(1000,1000))
    iy     = det.indexes_y(par, pix_scale_size_um=None, xy0_off_pix=None)
    ix, iy = det.indexes_xy(par, pix_scale_size_um=None, xy0_off_pix=None)
    img    = det.image(evt, img_nda, pix_scale_size_um=None, xy0_off_pix=None)

@see classes
\n  :py:class:`Detector.PyDetector` - factory for different detectors
\n  :py:class:`Detector.DetectorAccess` - c++ access interface to data
\n  :py:class:`Detector.PyDetectorAccess` - Python access interface to data
\n  :py:class:`Detector.WFDetector` - access waveform detector data ACQIRIS and IMP

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
import _psana
import Detector
import numpy as np
import PSCalib.GlobalUtils as gu
from   PSCalib.GeometryObject import data2x2ToTwo2x1, two2x1ToData2x2
from   Detector.PyDetectorAccess import PyDetectorAccess

##-----------------------------

class AreaDetector(object):
    """Python access to area detector data.
       Low level access is implemented on python or C++ through the boost::python wrapper
    """

##-----------------------------

    def __init__(self, src, env, pbits=0, iface='P') :
        """Parameters:
           src   [str]       - data source, ex: 'CxiDs2.0:Cspad.0'
           env   [psana.Env] - environment, ex: env=ds.env(), where ds=_psana.DataSource('exp=cxif5315:run=169')
           pbits [int]       - print control bit-word
           iface [char]      - preferable interface: 'C' - C++ (everything) or 'P' - Python based (everything except common mode) 
        """
        #print 'In c-tor AreaDetector'

        self.env     = env
        self.pbits   = pbits
        self.iscpp   = True if iface=='C' else False
        self.ispyt   = True if iface=='P' else False
        self.set_source(src, set_sub=False)
        self.dettype = gu.det_type_from_source(self.source)

        self.da   = Detector.DetectorAccess(self.source, self.env, pbits) # , 0xffff) C++ access methods
        self.pyda = PyDetectorAccess(self.source, self.env, pbits) # Python data access methods

        self._shape = None
        self._size  = None
        self._ndim  = None

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
            print '%s: input source: %s' % (self.__class__.__name__, src),\
                  '\n  string source: %s' % (str_src),\
                  '\n  source object: %s of type: %s' % (self.source, type(self.source))

        if set_sub :
            self.pyda.set_source(self.source)
            self.da.set_source(self.source)

##-----------------------------

    def print_members(self) :
        """Depricated method renamed to print_attributes() 
        """
        self.print_attributes()

##-----------------------------

    def print_attributes(self) :
        print 'AreaDetector object attributes:', \
              '\n  source : %s' % self.source, \
              '\n  dettype: %d' % self.dettype, \
              '\n  detname: %s' % gu.dic_det_type_to_name[self.dettype], \
              '\n  pbits  : %d' % self.pbits, \
              '\n  iscpp  : %d' % self.iscpp, \
              '\n  ispyt  : %d' % self.ispyt
        if self.iscpp : self.da.print_members()
        else          : self.pyda.print_attributes()

##-----------------------------

    def set_print_bits(self, pbits) :
        self.pbits = pbits
        self.da.set_print_bits(pbits)
        self.pyda.set_print_bits(pbits)

##-----------------------------

    def set_env(self, env) :
        self.env = env
        self.pyda.set_env(env)
        #self.da.set_env(env) # is not implemented and is not used this way

##-----------------------------

    def set_do_offset(self, do_offset=False) :
        """On/off application of offset in raw_data_camera(...)
        """
        self.pyda.set_do_offset(do_offset)
        self.da.setMode(0 if do_offset else 1)

##-----------------------------

    def runnum(self, par) :
        """ Returns run number for parameter par which can be evt or runnum(int)
        """
        return par if isinstance(par, int) else par.run()

##-----------------------------

    def is_cspad2x2(self) :
        if self.dettype == gu.CSPAD2X2 :
            #print 'Ma, look, it is cspad2x2!'
            return True
        else :
            return False
        #if arr is not None and arr.size == 143560 : return True

##-----------------------------

    def ndim(self, par) : # par = evt or runnum(int)
        """ Returns ndarray number of dimensions. If ndim>3 then returns 3.
        """
        if self._ndim is None :
            rnum = self.runnum(par)
            nd = self.da.ndim_v0(rnum) if self.iscpp else self.pyda.ndim(rnum)
            self._ndim = nd if nd<4 else 3
        return self._ndim

##-----------------------------

    def size(self, par) :
        if self._size is None :
            rnum = self.runnum(par)
            self._size = self.da.size_v0(rnum) if self.iscpp else self.pyda.size(rnum)
        return self._size
    
##-----------------------------

    def shape(self, par) :
        """ Returns ndarray with NATURAL shape.
        """        
        return np.array((2,185,388)) if self.is_cspad2x2() else self._shape_daq_(par)

##-----------------------------

    def _shape_daq_(self, par) :
        """ Returns ndarray shape. If ndim>3 shape is reduced to 3-d.
            Example: the shepe like [4,8,185,388] is reduced to [32,185,388]
        """
        if self._shape is None :
            rnum = self.runnum(par)
            sh = self.da.shape_v0(rnum) if self.iscpp else self.pyda.shape(rnum)
            self._shape = sh if len(sh)<4 else np.array((self.size(rnum)/sh[-1]/sh[-2], sh[-2], sh[-1]))
        return self._shape        

##-----------------------------

    def loading_status(self, rnum, calibtype=None) :
        """ Returns loading status of calibration constant gu.LOADED, DEFAULT, etc.
        """
        if self.iscpp : return self.da.status_v0(rnum, calibtype)
        else          : return self.pyda.status(rnum, calibtype)
        
##-----------------------------

    def _shaped_array_(self, rnum, arr, calibtype=None) :
        """ Returns shaped numpy.array if shape is defined and constants are loaded from file, None othervise.
        """
        if arr is None   : return None
        if arr.size == 0 : return None
        if calibtype is not None :
            status = self.loading_status(rnum, calibtype)
            if status != gu.LOADED and status != gu.DEFAULT : return None
        if self.size(rnum) : arr.shape = self._shape_daq_(rnum)
        return arr if not self.is_cspad2x2() else data2x2ToTwo2x1(arr)

##-----------------------------

    def _nda_or_none_(self, nda) :
        """Returns  ndarray or None
        """
        if nda is None : return None
        return nda if nda.size else None

##-----------------------------

    def pedestals(self, par) :
        rnum = self.runnum(par)
        if self.iscpp : return self._shaped_array_(rnum, self.da.pedestals_v0(rnum), gu.PEDESTALS)
        else          : return self._shaped_array_(rnum, self.pyda.pedestals(rnum),  gu.PEDESTALS)

##-----------------------------

    def rms(self, par) :
        rnum = self.runnum(par)
        if self.iscpp : return self._shaped_array_(rnum, self.da.pixel_rms_v0(rnum), gu.PIXEL_RMS)
        else          : return self._shaped_array_(rnum, self.pyda.pixel_rms(rnum),  gu.PIXEL_RMS)

##-----------------------------

    def gain(self, par) :
        rnum = self.runnum(par)
        if self.iscpp : return self._shaped_array_(rnum, self.da.pixel_gain_v0(rnum), gu.PIXEL_GAIN)
        else          : return self._shaped_array_(rnum, self.pyda.pixel_gain(rnum),  gu.PIXEL_GAIN)

##-----------------------------

    def mask_calib(self, par) :
        rnum = self.runnum(par)
        if self.iscpp : return self._shaped_array_(rnum, self.da.pixel_mask_v0(rnum), gu.PIXEL_MASK)
        else          : return self._shaped_array_(rnum, self.pyda.pixel_mask(rnum),  gu.PIXEL_MASK)

##-----------------------------

    def bkgd(self, par) :
        rnum = self.runnum(par)
        if self.iscpp : return self._shaped_array_(rnum, self.da.pixel_bkgd_v0(rnum), gu.PIXEL_BKGD)
        else          : return self._shaped_array_(rnum, self.pyda.pixel_bkgd(rnum),  gu.PIXEL_BKGD)

##-----------------------------

    def status(self, par) :
        rnum = self.runnum(par)
        if self.iscpp : return self._shaped_array_(rnum, self.da.pixel_status_v0(rnum), gu.PIXEL_STATUS)
        else          : return self._shaped_array_(rnum, self.pyda.pixel_status(rnum),  gu.PIXEL_STATUS)

##-----------------------------

    def status_as_mask(self, par) :
        """Returns 1/0 for status 0/>0.
        """
        rnum = self.runnum(par)
        stat = self.status(rnum)
        if stat is None : return None
        smask = np.select([stat==0, stat>0], [1, 0])
        if self.is_cspad2x2() : return smask # stat already has a shape (2,185,388)
        return self._shaped_array_(rnum, smask, gu.PIXEL_STATUS)

##-----------------------------

    def gain_mask(self, gain=None) :
        """Returns pixel gain mask evaluated from detector configuration.
        """
        return self.pyda.gain_mask(gain)

##-----------------------------

    def common_mode(self, par) :
        rnum = self.runnum(par)
        if self.iscpp : return self.da.common_mode_v0(rnum)
        else          : return self.pyda.common_mode(rnum)

##-----------------------------

    def instrument(self) :
        if self.iscpp : return self.da.instrument(self.env)
        else          : return self.pyda.inst()

##-----------------------------

    def print_config(self, evt) :
        if self.iscpp : self.da.print_config(evt, self.env)
        else          : self.pyda.print_config(evt)

##-----------------------------

    def raw_data(self, evt) :
        """Alias for depricated method renamed to raw(evt) 
        """
        return self.raw(evt)

##-----------------------------

    def raw(self, evt) :
        """Returns np.array with raw data
        """
        # get data using python methods
        rnum = self.runnum(evt)
        rdata = self.pyda.raw_data(evt, self.env)

        #if self.dettype == gu.ACQIRIS : return rdata # returns two arrays: wf, wt
        #if self.dettype == gu.IMP :     return rdata # returns nparray with shape=(4,1023)
        
        if rdata is not None : return self._shaped_array_(rnum, rdata)

        if self.pbits :
            print '!!! AreaDetector: Data for source %s is not found in python interface, trying C++' % self.source

        # get data using C++ methods
        if   self.dettype == gu.CSPAD    : rdata = self.da.data_int16_3 (evt, self.env)
        elif self.dettype == gu.CSPAD2X2 : rdata = self.da.data_int16_3 (evt, self.env)
        elif self.dettype == gu.PNCCD    : rdata = self.da.data_uint16_3(evt, self.env)
        else :                             rdata = self.da.data_uint16_2(evt, self.env)
        if self.pbits and rdata is None :
            print '!!! AreaDetector: Data for source %s is not found in C++ interface' % self.source
        return self._shaped_array_(rnum, rdata)

##-----------------------------

    def common_mode_apply(self, par, nda, cmpars=None) :
        """Apply common mode correction to nda (assuming that nda is data ndarray with subtracted pedestals)
           nda.dtype = np.float32 (or 64) is considered only, because common mode does not make sense for int data.
           If cmpars is not None then this sequence is used to override default common mode parameters coming from
           calib/.../common_mode/...
        """
        rnum = self.runnum(par)
        shape0 = nda.shape
        nda.shape = (nda.size,)
        if cmpars is not None: self.da.set_cmod_pars(rnum, np.array(cmpars, dtype=np.float64))
        if nda.dtype == np.float64 : self.da.common_mode_double_v0(rnum, nda)
        if nda.dtype == np.float32 : self.da.common_mode_float_v0 (rnum, nda)
        nda.shape = shape0

##-----------------------------

    def common_mode_correction(self, par, nda, cmpars=None) :
        """ Returns ndarray with common mode correction offsets. Assumes that nda is data ndarray with subtracted pedestals. 
        """
        nda_cm_corr = np.array(nda, dtype=np.float32, copy=True)
        self.common_mode_apply(self.runnum(par), nda, cmpars)
        return nda_cm_corr - nda

##-----------------------------

    def calib_data(self, evt) :
        """Alias of depricated method renamed to calib(evt) 
        """
        return self.calib(evt)

##-----------------------------

    def _print_warning(self, msg='') :
        print '\nWARNING! %s: %s' % (self.__class__.__name__, msg)

##-----------------------------

    def calib(self, evt, cmpars=None) :
        """ Gets raw data ndarray, Applys baic corrections and return thus calibrated data.
            Applied corrections:
            - pedestal subtraction
            - apply mask generated from pixel status
            - apply common mode correction
        """
        rnum = self.runnum(evt)

        raw = self.raw(evt) 
        if raw is None :
            if self.pbits & 32 : self._print_warning('calib(...) - raw data are missing.')
            return None

        peds  = self.pedestals(rnum)
        if peds is None :
            if self.pbits & 32 : self._print_warning('calib(...) - pedestals are missing.')
            return None
        
        if raw.shape != peds.shape :
            if self.pbits & 32 :
                msg = 'calib(...) - raw.shape = %s is different from peds.shape = %s. Try reshaping to data...' \
                      % (str(raw.shape), str(peds.shape))
                self._print_warning(msg)
            try    : peds.shape = raw.shape
            except : return None

        cdata = np.array(raw, dtype=np.float32, copy=True)
        cdata -= peds  # for cspad2x2 (2, 185, 388)

        if self.is_cspad2x2() : cdata = two2x1ToData2x2(cdata) # convert to DAQ shape for cspad2x2 ->(185, 388, 2)
        self.common_mode_apply(rnum, cdata, cmpars)
        if self.is_cspad2x2() : cdata = data2x2ToTwo2x1(cdata) # convert to Natural shape for cspad2x2 ->(2, 185, 388)

        smask = self.status_as_mask(rnum) # (2, 185, 388)
        if smask is None :
            if self.pbits & 32 : self._print_warning('calib(...) - mask is missing.')
        else :
            smask.shape = cdata.shape
            cdata *= smask      

        return cdata 

##-----------------------------

    def mask(self, par, calib=False, status=False, edges=False, central=False, unbond=False, unbondnbrs=False) :
        """Returns combined mask
        """
        rnum = self.runnum(par)

        mask_nda = None
        if calib  : mask_nda = self.mask_calib(rnum)
        if status : mask_nda = gu.merge_masks(mask_nda, self.status_as_mask(rnum)) 

        mbits = 0
        if edges      : mbits += 1
        if central    : mbits += 2
        if unbond     : mbits += 4
        if unbondnbrs : mbits += 8

        if mbits      : mask_nda = gu.merge_masks(mask_nda, self.mask_geo(rnum, mbits)) 
        return mask_nda

##-----------------------------
# Geometry info

    def geometry(self, par) :
        rnum = self.runnum(par)
        return self.pyda.geoaccess(rnum) 

    def coords_x(self, par) :
        rnum = self.runnum(par)
        if self.iscpp : return self._shaped_array_(rnum, self.da.pixel_coords_x_v0(rnum))
        else          : return self._shaped_array_(rnum, self.pyda.coords_x(rnum)) 
    
    def coords_y(self, par) :
        rnum = self.runnum(par)
        if self.iscpp : return self._shaped_array_(rnum, self.da.pixel_coords_y_v0(rnum))
        else          : return self._shaped_array_(rnum, self.pyda.coords_y(rnum)) 

    def coords_z(self, par) :
        rnum = self.runnum(par)
        if self.iscpp : return self._shaped_array_(rnum, self.da.pixel_coords_z_v0(rnum))
        else          : return self._shaped_array_(rnum, self.pyda.coords_z(rnum)) 

    def areas(self, par) :
        rnum = self.runnum(par)
        if self.iscpp : return self._shaped_array_(rnum, self.da.pixel_areas_v0(rnum))
        else          : return self._shaped_array_(rnum, self.pyda.areas(rnum)) 

    def mask_geo(self, par, mbits=255) :
        rnum = self.runnum(par)
        if self.iscpp : return self._shaped_array_(rnum, self.da.pixel_mask_geo_v0(rnum, mbits))
        else          : return self._shaped_array_(rnum, self.pyda.mask_geo(rnum, mbits))

    def indexes_x(self, par, pix_scale_size_um=None, xy0_off_pix=None, do_update=False) :
        rnum = self.runnum(par)
        if self.iscpp : return self._shaped_array_(rnum, self.da.pixel_indexes_x_v0(rnum))
        else          : return self._shaped_array_(rnum, self.pyda.indexes_x(rnum, pix_scale_size_um, xy0_off_pix, do_update))

    def indexes_y(self, par, pix_scale_size_um=None, xy0_off_pix=None, do_update=False) :
        rnum = self.runnum(par)
        if self.iscpp : return self._shaped_array_(rnum, self.da.pixel_indexes_y_v0(rnum))
        else          : return self._shaped_array_(rnum, self.pyda.indexes_y(rnum, pix_scale_size_um, xy0_off_pix, do_update))

    def indexes_xy(self, par, pix_scale_size_um=None, xy0_off_pix=None, do_update=False) :
        rnum = self.runnum(par)
        iX, iY = self.pyda.indexes_xy(rnum, pix_scale_size_um, xy0_off_pix, do_update)
        return self._shaped_array_(rnum, iX), self._shaped_array_(rnum, iY)

    def pixel_size(self, par) :
        rnum = self.runnum(par)
        psize = self.da.pixel_scale_size_v0(rnum) if self.iscpp else self.pyda.pixel_size(rnum) # Ex: 109.92 [um]
        return psize if psize != 1 else None

    def move_geo(self, par, dx, dy, dz) :
        rnum = self.runnum(par)
        self.pyda.move_geo(par, dx, dy, dz)

    def tilt_geo(self, par, dtx, dty, dtz) :
        rnum = self.runnum(par)
        self.pyda.tilt_geo(par, dtx, dty, dtz)

    def image(self, evt, nda_in=None, pix_scale_size_um=None, xy0_off_pix=None, do_update=False) :
        rnum = self.runnum(evt)
        nda = nda_in if nda_in is not None else self.calib(evt)
        if self.is_cspad2x2() : nda = two2x1ToData2x2(nda) # convert to DAQ shape for cspad2x2
        if nda is None : return None
        nda_img = np.array(nda, dtype=np.double).flatten()        
        if self.iscpp : return self._nda_or_none_(self.da.get_image_v0(rnum, nda_img))
        else          : return self._nda_or_none_(self.pyda.image(rnum, nda_img, pix_scale_size_um, xy0_off_pix, do_update))

    def __call__(self, evt, nda_in=None) :
        """Alias for image in order to call it as det(evt,...)"""
        return self.image(evt, nda_in)

##-----------------------------

if __name__ == "__main__" :

    from time import time
    import psana

    ntest = int(sys.argv[1]) if len(sys.argv)>1 else 1
    print 'Test # %d' % ntest
    dsname, src                  = 'exp=cxif5315:run=169', psana.Source('DetInfo(CxiDs2.0:Cspad.0)')
    if   ntest==2  : dsname, src = 'exp=meca1113:run=376', psana.Source('DetInfo(MecTargetChamber.0:Cspad2x2.1)')
    elif ntest==3  : dsname, src = 'exp=amob5114:run=403', psana.Source('DetInfo(Camp.0:pnCCD.0)')
    elif ntest==4  : dsname, src = 'exp=xppi0614:run=74',  psana.Source('DetInfo(NoDetector.0:Epix100a.0)')
    print 'Example for\n  dataset: %s\n  source : %s' % (dsname, src)

    ds = psana.DataSource(dsname)

    env = ds.env()
    cls = env.calibStore()
    eviter = ds.events()
    evt = eviter.next()
    rnum = evt.run()

    for key in evt.keys() : print key

    det = AreaDetector(src, env, pbits=0)

    nda = det.pedestals(rnum)
    print '\nnda:\n', nda
    print 'nda.dtype: %s nda.shape: %s' % (nda.dtype, nda.shape)

    t0_sec = time()
    nda = det.raw(evt)
    print '\nConsumed time to get raw data (sec) =', time()-t0_sec
    print '\nnda:\n', nda.flatten()[0:10]

    sys.exit ('Self test is done')

##-----------------------------
