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

    det = psana.Detector(src, env, pbits=0)

    # or directly
    from Detector.AreaDetector import AreaDetector    
    det = AreaDetector(src, env, pbits=0)

    # set parameters, if changed
    det.set_env(env)
    det.set_source(source)
    det.set_print_bits(pbits)

    # for Camera type of detector only
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
    stmask = det.status_as_mask(par, mode=0) # mode=0/1/2 masks zero/four/eight neighbors around each bad pixel
    mask   = det.mask_calib(par)
    cmod   = det.common_mode(par)

    # per-pixel (int16) gain mask from configuration data; 1/0 for low/high gain pixels,
    # or (float) per-pixel gain factors if gain is not None
    gmap = det.gain_mask(par, gain=None) 
    gmnz = det.gain_mask_non_zero(par, gain=None) # returns None if ALL pixels have high gain and mask should not be applied

    # set gfactor=high/low gain factor for CSPAD(2X2) in det.calib and det.image methods
    det.set_gain_mask_factor(gfactor=6.85)

    # set flag (for Chuck)
    det.do_reshape_2d_to_3d(flag=False) 

    # get raw data
    nda_raw = det.raw(evt)

    # get calibrated data (applied corrections: pedestals, common mode, gain mask, gain, pixel status mask)
    nda_cdata = det.calib(evt)
    # and with custom common mode parameter sequence
    nda_cdata = det.calib(evt, cmpars=(1,25,10,91)) # see description of common mode algorithms in confluence,
    # and with combined mask.
    nda_cdata = det.calib(evt, mbits=1) # see description of det.mask_comb method.

    # common mode correction for pedestal-subtracted numpy array nda:
    det.common_mode_apply(par, nda)
    cm_corr_nda = det.common_mode_correction(par, nda)
    # or with custom common mode parameter sequence
    det.common_mode_apply(par, nda, cmpars)
    cm_corr_nda = det.common_mode_correction(par, nda, cmpars)

    # access geometry information
    geo        = det.geometry(par)
    cx         = det.coords_x(par)
    cy         = det.coords_y(par)
    cz         = det.coords_z(par)
    cx, cy     = det.coords_xy(par)
    cx, cy, cz = det.coords_xyz(par)
    areas      = det.areas(par)
    mask_geo   = det.mask_geo(par, mbits=15) # mbits = +1-edges; +2-wide central cols;
    #                                                  +4/+8/+16-non-bond / with four / with eight neighbors
    ix         = det.indexes_x(par)
    iy         = det.indexes_y(par)
    ix, iy     = det.indexes_xy(par)
    pixel_size = det.pixel_size(par)
    ipx, ipy   = det.point_indexes(par, pxy_um=(0,0)) # by default returns detector origin indexes

    # change geometry object parameters
    det.move_geo(par, dx, dy, dz)    # move detector it 3-d space
    det.tilt_geo(par, dtx, dty, dtz) # tilt detector around 3 axes

    # access to combined mask
    # NOTE: by default none of mask keywords is set to True, returns None.
    mask = det.mask(par, calib=False, status=False, edges=False, central=False, unbond=False, unbondnbrs=False, unbondnbrs8=False)

    # or cashed mask with mbits - bitword control
    mask = det.mask_comb(par, mbits)
    # where mbits has bits for pixel_status, pixel_mask, edges, central, unbond, unbondnbrs, unbondnbrs8, respectively

    # static-mask methods for n-d mask arrays
    mask_nbr = det.mask_neighbors(mask, allnbrs=True) # allnbrs=False/True for 4/8 neighbors
    mask_edg = det.mask_edges(mask, mrows=1, mcols=1)

    # reconstruct image
    img   = det.image(evt) # uses calib() by default
    img   = det.image(evt, img_nda)
    xaxis = det.image_xaxis(par)
    yaxis = det.image_yaxis(par)

    # special case of indexing using non-default pixel scale size and x, y coordinate offset
    ix       = det.indexes_x(par, pix_scale_size_um=110, xy0_off_pix=(1000,1000))
    iy       = det.indexes_y(par, pix_scale_size_um=None, xy0_off_pix=None)
    ix, iy   = det.indexes_xy(par, pix_scale_size_um=None, xy0_off_pix=None)
    ipx, ipy = det.point_indexes(par, pxy_um=(0,0), pix_scale_size_um=None, xy0_off_pix=None) 
    img      = det.image(evt, img_nda, pix_scale_size_um=None, xy0_off_pix=None)
    xaxis    = det.image_xaxis(par, pix_scale_size_um=None, x0_off_pix=None)
    yaxis    = det.image_yaxis(par, pix_scale_size_um=None, y0_off_pix=None)

    # converting 2-d image to non-assembled array using pixel geometry information.
    # if geometry info is missing - returns None, except the case when flag is set by det.do_reshape_2d_to_3d(True).  
    nda      = det.ndarray_from_image(par, image, pix_scale_size_um=None, xy0_off_pix=None)

    # save n-d numpy array in the text file with metadata (global methods under hood of the class object)
    det.save_txtnda(fname='nda.txt', ndarr=myndarr, cmts=('comment1', 'comment2'), fmt='%.1f', verbos=False, addmetad=True)
    # or convenience method for cspad2x2
    det.save_asdaq(fname='nda.txt', ndarr=myndarr, cmts=('comment1', 'comment2'), fmt='%.1f', verbos=False, addmetad=True)

    # load n-d numpy array from the text file with metadata
    nda = det.load_txtnda(fname)

    # merge photons split between pixels and return array with integer number of photons per pixel
    nda_nphotons = det.photons(self, evt, nda_calib=None, mask=None, adu_per_photon=None)

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
#from   Detector.GlobalUtils import print_ndarr

##-----------------------------

class AreaDetector(object):
    """Python access to area detector data.
       Low level access is implemented on python or C++ through the boost::python wrapper
    """

##-----------------------------

    def __init__(self, src, env, pbits=0, iface='P') :
        """Constructor of the class AreaDetector.
        
           Parameters
           ----------
           src   : str       - data source, ex: 'CxiDs2.0:Cspad.0'
           env   : psana.Env - environment, ex: env=ds.env(), where ds=psana.DataSource('exp=cxif5315:run=169')
           pbits : int       - print control bit-word
           iface : char      - preferable interface: 'C' - C++ (everything) or 'P' - Python based (everything except common mode) 
        """

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
        
        self._rnum_mask  = None
        self._mbits_mask = None
        self._mask_nda   = None

        if self.pbits & 1 : self.print_members()

        self.set_gain_mask_factor(gfactor=6.85) # cpo default value for CSPAD(2x2) gain_mask, det.calib, det.image

        self.do_reshape_2d_to_3d(flag=False)    # Chuck - mandatory re-shaping 2-d to 3-d arrays        

        self.alg_photons = None

##-----------------------------

    def set_source(self, srcpar, set_sub=True) :
        """Sets data source parameter.
        
           Parameters
           ----------
           srcpar  : str  - regular source or its alias, ex.: 'XppEndstation.0:Rayonix.0' or 'rayonix'
           set_sub : bool - default=True - propagates source parameter to low level package  
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
        """Prints some of object attributes.
        """
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
        """Sets print-control bitword.

           Parameter
           ---------
           pbits : int - print-control bitword, ex.: 0377 (octal) 
        """
        self.pbits = pbits
        self.da.set_print_bits(pbits)
        self.pyda.set_print_bits(pbits)

##-----------------------------

    def set_env(self, env) :
        """Sets environment variable.
        
           Parameter
           ---------
           env : psana.Env() - psana environment variable, ex.: env=ds.env()
        """
        self.env = env
        self.pyda.set_env(env)
        #self.da.set_env(env) # is not implemented and is not used this way

##-----------------------------

    def set_do_offset(self, do_offset=False) :
        """Switch mode of the Camera type of detector.

           Parameter
           ---------
           do_offset : bool - control parameter to turn on/off Camera intensity offset, default=False
        """
        self.pyda.set_do_offset(do_offset)
        self.da.setMode(0 if do_offset else 1)

##-----------------------------

    def runnum(self, par) :
        """Returns integer run number from different options of input parameter.
        
           Parameter
           ---------
           par : int or psana.Event() - integer run number or psana event object.

           Returns
           -------
           int - run number
        """
        return par if isinstance(par, int) else par.run()

##-----------------------------

    def is_cspad(self) :
        """Returns True/False for CSPAD/other detector type

           Returns
           -------
           bool - True if current detector is CSPAD, False otherwise.
        """
        if self.dettype == gu.CSPAD :
            return True
        else :
            return False

##-----------------------------

    def is_cspad2x2(self) :
        """Returns True/False for CSPAD2x2/other detector type

           Returns
           -------
           bool - True if current detector is CSPAD2x2, False otherwise.
        """
        if self.dettype == gu.CSPAD2X2 :
            return True
        else :
            return False
        #if arr is not None and arr.size == 143560 : return True

##-----------------------------

    def ndim(self, par) : # par = evt or runnum(int)
        """Returns number of dimensions of current detector pixel numpy array.

           Parameter
           ---------
           par : int or psana.Event() - integer run number or psana event object.

           Returns
           -------
           int - number of dimensions of current detector pixel numpy array. If ndim>3 then returns 3.
        """
        if self._ndim is None :
            rnum = self.runnum(par)
            nd = self.da.ndim_v0(rnum) if self.iscpp else self.pyda.ndim(rnum)
            self._ndim = nd if nd<4 else 3
        return self._ndim

##-----------------------------

    def size(self, par) :
        """Returns size of the detector pixel-array.

           Parameter
           ---------
           par : int or psana.Event() - integer run number or psana event object.

           Returns
           -------
           int - size of the detector numpy pixel-array (number of pixels)
        """
        if self._size is None :
            rnum = self.runnum(par)
            self._size = self.da.size_v0(rnum) if self.iscpp else self.pyda.size(rnum)
        return self._size
    
##-----------------------------

    def shape(self, par) :
        """Returns shape of the detector pixel-array.

           Parameter
           ---------
           par : int or psana.Event() - integer run number or psana event object.

           Returns
           -------
           np.array - shape of the detector pixel-array, ex. for cspad (32,185,388).
        """        
        return np.array((2,185,388)) if self.is_cspad2x2() else self._shape_daq_(par)

##-----------------------------

    def _shape_daq_(self, par) :
        """Returns 2- or 3-d shape of the detector pixel-array as in DAQ.

           Parameter
           ---------
           par : int or psana.Event() - integer run number or psana event object.

           Returns
           -------
           np.array - detector pixel-array shape. If ndim>3 shape is reduced to 3-d.
                      Ex.: the shape like [4,8,185,388] is reduced to [32,185,388]
        """
        if self._shape is None :
            rnum = self.runnum(par)
            sh = self.da.shape_v0(rnum) if self.iscpp else self.pyda.shape(rnum)
            self._shape = sh if len(sh)<4 else np.array((self.size(rnum)/sh[-1]/sh[-2], sh[-2], sh[-1]))
        return self._shape        

##-----------------------------

    def loading_status(self, rnum, calibtype=None) :
        """Returns loading status of calibration constants of specified type.
           Parameters
           ----------
           rnum      : int - run number
           calibtype : int - enumerated value from the list
                       gu.PEDESTALS, PIXEL_STATUS, PIXEL_RMS, PIXEL_GAIN, PIXEL_MASK, PIXEL_BKGD, COMMON_MODE.

           Returns
           -------
           int - enumerated value from the list gu.LOADED, DEFAULT, UNREADABLE, UNDEFINED, WRONGSIZE, NONFOUND.
        """
        if self.iscpp : return self.da.status_v0(rnum, calibtype)
        else          : return self.pyda.status(rnum, calibtype)
        
##-----------------------------

    def do_reshape_2d_to_3d(self, flag=False) :
        """For Chuck - if flag is True - reshape 2-d arrays to 3-d.
           Parameters
           ----------
           flag : bool - False(def)/True 
        """        
        self.reshape_to_3d = flag
        self.pyda.do_reshape_2d_to_3d(flag)

##-----------------------------

    def _shaped_array_(self, rnum, arr, calibtype=None) :
        """ Returns shaped numpy.array if shape is defined and constants are loaded from file, None othervise.
        """
        if arr is None   : return None
        if arr.size == 0 : return None

        shape = arr.shape
        # for 2-d detectors
        if self.dettype in (gu.EPIX100A,\
                            gu.PRINCETON,\
                            gu.ANDOR,\
                            gu.ANDOR3D,\
                            gu.OPAL1000,\
                            gu.OPAL2000,\
                            gu.OPAL4000,\
                            gu.OPAL8000,\
                            gu.TM6740,\
                            gu.ORCAFL40,\
                            gu.FCCD960,\
                            gu.QUARTZ4A150,\
                            gu.RAYONIX,\
                            gu.FCCD,\
                            gu.TIMEPIX,\
                            gu.FLI,\
                            gu.PIMAX) :

            #if self.reshape_to_3d and len(shape)==2 :
            if self.reshape_to_3d :
                arr.shape = (1,shape[-2],shape[-1])
            return arr

        if calibtype is not None :
            status = self.loading_status(rnum, calibtype)
            if status != gu.LOADED and status != gu.DEFAULT : return None
        if self.size(rnum) : arr.shape = self._shape_daq_(rnum)

        return arr if not self.is_cspad2x2() else data2x2ToTwo2x1(arr)

##-----------------------------

    def _nda_or_none_(self, nda) :
        """Returns ndarray or None.
        """
        if nda is None : return None
        return nda if nda.size else None

##-----------------------------

    def pedestals(self, par) :
        """Returns per-pixel array of pedestals (dark run intensities) from calib directory.

           Parameter
           ---------
           par : int or psana.Event() - integer run number or psana event object.

           Returns
           -------
           np.array - per-pixel values loaded for calibration type pedestals.
        """
        rnum = self.runnum(par)
        if self.iscpp : return self._shaped_array_(rnum, self.da.pedestals_v0(rnum), gu.PEDESTALS)
        else          : return self._shaped_array_(rnum, self.pyda.pedestals(rnum),  gu.PEDESTALS)

##-----------------------------

    def rms(self, par) :
        """Returns per-pixel array of RMS values from calib directory.

           Parameter
           ---------
           par : int or psana.Event() - integer run number or psana event object.

           Returns
           -------
           np.array - per-pixel values loaded for calibration type pixel_rms.
        """
        rnum = self.runnum(par)
        if self.iscpp : return self._shaped_array_(rnum, self.da.pixel_rms_v0(rnum), gu.PIXEL_RMS)
        else          : return self._shaped_array_(rnum, self.pyda.pixel_rms(rnum),  gu.PIXEL_RMS)

##-----------------------------

    def gain(self, par) :
        """Returns per-pixel array of gain factors from calib directory.

           Parameter
           ---------
           par : int or psana.Event() - integer run number or psana event object.

           Returns
           -------
           np.array - per-pixel values loaded for calibration type pixel_gain.
        """
        rnum = self.runnum(par)
        if self.iscpp : return self._shaped_array_(rnum, self.da.pixel_gain_v0(rnum), gu.PIXEL_GAIN)
        else          : return self._shaped_array_(rnum, self.pyda.pixel_gain(rnum),  gu.PIXEL_GAIN)

##-----------------------------

    def mask_calib(self, par) :
        """Returns per-pixel array of mask from calib directory.

           Parameter
           ---------
           par : int or psana.Event() - integer run number or psana event object.

           Returns
           -------
           np.array - per-pixel values loaded for calibration type pixel_mask.
        """
        rnum = self.runnum(par)
        if self.iscpp : return self._shaped_array_(rnum, self.da.pixel_mask_v0(rnum), gu.PIXEL_MASK)
        else          : return self._shaped_array_(rnum, self.pyda.pixel_mask(rnum),  gu.PIXEL_MASK)

##-----------------------------

    def bkgd(self, par) :
        """Returns per-pixel array of background intensities from calib directory.

           Parameter
           ---------
           par : int or psana.Event() - integer run number or psana event object.

           Returns
           -------
           np.array - per-pixel values loaded for calibration type pixel_bkgd.
        """
        rnum = self.runnum(par)
        if self.iscpp : return self._shaped_array_(rnum, self.da.pixel_bkgd_v0(rnum), gu.PIXEL_BKGD)
        else          : return self._shaped_array_(rnum, self.pyda.pixel_bkgd(rnum),  gu.PIXEL_BKGD)

##-----------------------------

    def status(self, par) :
        """Returns array of pixel-status from calib directory.

           Parameter
           ---------
           par : int or psana.Event() - integer run number or psana event object.

           Returns
           -------
           np.array - per-pixel values loaded for calibration type pixel_status.
                    status bits: 0 - good pixel
                                 1 - saturated intensity
                                 2 - hot rms
                                 4 - cold
                                 8 - cold rms
        """
        rnum = self.runnum(par)
        if self.iscpp : return self._shaped_array_(rnum, self.da.pixel_status_v0(rnum), gu.PIXEL_STATUS)
        else          : return self._shaped_array_(rnum, self.pyda.pixel_status(rnum),  gu.PIXEL_STATUS)

##-----------------------------

    def status_as_mask(self, par, mode=0) :
        """Returns per-pixel array of mask generated from pixel_status.

           Parameter
           ---------
           par  : int or psana.Event() - integer run number or psana event object.
           mode : int - 0/1/2 masks zero/four/eight neighbors around each bad pixel

           Returns
           -------
           np.array - mask generated from calibration type pixel_status (1/0 for status 0/>0, respectively).
        """
        rnum = self.runnum(par)
        stat = self.status(rnum)
        if stat is None : return None
        smask = np.asarray(np.select((stat>0,), (0,), default=1), dtype=np.uint8)
        if mode : smask = gu.mask_neighbors(smask, allnbrs=(True if mode==2 else False))
        
        if self.is_cspad2x2() : return smask # stat already has a shape (2,185,388)
        return self._shaped_array_(rnum, smask, gu.PIXEL_STATUS)

##-----------------------------

    def mask_neighbors(self, mask, allnbrs=True) :
        """Returns n-d array of mask with masked neighbors on each 2-d segment.

           Parameter
           ---------
           mask    : np.array - input mask of good/bad (1/0) pixels
           allnbrs : bool - False/True masks 4/8 of neighbors around each bad pixel

           Returns
           -------
           np.array - mask with masked neighbors, shape = mask.shape
        """
        return gu.mask_neighbors(mask, allnbrs)

##-----------------------------

    def mask_edges(self, mask, mrows=1, mcols=1) :
        """Returns n-d array of mask with masked mrows and mcols edges on each 2-d segment.

           Parameter
           ---------
           mask  : np.array - input mask of good/bad (1/0) pixels
           mrows : int - number of edge rows to mask
           mcols : int - number of edge columns to mask

           Returns
           -------
           np.array - mask with masked edges, shape = mask.shape
        """
        return gu.mask_edges(mask, mrows, mcols)

##-----------------------------

    def gain_mask(self, par, gain=None) :
        """Returns per-pixel array with gain mask evaluated from detector configuration data.

           Parameter
           ---------
           par  : int or psana.Event() - integer run number or psana event object.
           gain : float - gain factor; mask will be multiplied by this factor if it is specified.

           Returns
           -------
           np.array - per-pixel gain mask; (int16) 1/0 or (float) gain/1 for low/high gain pixels.
        """
        return self.pyda.gain_mask(par, gain)

##-----------------------------

    def gain_mask_non_zero(self, par, gain=None) :
        """The same as gain_mask, but return None if ALL pixels have high gain.

           Parameter
           ---------
           par  : int or psana.Event() - integer run number or psana event object.
           gain : float - gain factor; mask will be multiplied by this factor if it is specified.

           Returns
           -------
           np.array - per-pixel gain mask; (int16) 1/0 or (float) gain/1 for low/high gain pixels.
        """
        return self.pyda.gain_mask_non_zero(par, gain)

##-----------------------------

    def common_mode(self, par) :
        """Returns array of common mode correction parameters.

           Parameter
           ---------
           par : int or psana.Event() - integer run number or psana event object.

           Returns
           -------
           np.array - values loaded for calibration type common_mode.
        """
        rnum = self.runnum(par)
        if self.iscpp : return self.da.common_mode_v0(rnum)
        else          : return self.pyda.common_mode(rnum)

##-----------------------------

    def instrument(self) :
        """Returns name of instrument.

           Returns
           -------
           str - name of instrument, ex.: 'AMO', 'XPP', 'SXR', 'CXI, 'MEC', 'XCS', etc.   
        """
        if self.iscpp : return self.da.instrument(self.env)
        else          : return self.pyda.inst()

##-----------------------------

    def print_config(self, evt) :
        """Prints configuration parameters if available.

           Parameter
           ---------
           evt : psana.Event() - psana event object.
        """
        if self.iscpp : self.da.print_config(evt, self.env)
        else          : self.pyda.print_config(evt)

##-----------------------------

    def raw_data(self, evt) :
        """Alias for depricated method renamed to raw(evt) 
        """

        return self.raw(evt)

##-----------------------------

    def raw(self, evt) :
        """Returns per-pixel array of intensities from raw data.

           Parameter
           ---------
           evt : psana.Event() - psana event object.

           Returns
           -------
           np.array - per-pixel intensities [ADU] of raw data.
        """
        rdata = None

        if self.iscpp :
            if   self.dettype == gu.CSPAD    : rdata = self.da.data_int16_3 (evt, self.env)
            elif self.dettype == gu.CSPAD2X2 : rdata = self.da.data_int16_3 (evt, self.env)
            elif self.dettype == gu.PNCCD    : rdata = self.da.data_uint16_3(evt, self.env)
            else :                             rdata = self.da.data_uint16_2(evt, self.env)

        else:
            rdata = self.pyda.raw_data(evt, self.env)

        if rdata is not None : return self._shaped_array_(self.runnum(evt), rdata)

        if self.pbits :
            print 'WARNING: AreaDetector.raw - data for source %s is not found in %s interface.'%\
                  (self.source, 'C++' if self.iscpp else 'Python')

        return rdata

##-----------------------------

    def common_mode_apply(self, par, nda, cmpars=None) :
        """Apply common mode correction algorithm.
        
           Apply common mode correction to nda (assuming that nda is data ndarray with subtracted pedestals)
           nda.dtype = np.float32 (or 64) is considered only, because common mode does not make sense for int data.
           If cmpars is not None then this sequence is used to override default common mode parameters coming from
           calib/.../common_mode/...

           Parameters
           ----------
           par    : int or psana.Event() - integer run number or psana event object.
           nda    : np.array - input: raw data with subtracted pedestals, output: cm corrected data.
           cmpars : list - common mode parameters, ex.: (1,50,50,100).
                    By default uses parameters from calib directory. 

           Returns
           -------
           I/O parameter nda : np.array - per-pixel corrected intensities.
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
        """Returns per-pixel array of common mode correction offsets.
  
           Parameters
           ----------
           par    : int or psana.Event() - integer run number or psana event object.
           nda    : np.array - raw data with subtracted pedestals. Input data is not modified.
           cmpars : list - common mode parameters, ex.: (1,50,50,100)
                    By default uses parameters from calib directory. 

           Returns
           -------
           np.array - per-pixel common mode correction offsets.
        """
        nda_cm_corr = np.array(nda, dtype=np.float32, copy=True)
        self.common_mode_apply(self.runnum(par), nda_cm_corr, cmpars)
        return nda_cm_corr - nda

##-----------------------------

    def calib_data(self, evt) :
        """Alias for depricated method renamed to calib.
        """
        return self.calib(evt)

##-----------------------------

    def _print_warning(self, msg='') :
        print '\nWARNING! %s: %s' % (self.__class__.__name__, msg)

##-----------------------------

    def set_gain_mask_factor(self, gfactor=6.85) :
        """Sets the gain factor which is passed to gain_mask(...) in the det.calib and det.image methods.
        """
        self._gain_mask_factor = gfactor

##-----------------------------

    def calib(self, evt, cmpars=None, mbits=1) :
        """Returns per-pixel array of calibrated data intensities.
        
           Gets raw data ndarray, applys baic corrections and return thus calibrated data.
           Applied corrections:
           - pedestal subtraction, returns det.raw(evt) if file with pedestals is missing   
           - apply common mode correction
           - gain_mask or "hybrid" gain from configuration object for CSPAD(2x2) only
           - gain if pixel_gain calibration file is available
           - apply mask generated from pixel status ("bad pixels"
             from calibration).  Optionally apply other masks if
             "mbits" parameter set
  
           Parameters
           ----------
           evt    : psana.Event() - psana event object.
           cmpars : list - common mode parameters, ex.: (1,50,50,100)
                    By default uses parameters from calib directory. 
           mbits  : int - mask control bit-word.  optional.
                    defaults to 1.  Bit definitions:
                 + 1  - pixel_status ("bad pixels" deployed by calibman)
                 + 2  - pixel_mask (deployed by user in "pixel_mask" calib dir)
                 + 4  - edge pixels
                 + 8  - big "central" pixels of a cspad2x1
                 + 16 - unbonded pixels
                 + 32 - unbonded pixel with four neighbors
                 + 64 - unbonded pixel with eight neighbors

           Returns
           -------
           np.array - per-pixel array of calibrated intensities from data.
        """
        rnum = self.runnum(evt)

        raw = self.raw(evt) 
        if raw is None :
            if self.pbits & 32 : self._print_warning('calib(...) - raw data are missing.')
            return None

        peds = self.pedestals(rnum)
        if peds is None :
            if self.pbits & 32 : self._print_warning('calib(...) - pedestals are missing, return raw data.')
            return np.array(raw, dtype=np.float32, copy=True)
        
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


        # ------------- 2016-06-24, 08-30 gain_mask -> gain_mask_non_zero
        gainmask = self.gain_mask_non_zero(rnum, gain=self._gain_mask_factor)
        #print 'XXX: use _gain_mask_factor = ', self._gain_mask_factor        
        #print 'XXX: gainmask.mean(): ', gainmask.mean()
        #print_ndarr(gainmask, 'XXX: det.calib(): apply gain_mask')

        if gainmask is None :
            if self.pbits & 32 : self._print_warning('calib(...) - gain_mask calibration in config store is missing.')
        else :
            cdata *= gainmask

        gain = self.gain(rnum)
        if gain is None :
            if self.pbits & 32 : self._print_warning('calib(...) - pixel_gain calibration file is missing.')
        else :
            #print_ndarr(gain, 'XXX: det.calib(): apply gain')
            cdata *= gain     
        # -------------

        if mbits > 0 : 
            #smask = self.status_as_mask(rnum) # (2, 185, 388)
            mask = self.mask_comb(rnum, mbits)
            if mask is None :
                if self.pbits & 32 : self._print_warning('combined mask is missing.')
            else :
                mask.shape = cdata.shape
                cdata *= mask      

        return cdata 

##-----------------------------

    def mask(self, par, calib=False, status=False, edges=False, central=False,\
             unbond=False, unbondnbrs=False, unbondnbrs8=False) :
        """Returns per-pixel array with mask values (per-pixel product of all requested masks).

           Parameters
           ----------
           par     : int or psana.Event() - integer run number or psana event object.
           calib   : bool - True/False = on/off mask from calib directory.
           status  : bool - True/False = on/off mask generated from calib pixel_status. 

           Other parameters make sense for cspad 2x1 sensors only:
           edges      : bool - True/False = on/off mask of edges. 
           central    : bool - True/False = on/off mask of two central columns. 
           unbond     : bool - True/False = on/off mask of unbonded pixels.
           unbondnbrs : bool - True/False = on/off mask of unbonded pixel with four neighbors. 
           unbondnbrs8: bool - True/False = on/off mask of unbonded pixel with eight neighbors. 

           Returns
           -------
           np.array - per-pixel mask values 1/0 for good/bad pixels.
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
        if unbondnbrs8: mbits += 16

        if mbits      : mask_nda = gu.merge_masks(mask_nda, self.mask_geo(rnum, mbits)) 
        return mask_nda

##-----------------------------

    def mask_comb(self, par, mbits=0) :
        """Returns per-pixel array with combined mask controlled by mbits bit-word.

           This method has same functionality as method mask(...) but under control of a single bit-word mbits. 

           Parameters
           ----------
           par   : int or psana.Event() - integer run number or psana event object.
           mbits : int - mask control bit-word.
                 = 0  - returns None
                 + 1  - pixel_status ("bad pixels" deployed by calibman)
                 + 2  - pixel_mask (deployed by user in "pixel_mask" calib dir)
                 + 4  - edge pixels
                 + 8  - big "central" pixels of a cspad2x1
                 + 16 - unbonded pixels
                 + 32 - unbonded pixel with four neighbors
                 + 64 - unbonded pixel with eight neighbors

           Returns
           -------
           np.array - per-pixel mask values 1/0 for good/bad pixels.
        """
        rnum = self.runnum(par)
        
        #Check/return cached mask
        if rnum == self._rnum_mask\
           and mbits == self._mbits_mask\
           and self._mask_nda is not None : return self._mask_nda

        #Evaluate new mask
        self._rnum_mask  = rnum
        self._mbits_mask = mbits
        self._mask_nda = self.mask(rnum,\
                                   status     = mbits&1,\
                                   calib      = mbits&2,\
                                   edges      = mbits&4,\
                                   central    = mbits&8,\
                                   unbond     = mbits&16,\
                                   unbondnbrs = mbits&32,\
                                   unbondnbrs8= mbits&64)
        return self._mask_nda

##-----------------------------
# Geometry info

    def geometry(self, par) :
        """Creates and returns detector geometry object.

           Parameter
           ---------
           par : int or psana.Event() - integer run number or psana event object.

           Returns
           -------
           PSCalib.GeometryAccess - detector geometry object.
        """
        rnum = self.runnum(par)
        return self.pyda.geoaccess(rnum) 


    def coords_x(self, par) :
        """Returns per-pixel array of x coordinates.

           Parameter
           ---------
           par : int or psana.Event() - integer run number or psana event object.

           Returns
           -------
           np.array - array of pixel x coordinates.
        """
        rnum = self.runnum(par)
        if self.iscpp : return self._shaped_array_(rnum, self.da.pixel_coords_x_v0(rnum))
        else          : return self._shaped_array_(rnum, self.pyda.coords_x(rnum)) 

    
    def coords_y(self, par) :
        """Returns per-pixel array of y coordinates.

           Parameter
           ---------
           par : int or psana.Event() - integer run number or psana event object.

           Returns
           -------
           np.array - array of pixel y coordinates.
        """
        rnum = self.runnum(par)
        if self.iscpp : return self._shaped_array_(rnum, self.da.pixel_coords_y_v0(rnum))
        else          : return self._shaped_array_(rnum, self.pyda.coords_y(rnum)) 


    def coords_z(self, par) :
        """Returns per-pixel array of z coordinates.

           Parameter
           ---------
           par : int or psana.Event() - integer run number or psana event object.

           Returns
           -------
           np.array - array of pixel z coordinates.
        """
        rnum = self.runnum(par)
        if self.iscpp : return self._shaped_array_(rnum, self.da.pixel_coords_z_v0(rnum))
        else          : return self._shaped_array_(rnum, self.pyda.coords_z(rnum)) 


    def coords_xy(self, par) :
        """Returns per-pixel arrays of x and y coordinates.

           Parameter
           ---------
           par : int or psana.Event() - integer run number or psana event object.

           Returns
           -------
           np.array - 2 arrays of pixel x and y coordinates, respectively.
        """
        rnum = self.runnum(par)
        cx, cy = self.pyda.coords_xy(rnum)
        return self._shaped_array_(rnum, cx), self._shaped_array_(rnum, cy) 


    def coords_xyz(self, par) :
        """Returns per-pixel arrays of x, y, and z coordinates.

           Parameter
           ---------
           par : int or psana.Event() - integer run number or psana event object.

           Returns
           -------
           np.array - 3 arrays of pixel x, y, and z coordinates, respectively.
        """
        rnum = self.runnum(par)
        cx, cy, cz = self.pyda.coords_xyz(rnum)
        return self._shaped_array_(rnum, cx), self._shaped_array_(rnum, cy), self._shaped_array_(rnum, cz) 


    def areas(self, par) :
        """Returns per-pixel array of pixel area.

           Parameter
           ---------
           par : int or psana.Event() - integer run number or psana event object.

           Returns
           -------
           np.array - array of pixel areas.
        """
        rnum = self.runnum(par)
        if self.iscpp : return self._shaped_array_(rnum, self.da.pixel_areas_v0(rnum))
        else          : return self._shaped_array_(rnum, self.pyda.areas(rnum)) 


    def mask_geo(self, par, mbits=255) :
        """Returns per-pixel array with mask controlled by mbits bit-word.

           Parameters
           ----------
           par   : int or psana.Event() - integer run number or psana event object.
           mbits : int - mask control bit-word.
                 = 0 - returns None
                 + 1 - edges     
                 + 2 - central   
                 + 4 - unbond    
                 + 8 - unbondnbrs

           Returns
           -------
           np.array - per-pixel mask values 1/0 for good/bad pixels.
        """
        rnum = self.runnum(par)
        if self.iscpp : return self._shaped_array_(rnum, self.da.pixel_mask_geo_v0(rnum, mbits))
        else          : return self._shaped_array_(rnum, self.pyda.mask_geo(rnum, mbits))


    def indexes_x(self, par, pix_scale_size_um=None, xy0_off_pix=None, do_update=False) :
        """Returns array of pixel integer x indexes.

           Parameters
           ----------
           par               : int or psana.Event() - integer run number or psana event object.
           pix_scale_size_um : float - pixel scale size [um] which is used to convert coordinate in index.
           xy0_off_pix       : list of floats - image (x,y) origin offset in order to make all indexes positively defined.
           do_update         : bool - force to update cached array.

           Returns
           -------
           np.array - array of pixel x indexes.
        """
        rnum = self.runnum(par)
        if self.iscpp : return self._shaped_array_(rnum, self.da.pixel_indexes_x_v0(rnum))
        else          : return self._shaped_array_(rnum, self.pyda.indexes_x(rnum, pix_scale_size_um, xy0_off_pix, do_update))


    def indexes_y(self, par, pix_scale_size_um=None, xy0_off_pix=None, do_update=False) :
        """Returns array of pixel integer y indexes.

           Parameters
           ----------
           par               : int or psana.Event() - integer run number or psana event object.
           pix_scale_size_um : float - pixel scale size [um] which is used to convert coordinate in index.
           xy0_off_pix       : list of floats - image (x,y) origin offset in order to make all indexes positively defined.
           do_update         : bool - force to update cached array.

           Returns
           -------
           np.array - array of pixel y indexes.
        """
        rnum = self.runnum(par)
        if self.iscpp : return self._shaped_array_(rnum, self.da.pixel_indexes_y_v0(rnum))
        else          : return self._shaped_array_(rnum, self.pyda.indexes_y(rnum, pix_scale_size_um, xy0_off_pix, do_update))


    def indexes_xy(self, par, pix_scale_size_um=None, xy0_off_pix=None, do_update=False) :
        """Returns two arrays of pixel integer x and y indexes.

           Parameters
           ----------
           par               : int or psana.Event() - integer run number or psana event object.
           pix_scale_size_um : float - pixel scale size [um] which is used to convert coordinate in index.
           xy0_off_pix       : list of floats - image (x,y) origin offset in order to make all indexes positively defined.
           do_update         : bool - force to update cached array.

           Returns
           -------
           (np.array, np.array) - list of two arrays of pixel x and y indexes, respectively.
        """
        rnum = self.runnum(par)
        iX, iY = self.pyda.indexes_xy(rnum, pix_scale_size_um, xy0_off_pix, do_update)
        return self._shaped_array_(rnum, iX), self._shaped_array_(rnum, iY)


    def point_indexes(self, par, pxy_um=(0,0), pix_scale_size_um=None, xy0_off_pix=None) :
        """Returns (ix, iy) indexes of the point (x,y) specified in [um].

           Parameters
           ----------
           par               : int or psana.Event() - integer run number or psana event object.
           pxy_um            : list of two float values - coordinates of the point in the detector frame, default (0,0)
           pix_scale_size_um : float - pixel scale size [um] which is used to convert coordinate in index.
           xy0_off_pix       : list of floats - image (x,y) origin offset in order to make all indexes positively defined.

           Returns
           -------
           tuple - (ix, iy) tuple of two indexes associated with input point coordinates.
        """
        rnum = self.runnum(par)
        ix, iy = self.pyda.point_indexes(rnum, pxy_um, pix_scale_size_um, xy0_off_pix)
        return ix, iy


    def pixel_size(self, par) :
        """Returns pixel scale size in [um]. 

           Parameters
           ----------
           par : int or psana.Event() - integer run number or psana event object.

           Returns
           -------
           float - pixel size in [um].
        """
        rnum = self.runnum(par)
        psize = self.da.pixel_scale_size_v0(rnum) if self.iscpp else self.pyda.pixel_size(rnum) # Ex: 109.92 [um]
        return psize if psize != 1 else None


    def move_geo(self, par, dx, dy, dz) :
        """Moves detector. 

           Parameters
           ----------
           par : int or psana.Event() - integer run number or psana event object.
           dx, dy, dz : float - three coordinate increments [um] of the detector motion. 
        """
        rnum = self.runnum(par)
        self.pyda.move_geo(par, dx, dy, dz)


    def tilt_geo(self, par, dtx, dty, dtz) :
        """Tilts detector. 

           Parameters
           ----------
           par : int or psana.Event() - integer run number or psana event object.
           dtx, dty, dtz : float - three angular increments [deg] of the detector tilt. 
        """
        rnum = self.runnum(par)
        self.pyda.tilt_geo(par, dtx, dty, dtz)


    def image_xaxis(self, par, pix_scale_size_um=None, x0_off_pix=None) :
        """Returns array of pixel x coordinates associated with image x-y grid.

           Parameters
           ----------
           par : int or psana.Event() - integer run number or psana event object.
           pix_scale_size_um : float - pixel scale size [um] which is used to convert coordinate in index.
           x0_off_pix        : float - origin x coordinate offset in number of pixels

           Returns
           -------
           np.array - array of pixel x coordinates of image x-y grid.
        """
        rnum = self.runnum(par)
        return self.pyda.image_xaxis(rnum, pix_scale_size_um, x0_off_pix)


    def image_yaxis(self, par, pix_scale_size_um=None, y0_off_pix=None) :
        """Returns array of pixel x coordinates associated with image x-y grid.

           Parameters
           ----------
           par : int or psana.Event() - integer run number or psana event object.
           pix_scale_size_um : float - pixel scale size [um] which is used to convert coordinate in index.
           y0_off_pix        : float - origin y coordinate offset in number of pixels

           Returns
           -------
           np.array - array of pixel y coordinates of image x-y grid.
        """
        rnum = self.runnum(par)
        return self.pyda.image_yaxis(rnum, pix_scale_size_um, y0_off_pix)


    def image(self, evt, nda_in=None, pix_scale_size_um=None, xy0_off_pix=None, do_update=False) :
        """Returns 2-d array of intensities for imaging.

           Parameters
           ----------
           evt               : psana.Event() - psana event object.
           nda_in            : input n-d array which needs to be converted in image; default - use calib methood.
           pix_scale_size_um : float - pixel scale size [um] which is used to convert coordinate in index.
           xy0_off_pix       : list of floats - image (x,y) origin offset in order to make all indexes positively defined.
           do_update         : bool - force to update cached array.

           Returns
           -------
           np.array - 2-d array of intensities for imaging.
        """
        rnum = self.runnum(evt)
        nda = nda_in if nda_in is not None else self.calib(evt)

        if nda is None : return None

        shape = nda.shape
        if self.reshape_to_3d and len(shape)==3 and shape[0]==1: nda.shape = shape[1:]

        if len(nda.shape)==2 and self.dettype != gu.EPIX100A :
            return nda

        if self.is_cspad2x2() : nda = two2x1ToData2x2(nda) # convert to DAQ shape for cspad2x2
        nda_img = np.array(nda, dtype=np.double).flatten()        
        if self.iscpp : return self._nda_or_none_(self.da.get_image_v0(rnum, nda_img))
        else          : return self._nda_or_none_(self.pyda.image(rnum, nda_img, pix_scale_size_um, xy0_off_pix, do_update))


    def ndarray_from_image(self, par, image, pix_scale_size_um=None, xy0_off_pix=None, do_update=False) :
        """Returns n-d array of intensities extracted from image using image bin indexes.

           Parameters
           ----------
           par               : int or psana.Event() - integer run number or psana event object.
           image             : np.array - input 2-d array which will be converted to n-d array.
           pix_scale_size_um : float - pixel scale size [um] which is used to convert coordinate in index.
           xy0_off_pix       : list of floats - image (x,y) origin offset in order to make all indexes positively defined.
           do_update         : bool - force to update cached array.

           Returns
           -------
           np.array - n-d array of intensities made from image.
        """
        rnum = self.runnum(par)
        return self._shaped_array_(rnum, self.pyda.ndarray_from_image(rnum, image, pix_scale_size_um, xy0_off_pix, do_update))

    #def __call__(self, evt, nda_in=None) :
    #    """Alias for image in order to call it as det(evt,...)"""
    #    return self.image(evt, nda_in)

##-----------------------------

    def save_txtnda(self, fname='nda.txt', ndarr=None, cmts=(), fmt='%.1f', verbos=False, addmetad=True) :
        """Saves n-d array in the formatted text file with hash-type cumments and metadata.

           Parameters
           ----------
           fname    : str - output file name.
           ndarr    : np.array - array of numerical values to save in text file.
           cmts     : list of str - list of strings which will be saved as comments in the file header.
           fmt      : str - format of values in the file.
           verbose  : bool - True/False = on/off messages from this method (about saved file etc.)
           addmetad : bool - True/False = on/off saving methadata (data type, and shape info) in file.
        """
        list_cmts = list(cmts)
        list_cmts.append('SOURCE  %s' % gu.string_from_source(self.source))
        # DO NOT ADD metadata for CSPAD and CSPAD2x2
        addmd = False if ndarr.size in (2*185*388, 32*185*388) else addmetad
        self.pyda.save_txtnda(fname, ndarr, list_cmts, fmt, verbos, addmd)

##-----------------------------

    def save_asdaq(self, fname='nda.txt', ndarr=None, cmts=(), fmt='%.1f', verbos=False, addmetad=True) :
        """Saves per-pixel n-d array shaped and ordered as in DAQ.

           The same functionality as in the method save_txtnda(...), but array is shuffled to DAQ order. 
           Currently re-shuffle pixels for cspad2x2 only from natural shape=(2,185,388) to daq shape (185,388,2).
           For all other detectors n-d array is saved unchanged. 

           Parameters
           ----------
           fname    : str - output file name.
           ndarr    : np.array - array of numerical values to save in text file.
           cmts     : list of str - list of strings which will be saved as comments in the file header.
           fmt      : str - format of values in the file.
           verbose  : bool - True/False = on/off messages from this method (about saved file etc.)
           addmetad : bool - True/False = on/off saving methadata (data type, and shape info) in file.
        """
        is_cspad2x2_natural = (ndarr.size == 2*185*388 and len(ndarr.shape)>1 and ndarr.shape[-1] == 388)
        nda = two2x1ToData2x2(ndarr) if is_cspad2x2_natural else ndarr
        self.save_txtnda(fname, nda, cmts, fmt, verbos, addmetad)

##-----------------------------

    def load_txtnda(self, fname) :
        """Returns n-d array loaded from specified formatted text file.

           Parameters
           ----------
           fname : str - input file name.

           Returns
           -------
           np.array - array with values loaded from file,
                      shaped in accordance with metadata (if available).
                      If metadata is missing, output array will have 2- or 1-d shape;
                      spaces and '\n' characters in the text file are used to find the shape of the array. 
        """

        return self.pyda.load_txtnda(fname)

##-----------------------------

    def photons(self, evt, nda_calib=None, mask=None, adu_per_photon=None) :
        """Returns 2-d or 3-d array of integer number of merged photons - algorithm suggested by Chuck.

           Parameters
           ----------
           evt            : psana.Event() - psana event object.
           nda_calib      : (float, double, int, int16) numpy.array - calibrated data, float number of photons per pixel.
           mask           : (uint8) numpy.array user defined mask.
           adu_per_photon : float conversion factor which is applied as nda_calib/adu_per_photon.

           Returns
           -------
           np.array - 2-d or 3-d array of integer number of merged photons.
        """

        if self.alg_photons is None :
            from Detector.AlgoAccess import alg_photons; self.alg_photons = alg_photons

        #rnum = self.runnum(evt)
        nda = nda_calib if nda_calib is not None else self.calib(evt)
        if adu_per_photon is not None and adu_per_photon !=0 :
            f = 1./adu_per_photon
            nda *= f

        msk = self.mask(evt, calib=True, status=True, edges=True, central=True, unbond=True, unbondnbrs=True) \
              if mask is None else mask

        return self.alg_photons(nda, msk)

##-----------------------------

    def shape_config(self, env) :
        return self.pyda.shape_config(env)

##-----------------------------
##-----------------------------
##-----------------------------
##-----------------------------
##-----------------------------
##-----------------------------

if __name__ == "__main__" :
    """Self-test method.
       Usage: python <path>/AreaDetector.py <test-number>
    """

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
