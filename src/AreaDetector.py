
"""
Class :py:class:`AreaDetector` contains a collection of access methods to detector data and meta-data
=====================================================================================================

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

    det = psana.Detector(src, env)

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
    shape = det.shape(par=0)
    size  = det.size(par=0)
    ndim  = det.ndim(par=0)
    instrument = det.instrument()

    # access intensity calibration parameters
    peds   = det.pedestals(par) # returns array of pixel pedestals from calib store type pedestals
    rms    = det.rms(par)       # returns array of pixel dark noise rms from calib store type pixel_rms
    gain   = det.gain(par)      # returns array of pixel gain from calib store type pixel_gain
    offset = det.offset(par)    # returns array of pixel offset from calib store type pixel_offset
    bkgd   = det.bkgd(par)      # returns array of pixel background from calib store type pixel_bkgd
    status = det.status(par)    # returns array of pixel status from calib store type pixel_status
    datast = det.datast(par)    # returns array of pixel status from calib store type pixel_datast
    stmask = det.status_as_mask(par, **kwargs) # returns array of masked bad pixels in det.status
                                               # kwargs.mode=0/1/2 masks zero/four/eight neighbors around each bad pixel
                                               # kwargs.indexes=(0,1,2,3,4) - merging parameter for epix10ka2m
                                               # kwargs.mstcode=0xffff - bitword for status codes to mask uint16
    mask   = det.mask_calib(par)  # returns array of pixel mask from calib store type pixel_mask
    cmod   = det.common_mode(par) # returns 1-d array of common mode parameters from calib store type common_mode

    # per-pixel (int16) gain mask from configuration data; 1/0 for low/high gain pixels,
    # or (float) per-pixel gain factors if gain is not None
    gmap = det.gain_mask(par, gain=None) # returns array of pixel gains using configuration data
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
    nda_cdata = det.calib(evt, status=True, calib=True) # see description of det.mask_v2 or deprecated det.mask_comb method.
    # NEW - common mode correction for pnCCD:
    nda_cdata = det.calib(evt, (8,5,500), mask=mask)

    # common mode correction for pedestal-subtracted numpy array nda:
    det.common_mode_apply(par, nda)
    cm_corr_nda = det.common_mode_correction(par, nda)
    # or with custom common mode parameter sequence
    det.common_mode_apply(par, nda, cmpars, **kwargs)
    cm_corr_nda = det.common_mode_correction(par, nda, cmpars, **kwargs)

    # access geometry information
    geo        = det.geometry(par)   # returns geometry object (top-most)

    cframe = gu.CFRAME_PSANA # or gu.CFRAME_LAB
    cx         = det.coords_x(par, cframe)   # returns array of pixel x coordinates
    cy         = det.coords_y(par, cframe)   # returns array of pixel y coordinates
    cz         = det.coords_z(par, cframe)   # returns array of pixel z coordinates
    cx, cy     = det.coords_xy(par, cframe)  # returns arrays of pixel x and y coordinates
    cx, cy, cz = det.coords_xyz(par, cframe) # returns arrays of pixel x, y, and z coordinates
    areas      = det.areas(par)      # returns array of pixel areas relative smallest pixel
    mask_geo   = det.mask_geo(par, mbits=15, **kwargs) # returns mask of segment-specific pixels
                                             #  mbits = +1-edges; +2-wide central cols;
                                             #          +4/+8/+16-non-bond / with four / with eight neighbors
                                             # **kwargs - dict of additional parameters (width=5,...)
    ix         = det.indexes_x(par)  # returns array of pixel indexes along x for image
    iy         = det.indexes_y(par)  # returns array of pixel indexes along y for image
    ix, iy     = det.indexes_xy(par) # returns arrays of pixel indexes along x and y for image
    pixel_size = det.pixel_size(par) # returns array of pixel sizes
    ipx, ipy   = det.point_indexes(par, pxy_um=(0,0)) # by default returns detector origin indexes

    # change geometry object parameters
    det.move_geo(par, dx, dy, dz)    # move detector it 3-d space
    det.tilt_geo(par, dtx, dty, dtz) # tilt detector around 3 axes

    # get geometry in PSF format.
    # PSF stands for asic (0,0) pixel Position, Slow, and Fast orthogonal vectors along rows and columns, respectively.
    # psf (list-of-tuples) shapesd as (<number-of-asics>, 3(vectors vp, vs, vf), 3(vector components x,y,z)).
    psf = det.psf(par, cframe=1) # cframe=1 stands for gu.CFRAME_LAB

    # convert psana per-panel data to PSF per-asic data array with shape=(<number-of-asics>, <rows-in-asic>, <cols-in-asic>)
    datapsf = det.data_psf(par, data)

    # get pixel coordinate array through the psf vectors
    xarr, yarr, zarr = det.pixel_coords_psf(par, cframe=1)

    # access to combined mask
    # NOTE: by default none of mask keywords is set to True, returns None.
    mask = det.mask(par, calib=False, status=False, edges=False, central=False, unbond=False, unbondnbrs=False, unbondnbrs8=False, **kwargs)

    mask = det.mask_v2(evt, status=True, unbond=False, neighbors=False, edges=False, central=False, calib=False, **kwa)

    # Example:
    kwa={'status'   :True, 'mstcode':64, 'indexes':(0,1,2,3,4),\
         'unbond'   :True,\
         'neighbors':True, 'rad':5, 'ptrn':'r',\
         'edges'    :True, 'mrows':2, 'mcols':4,\
         'central'  :True, 'wcentral':10}
    mask = det.mask_v2(evt, **kwa)

    # or cashed mask with mbits - bitword control
    mask = det.mask_comb(par, mbits, **kwargs)
    # where mbits has bits for pixel_status, pixel_mask, edges, central, unbond, unbondnbrs, unbondnbrs8, respectively

    # static-mask methods for n-d mask arrays
    mask_nbr = det.mask_neighbors(mask, allnbrs=True) # allnbrs=False/True for 4/8 neighbors
    mask = det.mask_neighbors_in_radius(self, mask, rad=9, ptrn='r') # mask array with increased by radial paramerer rad region around all 0-pixels in the input mask ndarray.
    mask_edg = det.mask_edges(mask, mrows=1, mcols=1)

    mask = det.mask_total(par, **kwargs) # is used in det.calib as det.mask_v2 if mbits is None else det.mask_comb

    # reconstruct image
    img   = det.image(evt) # uses calib() by default
    img   = det.image(evt, img_nda)
    xaxis = det.image_xaxis(par)
    yaxis = det.image_yaxis(par)

    # special case of indexing using non-default pixel scale size and x, y coordinate offset
    ix       = det.indexes_x(par, pix_scale_size_um=110, xy0_off_pix=(1000,1000))
    iy       = det.indexes_y(par, pix_scale_size_um=None, xy0_off_pix=None)
    ix, iy   = det.indexes_xy(par, pix_scale_size_um=None, xy0_off_pix=None)
    ix, iy   = det.indexes_xy_at_z(par, zplane=None, pix_scale_size_um=None, xy0_off_pix=None)
    ipx, ipy = det.point_indexes(par, pxy_um=(0,0), pix_scale_size_um=None, xy0_off_pix=None, cframe=gu.CFRAME_PSANA, fract=False)
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
    nda_nphotons = det.photons(self, evt, nda_calib=None, mask=None, adu_per_photon=None, thr_fraction=0.9)

See classes
  - :class:`AlgoAccess`
  - :class:`AreaDetector`
  - :class:`ControlDataDetector`
  - :class:`DdlDetector`       - access to DDL data
  - :class:`DetectorTypes`
  - :class:`EpicsDetector`     - access to EPICS data
  - :class:`EvrDetector`       - access to EVR data
  - :class:`Generic1DDetector`
  - :class:`GenericWFDetector`
  - :class:`GlobalUtils`
  - :class:`IpimbDetector`
  - :class:`OceanDetector`
  - :class:`PyDataAccess`
  - :class:`PyDetectorAccess`  - Python access interface to data
  - :class:`PyDetector`        - factory for different detectors
  - :class:`TDCDetector`
  - :class:`UsdUsbDetector`    - UsdUsb Encoder Box
  - :class:`WFDetector`        - access to waveform detector data

This software was developed for the LCLS project.
If you use all or part of it, please give an appropriate acknowledgment.

Author Mikhail Dubrovin
"""
from __future__ import print_function
from __future__ import division

import sys
import _psana
import Detector
import numpy as np
import PSCalib.GlobalUtils as gu
from   PSCalib.GeometryObject import data2x2ToTwo2x1, two2x1ToData2x2
from   Detector.PyDetectorAccess import PyDetectorAccess
from   Detector.GlobalUtils import info_ndarr

from Detector.UtilsJungfrau import calib_jungfrau
from Detector.UtilsEpix10ka import calib_epix10ka_any


class AreaDetector(object):
    """Python access to area detector data.
       Low level access is implemented on python or C++ through the boost::python wrapper
    """

    def __init__(self, src, env, pbits=0, iface='P'):
        """Constructor of the class :class:`AreaDetector`.

           Parameters

           - src   : str       - data source, e.g. 'CxiDs2.0:Cspad.0'
           - env   : psana.Env - environment, e.g. env=ds.env(), where ds=psana.DataSource('exp=cxif5315:run=169')
           - pbits : int       - print control bit-word
           - iface : char      - preferable interface: 'C' - C++ (everything) or 'P' - Python based (everything except common mode)
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

        if self.pbits & 1: self.print_members()

        self.set_gain_mask_factor(gfactor=6.85) # cpo default value for CSPAD(2x2) gain_mask, det.calib, det.image

        self.do_reshape_2d_to_3d(flag=False)    # Chuck - mandatory re-shaping 2-d to 3-d arrays

        self.alg_photons = None


    def set_source(self, srcpar, set_sub=True):
        """Sets data source parameter.

           Parameters

           - srcpar  : str  - regular source or its alias, ex.: 'XppEndstation.0:Rayonix.0' or 'rayonix'
           - set_sub : bool - default=True - propagates source parameter to low level package
        """
        #print('type of srcpar: ', type(srcpar))

        src = srcpar if isinstance(srcpar, _psana.Source) else _psana.Source(srcpar)
        str_src = gu.string_from_source(src)
        self.name = str_src

        # in case of alias convert it to _psana.Src
        amap = self.env.aliasMap()
        psasrc = amap.src(str_src)
        self.source  = src if amap.alias(psasrc) == '' else amap.src(str_src)

        if not isinstance(self.source, _psana.Source): self.source = _psana.Source(self.source)

        if self.pbits & 16:
            print('%s: input source: %s' % (self.__class__.__name__, src),\
                  '\n  string source: %s' % (str_src),\
                  '\n  source object: %s of type: %s' % (self.source, type(self.source)))

        if set_sub:
            self.pyda.set_source(self.source)
            self.da.set_source(self.source)


    def print_members(self):
        """Depricated method renamed to print_attributes()
        """
        self.print_attributes()


    def print_attributes(self):
        """Prints some of object attributes.
        """
        print('AreaDetector object attributes:', \
              '\n  source : %s' % self.source, \
              '\n  dettype: %d' % self.dettype, \
              '\n  detname: %s' % gu.dic_det_type_to_name[self.dettype], \
              '\n  pbits  : %d' % self.pbits, \
              '\n  iscpp  : %d' % self.iscpp, \
              '\n  ispyt  : %d' % self.ispyt)
        if self.iscpp: self.da.print_members()
        else         : self.pyda.print_attributes()


    def set_print_bits(self, pbits):
        """Sets print-control bitword.

           Parameter

           - pbits : int - print-control bitword, ex.: 0377 (octal)
        """
        self.pbits = pbits
        self.da.set_print_bits(pbits)
        self.pyda.set_print_bits(pbits)


    def set_env(self, env):
        """Sets environment variable.

           Parameter

           - env : psana.Env() - psana environment variable, ex.: env=ds.env()
        """
        self.env = env
        self.pyda.set_env(env)


    def set_do_offset(self, do_offset=False):
        """Switch mode of the Camera type of detector.

           Parameter

           - do_offset : bool - control parameter to turn on/off Camera intensity offset, default=False
        """
        self.pyda.set_do_offset(do_offset)
        self.da.setMode(0 if do_offset else 1)


    def runnum(self, par):
        """Returns integer run number from different options of input parameter.

           Parameter

           - par : int or psana.Event() - integer run number or psana event object.

           Returns

           - int - run number or 0 if can't be defined.
        """
        return par if isinstance(par, int) else par.run() if isinstance(par, _psana.Event) else 0


    def is_cspad(self):
        """Returns (bool) True/False for CSPAD/other detector type
        """
        return self.dettype == gu.CSPAD


    def is_cspad2x2(self):
        """Returns (bool) True/False for CSPAD2x2/other detector type
        """
        return self.dettype == gu.CSPAD2X2
        #if arr is not None and arr.size == 143560 : return True


    def is_jungfrau(self):
        """Returns (bool) True/False for jungfrau/other detector type
        """
        return self.dettype == gu.JUNGFRAU


    def is_epix10ka_any(self):
        """Returns (bool) True/False for epix10ka or its composites/other detector type
        """
        return self.dettype in (gu.EPIX10KA2M, gu.EPIX10KAQUAD, gu.EPIX10KA)


    def is_epix10ka(self):
        """Returns (bool) True/False for epix10ka/other detector type
        """
        return self.dettype == gu.EPIX10KA


    def is_epix10ka2m(self):
        """Returns (bool) True/False for epix10ka2m/other detector type
        """
        return self.dettype == gu.EPIX10KA2M


    def is_epix10kaquad(self):
        """Returns (bool) True/False for epix10kaquad/other detector type
        """
        return self.dettype == gu.EPIX10KAQUAD


    def is_epix100a(self):
        """Returns (bool) True/False for epix100a/other detector type
        """
        return self.dettype == gu.EPIX100A


    def ndim(self, par): # par = evt or runnum(int)
        """Returns number of dimensions of current detector pixel numpy array.

           Parameter

           - par : int or psana.Event() - integer run number or psana event object.

           Returns

           - int - number of dimensions of current detector pixel numpy array. If ndim>3 then returns 3.
        """
        if self._ndim is None:
            nd = self.pyda.ndim(par)
            if self.is_epix10ka_any(): return nd
            self._ndim = nd if nd<4 else 3
        return self._ndim


    def size(self, par):
        """Returns size of the detector pixel-array.

           Parameter

           - par : int or psana.Event() - integer run number or psana event object.

           Returns

           - int - size of the detector numpy pixel-array (number of pixels)
        """
        if self._size is None:
            self._size = self.pyda.size(par)
        return self._size


    def shape(self, par=0):
        """Returns shape of the detector pixel-array.

           For all detectors except cspad2x2 shape is the same as in DAQ.

           Parameter

           - par : int or psana.Event() - integer run number or psana event object.

           Returns

           - np.array - shape of the detector pixel-array, ex. for cspad (32,185,388).
        """
        return np.array((2,185,388)) if self.is_cspad2x2() else self._shape_daq_(par)


    def _shape_daq_(self, par=0):
        """Returns 2- or 3-d shape of the detector pixel-array as in DAQ.

           Parameter

           - par : int or psana.Event() - integer run number or psana event object.\

           Returns

           - np.array - detector pixel-array shape. If ndim .gt. 3 shape is reduced to 3-d.
                      Ex.: the shape like (4,8,185,388) is reduced to (32,185,388)
        """
        if self._shape is None:
            sh = self.pyda.shape(par)
            if self.is_epix10ka_any(): return sh
            self._shape = sh if len(sh)<4 else np.array((self.size(par)//sh[-1]//sh[-2], sh[-2], sh[-1]))
        return self._shape


    def loading_status(self, par, calibtype=None):
        """Returns loading status of calibration constants of specified type.

           Parameters

           - rnum      : int - run number
           - calibtype : int - enumerated value from the list
                         gu.PEDESTALS, PIXEL_STATUS, PIXEL_RMS, PIXEL_GAIN, PIXEL_MASK, PIXEL_BKGD, COMMON_MODE.

           Returns

           - int - enumerated value from the list gu.LOADED, DEFAULT, UNREADABLE, UNDEFINED, WRONGSIZE, NONFOUND.
        """
        if self.iscpp: return self.da.status_v0(self.runnum(par), calibtype)
        else         : return self.pyda.status(par, calibtype)


    def do_reshape_2d_to_3d(self, flag=False):
        """For Chuck - if flag is True - reshape 2-d arrays to 3-d.

           Parameters

           - flag : bool - False(def)/True
        """
        self.reshape_to_3d = flag
        self.pyda.do_reshape_2d_to_3d(flag)


    def _shaped_array_(self, par, arr, calibtype=None):
        """Returns shaped numpy.array if shape is defined and constants are loaded from file, None othervise.

           Parameters

           - par : int | psana.Event - run number of event object
           - arr : np.array - array to re-shape
           - calibtype : int - DEPRICATED calibration type

           Returns
           - np.array - reshaped input array, None if arr is None or zero size,
                        input array as is if its size is inconsistent with expected
                        (should be better to rise.IOError).
        """
        rnum = self.runnum(par)

        if arr is None  : return None
        if arr.size == 0: return None
        if arr.size != self.size(rnum):
            #msg = 'WARNING: Array shape %s size %d is different from its configuration shape %s size %d' %\
            #      (arr.shape, arr.size, self._shape_daq_(rnum), self.size(rnum))
            #print(msg)
            #raise IOError(msg)
            return arr # return array as is, works for Jungfrau
        if self.dettype in (gu.EPIX10KA2M, gu.EPIX10KAQUAD): return arr # as is

        if self.dettype == gu.EPIX10KA:
            sh = arr.shape
            if len(sh) == 2: arr.shape = (1,sh[-2],sh[-1])
            return arr # all 2d re-shaped to 3d

        shape = self._shape_daq_(rnum)

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
                            gu.PIMAX,\
                            gu.PIXIS):

            #if self.reshape_to_3d and len(shape)==2:
            if self.reshape_to_3d:
                arr.shape = (1,shape[-2],shape[-1])
            else:
                arr.shape = shape
            return arr

        #if calibtype is not None:
        #    status = self.loading_status(rnum, calibtype)
        #    if status != gu.LOADED and status != gu.DEFAULT: return None

        arr.shape = shape

        return arr if not self.is_cspad2x2() else data2x2ToTwo2x1(arr)


    def _nda_or_none_(self, nda):
        """Returns ndarray or None.
        """
        if nda is None: return None
        return nda if nda.size else None


    def pedestals(self, par):
        """Returns per-pixel array of pedestals (dark run intensities) from calib directory.

           Parameter

           - par : int or psana.Event() - integer run number or psana event object.

           Returns

           - np.array - per-pixel values loaded for calibration type pedestals.
        """
        return self._shaped_array_(par, self.pyda.pedestals(par), gu.PEDESTALS)


    def rms(self, par):
        """Returns per-pixel array of RMS values from calib directory.

           Parameter

           - par : int or psana.Event() - integer run number or psana event object.

           Returns

           - np.array - per-pixel values loaded for calibration type pixel_rms.
        """
        return self._shaped_array_(par, self.pyda.pixel_rms(par), gu.PIXEL_RMS)


    def gain(self, par):
        """Returns per-pixel array of gain factors from calib directory.

           Parameter

           - par : int or psana.Event() - integer run number or psana event object.

           Returns

           - np.array - per-pixel values loaded for calibration type pixel_gain.
        """
        return self._shaped_array_(par, self.pyda.pixel_gain(par), gu.PIXEL_GAIN)


    def offset(self, par):
        """Returns per-pixel array of offsets from calib directory.

           Parameter

           - par : int or psana.Event() - integer run number or psana event object.

           Returns

           - np.array - per-pixel values loaded for calibration type pixel_offset.
        """
        return self._shaped_array_(par, self.pyda.pixel_offset(par), gu.PIXEL_OFFSET)


    def mask_calib(self, par):
        """Returns per-pixel array of mask from calib directory.

           Parameter

           - par : int or psana.Event() - integer run number or psana event object.

           Returns

           - np.array - per-pixel values loaded for calibration type pixel_mask.
        """
        return self._shaped_array_(par, self.pyda.pixel_mask(par), gu.PIXEL_MASK)


    def bkgd(self, par):
        """Returns per-pixel array of background intensities from calib directory.

           Parameter

           - par : int or psana.Event() - integer run number or psana event object.

           Returns

           - np.array - per-pixel values loaded for calibration type pixel_bkgd.
        """
        return self._shaped_array_(par, self.pyda.pixel_bkgd(par), gu.PIXEL_BKGD)


    def status(self, par):
        """Returns array of pixel-status from calib directory.

           Parameter

           - par : int or psana.Event() - integer run number or psana event object.

           Returns

           - np.array - per-pixel values loaded for calibration type pixel_status.
                    status bits: 0 - good pixel
                                 1 - saturated intensity
                                 2 - hot rms
                                 4 - cold
                                 8 - cold rms
        """
        return self._shaped_array_(par, self.pyda.pixel_status(par), gu.PIXEL_STATUS)


    def datast(self, par):
        """Returns array of pixel data status from calib directory,
           the same as status, but evaluated for non-dark data runs.

           Parameter

           - par : int or psana.Event() - integer run number or psana event object.

           Returns

           - np.array - per-pixel values loaded for calibration type pixel_datast.
                    status bits: 0 - good pixel
                                 1,2,4,8,.. TBD
        """
        return self._shaped_array_(par, self.pyda.pixel_datast(par), gu.PIXEL_DATAST)


    def status_as_mask(self, par, **kwargs):
        """Returns per-pixel array of mask generated from pixel_status.

           Parameter

           - par  : int or psana.Event() - integer run number or psana event object.
           - kwargs.mstcode : bitword for mask status codes
           - kwargs.mode    : int - 0/1/2 masks zero/four/eight neighbors around each bad pixel
           - kwargs.indexes : tuple of indexes standing for 'FH','FM','FL','AHL-H','AML-M'

           Returns

           - np.array - mask generated from calibration type pixel_status (1/0 for status 0/>0, respectively).
        """
        stat = self.status(par)
        if stat is None: return None

        mstcode = kwargs.get('mstcode', 0xffff) # bitword for status codes to mask uint16
        mode = kwargs.get('mode', 0) # 0/1/2 masks zero/four/eight neighbors around each bad pixel

        if self.is_epix10ka_any():
            stat = gu.merge_status(stat, **kwargs) # indexes=(0,1,2,3,4) or (0,1,2)

        smask = np.asarray(np.select((stat & mstcode,), (0,), default=1), dtype=np.uint8)

        if mode: smask = gu.mask_neighbors(smask, allnbrs=(True if mode>=2 else False))

        if self.is_jungfrau(): # merge 3 gains
            return gu.merge_masks(gu.merge_masks(smask[0,:], smask[1,:]), smask[2,:])

        if self.is_cspad2x2(): return smask # stat already has a shape (2,185,388)
        return self._shaped_array_(par, smask, gu.PIXEL_STATUS)


    def mask_neighbors(self, mask, allnbrs=True):
        """Returns n-d array of mask with masked neighbors on each 2-d segment.

           Parameter

           - mask    : np.array - input mask of good/bad (1/0) pixels
           - allnbrs : bool - False/True masks 4/8 of neighbors around each bad pixel

           Returns

           - np.array - mask with masked neighbors, shape = mask.shape
        """
        return gu.mask_neighbors(mask, allnbrs)


    def mask_neighbors_in_radius(self, mask, rad=9, ptrn='r'):
        """Returns 2-d or n-d mask array with increased by radial paramerer rad region around all 0-pixels in the input mask.

           Parameter

           - mask : np.array - input mask of good/bad (1/0) pixels
           - rad  : int - radisl parameter for masking region aroung each 0-pixel in mask
           - ptrn : char - pattern of the masked region, ptrn='r' -rhombus, othervise square [-rad,+rad] in rows and columns.

           Returns

           - np.array - mask with masked neighbors, shape = mask.shape
        """
        return gu.mask_neighbors_in_radius(self, mask, rad, ptrn)


    def mask_edges(self, mask, mrows=1, mcols=1):
        """Returns n-d array of mask with masked mrows and mcols edges on each 2-d segment.

           Parameter

           - mask  : np.array - input mask of good/bad (1/0) pixels
           - mrows : int - number of edge rows to mask
           - mcols : int - number of edge columns to mask

           Returns

           - np.array - mask with masked edges, shape = mask.shape
        """
        return gu.mask_edges(mask, mrows, mcols)


    def gain_mask(self, par, gain=None):
        """Returns per-pixel array with gain mask evaluated from detector configuration data.

           Parameter

           - par  : int or psana.Event() - integer run number or psana event object.
           - gain : float - gain factor; mask will be multiplied by this factor if it is specified.

           Returns

           - np.array - per-pixel gain mask; (int16) 1/0 or (float) gain/1 for low/high gain pixels.
        """
        return self._shaped_array_(par, self.pyda.gain_mask(par, gain), gu.PIXEL_MASK)


    def gain_mask_non_zero(self, par, gain=None):
        """The same as gain_mask, but return None if ALL pixels have high gain.

           Parameter

           - par  : int or psana.Event() - integer run number or psana event object.
           - gain : float - gain factor; mask will be multiplied by this factor if it is specified.

           Returns

           - np.array - per-pixel gain mask; (int16) 1/0 or (float) gain/1 for low/high gain pixels.
        """
        return self._shaped_array_(par, self.pyda.gain_mask_non_zero(par, gain), gu.PIXEL_MASK)


    def common_mode(self, par):
        return self.pyda.common_mode(par)


    def instrument(self):
        return self.pyda.inst()


    def print_config(self, evt):
        self.pyda.print_config(evt)


    def raw_data(self, evt):
        return self.raw(evt)


    def raw(self, evt):
        """Returns per-pixel array of intensities from raw data.

           Parameter

           - evt : psana.Event() - psana event object.

           Returns

           - np.array - per-pixel intensities [ADU] of raw data.
        """
        #rdata = None
        #if self.iscpp :
        #    if   self.dettype == gu.CSPAD   : rdata = self.da.data_int16_3 (evt, self.env)
        #    elif self.dettype == gu.CSPAD2X2: rdata = self.da.data_int16_3 (evt, self.env)
        #    elif self.dettype == gu.PNCCD   : rdata = self.da.data_uint16_3(evt, self.env)
        #    else:                             rdata = self.da.data_uint16_2(evt, self.env)
        #else:
        rdata = self.pyda.raw_data(evt, self.env)

        if rdata is not None: return self._shaped_array_(self.runnum(evt), rdata)

        if self.pbits:
            print('WARNING: AreaDetector.raw - data for source %s is not found in %s interface.'%\
                  (self.source, 'C++' if self.iscpp else 'Python'))

        return rdata


    def common_mode_apply(self, par, nda, cmpars=None, **kwargs):
        """Apply common mode correction algorithm.

           Apply common mode correction to nda (assuming that nda is data ndarray with subtracted pedestals)
           nda.dtype = np.float32 (or 64) is considered only, because common mode does not make sense for int data.
           If cmpars is not None then this sequence is used to override default common mode parameters coming from
           calib/.../common_mode/...

           Parameters

           - par    : int or psana.Event() - integer run number or psana event object.
           - nda    : np.array - input: raw data with subtracted pedestals, output: cm corrected data.
           - cmpars : list - common mode parameters, ex.: (1,50,50,100). cmpars=0 - common mode is not applied.
                    By default uses parameters from calib directory.

           Returns

           - I/O parameter nda : np.array - per-pixel corrected intensities.
        """

        # TURN OFF common mode correction using input parameter cmpars=0
        if cmpars==0: return

        rnum = self.runnum(par)
        _cmpars = self.common_mode(rnum) if cmpars is None else cmpars

        # TURN OFF common mode correction in default object PSCalib.CalibParsBase*
        if _cmpars[0]==0: return

        shape0 = nda.shape
        nda.shape = (nda.size,)

        if _cmpars is not None and _cmpars[0] in [6,8]:
            # go into python
            self.pyda.common_mode_apply(_cmpars, nda, **kwargs)
        else:
            # go into cpp
            if cmpars is not None:
                self.da.set_cmod_pars(rnum, np.array(cmpars, dtype=np.float64))
            if nda.dtype == np.float64:
                self.da.common_mode_double_v0(rnum, nda)
            if nda.dtype == np.float32:
                self.da.common_mode_float_v0(rnum, nda)

        nda.shape = shape0


    def common_mode_correction(self, par, nda, cmpars=None, **kwargs):
        """Returns per-pixel array of common mode correction offsets.

           Parameters

           - par    : int or psana.Event() - integer run number or psana event object.
           - nda    : np.array - raw data with subtracted pedestals. Input data is not modified.
           - cmpars : list - common mode parameters, ex.: (1,50,50,100)
                    By default uses parameters from calib directory.

           Returns

           - np.array - per-pixel common mode correction offsets.
        """
        nda_cm_corr = np.array(nda, dtype=np.float32, copy=True)
        self.common_mode_apply(self.runnum(par), nda_cm_corr, cmpars, **kwargs)
        return nda_cm_corr - nda


    def calib_data(self, evt):
        return self.calib(evt)


    def _print_warning(self, msg=''):
        print('\nWARNING! %s: %s' % (self.__class__.__name__, msg))


    def set_gain_mask_factor(self, gfactor=6.85):
        """Sets the gain factor which is passed to gain_mask(...) in the det.calib and det.image methods.
        """
        self._gain_mask_factor = gfactor


    def calib(self, evt, cmpars=None, mbits=None, **kwargs):
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

           - evt    : psana.Event() - psana event object.
           - cmpars : list - common mode parameters, ex.: (1,50,50,100)
                    By default uses parameters from calib directory.
                    0 - common mode is not applied.
           - mbits  : int - DEPRECATED mask control bit-word. optional.

           - **kwargs : dict - parameters for mask, common mode correction algorithm etc., i.e. for pnccd: cmpars=(8,5,500).
                method mask_v2 - descriptin of mask parameters
                method mask_comb - descriptin of mask parameters - works if mbits>0

           Returns

           - np.array - per-pixel array of calibrated intensities from data.
        """
        kwargs['mbits']=mbits

        if self.is_jungfrau():
            return calib_jungfrau(self, evt, cmpars, **kwargs)
        if self.is_epix10ka_any():
            return calib_epix10ka_any(self, evt, cmpars, **kwargs)

        rnum = self.runnum(evt)

        raw = self.raw(evt)
        if raw is None:
            if self.pbits & 32: self._print_warning('calib(...) - raw data are missing.')
            return None

        peds = self.pedestals(evt)
        if peds is None:
            if self.pbits & 32: self._print_warning('calib(...) - pedestals are missing, return raw data.')
            return np.array(raw, dtype=np.float32, copy=True)

        if raw.shape != peds.shape:
            if self.pbits & 32:
                msg = 'calib(...) - raw.shape = %s is different from peds.shape = %s. Try reshaping to data...' \
                      % (str(raw.shape), str(peds.shape))
                self._print_warning(msg)
            try   : peds.shape = raw.shape
            except: return None

        cdata = np.array(raw, dtype=np.float32, copy=True)
        cdata -= peds  # for cspad2x2 (2, 185, 388)

        if self.is_cspad2x2(): cdata = two2x1ToData2x2(cdata) # convert to DAQ shape for cspad2x2 ->(185, 388, 2)

        self.common_mode_apply(rnum, cdata, cmpars, **kwargs)

        if self.is_cspad2x2(): cdata = data2x2ToTwo2x1(cdata) # convert to Natural shape for cspad2x2 ->(2, 185, 388)

        # ------------- 2016-06-24, 08-30 gain_mask -> gain_mask_non_zero

        if self.is_cspad():
            gainmask = self.gain_mask_non_zero(rnum, gain=self._gain_mask_factor)
            #print('XXX: use _gain_mask_factor = ', self._gain_mask_factor)
            #print('XXX: gainmask.mean(): ', gainmask.mean())
            #print_ndarr(gainmask, 'XXX: det.calib(): apply gain_mask')

            if gainmask is None:
                if self.pbits & 32: self._print_warning('calib(...) - gain_mask calibration in config store is missing.')
            else:
                cdata *= gainmask

        gain = self.gain(evt)
        if gain is None:
            if self.pbits & 32: self._print_warning('calib(...) - pixel_gain calibration file is missing.')
        else:
            #print_ndarr(gain, 'XXX: det.calib(): apply gain')
            cdata *= gain
        # -------------

        mask = self.mask_total(evt, **kwargs)

        if mask is None:
            if self.pbits & 32: self._print_warning('combined mask is missing.')
        else:
            mask.shape = cdata.shape
            cdata *= mask

        return cdata


    def mask_total(self, par, **kwargs):
        """returns the best cached mask for det.calib method selected from det.mask_v2 or deprecated det.mask_comb methods.
        """

        rnum = self.runnum(par)

        #Check/return cached mask
        if rnum == self._rnum_mask\
           and self._mask_nda is not None: return self._mask_nda

        #Evaluate new mask
        mbits = kwargs.pop('mbits', None) # None - new mask_v2 is used for pixel_status only
        self._rnum_mask  = rnum
        self._mask_nda = self.mask_v2(par, **kwargs) if mbits is None else\
                         self.mask_comb(par, mbits, **kwargs) if mbits>0 else\
                         None

        # Merge with mask from optional parameter in det.calib(...,mask=...)
        mask_opt = kwargs.get('mask',None)
        if mask_opt is not None:
            self._mask_nda = mask_opt if mask is None else gu.merge_masks(self._mask_nda, mask_opt)

        return self._mask_nda


    def mask_v2(self, par, status=True, unbond=False, neighbors=False, edges=False, central=False, calib=False, **kwargs):
        """Returns combined mask controlled by the keyword arguments.
           Parameters
           ----------
           - status   : bool : True  - mask from pixel_status constants,
                                       kwargs: mstcode=0o377 - status bits to use in mask.
                                       Status bits show why pixel is considered as bad.
                                       Content of the bitword depends on detector and code version.
                                       It is wise to exclude pixels with any bad status by setting mstcode=0o377.
                                       kwargs: indexes=(0,1,2,3,4) - list of gain range indexes to merge for epix10ka only
           - unbond   : bool : False - mask of unbond pixels for cspad 2x1 panels only
           - neighbor : bool : False - mask of neighbors of all bad pixels,
                                       kwargs: rad=5 - radial parameter of masked region
                                       kwargs: ptrn='r'-rhombus, 'c'-circle, othervise square region around each bad pixel
           - edges    : bool : False - mask edge rows and columns of each panel,
                                       kwargs: mrows=1, mcols=1 - number of masked edge rows, columns
           - central  : bool : False - mask central rows and columns of each panel consisting of ASICS (cspad, epix, jungfrau),
                                       kwargs: wcentral=1 - number of masked central rows and columns in the segment
                                       works for cspad2x1, epix100, epix10ka, jungfrau
           - calib    : bool : False - apply user's defined mask from pixel_mask constants

           Returns
           -------
           np.array: dtype=np.uint8, shape as det.raw - mask array of 1 or 0 or None if all switches are False.
        """
        mask = None
        if status:
            mstcode = kwargs.get('mstcode', 0o377)
            indexes = kwargs.get('indexes', (0,1,2,3,4) if self.is_epix10ka_any() else None)
            mask = self.status_as_mask(par, mstcode=mstcode, mode=0, indexes=indexes)
            # mode=0 - do not mask neighbors here
            # indexes=(0,1,2,3,4) - list of indexes of epix10ka... gain modes to merge status

        if unbond and (self.is_cspad2x2() or self.is_cspad()):
            mask_unbond = self.mask_geo(par, width=0, wcentral=0, mbits=4) # mbits=4 - unbonded pixels for cspad2x1 segments
            mask = mask_unbond if mask is None else gu.merge_masks(mask, mask_unbond)

        if neighbors and mask is not None:
            rad = kwargs.get('rad', 5)
            ptrn = kwargs.get('ptrn', 'r')
            mask = gu.mask_neighbors_in_radius(mask, rad=rad, ptrn=ptrn)

        if edges:
            mrows = kwargs.get('mrows', 1)
            mcols = kwargs.get('mcols', 1)
            mask_edges = gu.mask_edges(mask, mrows=mrows, mcols=mcols) # masks each segment edges only
            mask = mask_edges if mask is None else gu.merge_masks(mask, mask_edges)

        if central:
            # mask_geo
            #mbits=1 - mask edges,
            #     +2 - mask two central columns,
            #     +4 - mask non-bonded pixels,
            #     +8 - mask nearest four neighbours of nonbonded pixels,
            #     +16- mask eight neighbours of nonbonded pixels.

            wcentral = kwargs.get('wcentral', 1)
            mask_central = self.mask_geo(par, width=0, wcentral=wcentral, mbits=2)
            mask = mask_central if mask is None else gu.merge_masks(mask, mask_central)

        if calib:
            mask_calib = self.mask_calib(par)
            mask = mask_calib if mask is None else gu.merge_masks(mask, mask_calib)

        return mask


    def mask(self, par, calib=False, status=False, edges=False, central=False,\
             unbond=False, unbondnbrs=False, unbondnbrs8=False, **kwargs):
        """Returns per-pixel array with mask values (per-pixel product of all requested masks).

           Parameters

           - par     : int or psana.Event() - integer run number or psana event object.
           - calib   : bool - True/False = on/off mask from calib directory.
           - status  : bool - True/False = on/off mask generated from calib pixel_status.

           Other parameters work for selected detectors with appropriate implementation (cspad, epix10ka, jungfrau etc.):

           - edges      : bool - True/False = on/off mask of edges.
           - central    : bool - True/False = on/off mask of two central columns.
           - unbond     : bool - True/False = on/off mask of unbonded pixels.
           - unbondnbrs : bool - True/False = on/off mask of unbonded pixel with four neighbors.
           - unbondnbrs8: bool - True/False = on/off mask of unbonded pixel with eight neighbors.
           - kwargs     : dict - additional parameters passed to low level methods
                          kwargs.mstcode=0xffff - status_as_mask - bitword for mask status codes
                          kwargs.mode=0/1/2 - status_as_mask - masks zero/four/eight neighbors around each bad pixel
                          kwargs.indexes=(0,1,2,3,4) - status_as_mask list of gain indexes to merge for epix10ka2n
                          kwargs.mbits=1 - mask_geo - mask edges, +2 - mask central in mask_geo
                          kwargs.width=1 - mask_geo - number of masked rows columns on each edge
                          kwargs.wcentral=1 - mask_geo - number of masked rows columns in the center of each panel

           Returns

           - np.array - per-pixel mask values 1/0 for good/bad pixels.
        """
        rnum = self.runnum(par)

        mask_nda = None
        if calib : mask_nda = self.mask_calib(par)
        if status: mask_nda = gu.merge_masks(mask_nda, self.status_as_mask(par, **kwargs))

        mbits = 0
        if edges      : mbits += 1
        if central    : mbits += 2
        if unbond     : mbits += 4
        if unbondnbrs : mbits += 8
        if unbondnbrs8: mbits += 16

        if mbits      : mask_nda = gu.merge_masks(mask_nda, self.mask_geo(rnum, mbits=mbits, **kwargs))
        return mask_nda


    def mask_comb(self, par, mbits=0, **kwargs):
        """Returns per-pixel array with combined mask controlled by mbits bit-word.

           This method has same functionality as method mask(...) but under control of a single bit-word mbits.

           Parameters

           - par   : int or psana.Event() - integer run number or psana event object.
           - mbits : int - mask control bit-word.

                 = 0  - returns None
                 + 1  - pixel_status ("bad pixels" deployed by calibman)
                 + 2  - pixel_mask (deployed by user in "pixel_mask" calib dir)
                 + 4  - edge pixels
                 + 8  - big "central" pixels of a cspad2x1
                 + 16 - unbonded pixels
                 + 32 - unbonded pixel with four neighbors
                 + 64 - unbonded pixel with eight neighbors

           - kwargs : dict - additional parameters passed to low level methods as explained in method mask(...)

           Returns

           - np.array - per-pixel mask values 1/0 for good/bad pixels.
        """
        rnum = self.runnum(par)

        #Check/return cached mask
        if rnum == self._rnum_mask\
           and mbits == self._mbits_mask\
           and self._mask_nda is not None: return self._mask_nda

        #Evaluate new mask
        self._rnum_mask  = rnum
        self._mbits_mask = mbits
        self._mask_nda = self.mask(par,\
                                   status     = mbits&1,\
                                   calib      = mbits&2,\
                                   edges      = mbits&4,\
                                   central    = mbits&8,\
                                   unbond     = mbits&16,\
                                   unbondnbrs = mbits&32,\
                                   unbondnbrs8= mbits&64,\
                                   **kwargs)
        return self._mask_nda

# Geometry info

    def geometry(self, par):
        """Creates and returns detector geometry object.

           Parameter

           - par : psana.Event() | int - psana event object or run number

           Returns

           - PSCalib.GeometryAccess - detector geometry object.
        """
        #rnum = self.runnum(par)
        return self.pyda.geoaccess(par)


    def coords_x(self, par, cframe=gu.CFRAME_PSANA):
        """Returns per-pixel array of x coordinates.

           Parameter

           - par : int or psana.Event() - integer run number or psana event object.

           Returns

           - np.array - array of pixel x coordinates.
        """
        return self._shaped_array_(par, self.pyda.coords_x(par, cframe))


    def coords_y(self, par, cframe=gu.CFRAME_PSANA):
        """Returns per-pixel array of y coordinates.

           Parameter

           - par : int or psana.Event() - integer run number or psana event object.

           Returns

           - np.array - array of pixel y coordinates.
        """
        return self._shaped_array_(par, self.pyda.coords_y(par, cframe))


    def coords_z(self, par, cframe=gu.CFRAME_PSANA):
        """Returns per-pixel array of z coordinates.

           Parameter

           - par : int or psana.Event() - integer run number or psana event object.

           Returns

           - np.array - array of pixel z coordinates.
        """
        return self._shaped_array_(par, self.pyda.coords_z(par, cframe))


    def coords_xy(self, par, cframe=gu.CFRAME_PSANA):
        """Returns per-pixel arrays of x and y coordinates.

           Parameter

           - par : int or psana.Event() - integer run number or psana event object.

           Returns

           - np.array - 2 arrays of pixel x and y coordinates, respectively.
        """
        rnum = self.runnum(par)
        cx, cy = self.pyda.coords_xy(par, cframe)
        return self._shaped_array_(rnum, cx), self._shaped_array_(rnum, cy)


    def coords_xyz(self, par, cframe=gu.CFRAME_PSANA):
        """Returns per-pixel arrays of x, y, and z coordinates.

           Parameter

           - par : int or psana.Event() - integer run number or psana event object.

           Returns

           - np.array - 3 arrays of pixel x, y, and z coordinates, respectively.
        """
        rnum = self.runnum(par)
        cx, cy, cz = self.pyda.coords_xyz(par, cframe)
        return self._shaped_array_(rnum, cx), self._shaped_array_(rnum, cy), self._shaped_array_(rnum, cz)


    def areas(self, par):
        """Returns per-pixel array of pixel area.

           Parameter

           - par : int or psana.Event() - integer run number or psana event object.

           Returns

           - np.array - array of pixel areas.
        """
        return self._shaped_array_(par, self.pyda.areas(par))


    def mask_geo(self, par, mbits=255, **kwargs):
        """Returns per-pixel array with mask controlled by mbits bit-word.

           Parameters

           - par   : int or psana.Event() - integer run number or psana event object.
           - mbits : int - mask control bit-word.

                 = 0 - returns None
                 + 1 - edges
                 + 2 - central
                 + 4 - unbond
                 + 8 - unbondnbrs
           - kwargs     : dict - additional parameters passed to low level methods (width,...)

           Returns

           - np.array - per-pixel mask values 1/0 for good/bad pixels.
        """
        return self._shaped_array_(par, self.pyda.mask_geo(par, mbits=mbits, **kwargs))


    def indexes_x(self, par, pix_scale_size_um=None, xy0_off_pix=None, do_update=False):
        """Returns array of pixel integer x indexes.

           Parameters

           - par               : int or psana.Event() - integer run number or psana event object.
           - pix_scale_size_um : float - pixel scale size [um] which is used to convert coordinate in index.
           - xy0_off_pix       : list of floats - image (x,y) origin offset in order to make all indexes positively defined.
           - do_update         : bool - force to update cached array.

           Returns

           - np.array - array of pixel x indexes.
        """
        return self._shaped_array_(par, self.pyda.indexes_x(par, pix_scale_size_um, xy0_off_pix, do_update))


    def indexes_y(self, par, pix_scale_size_um=None, xy0_off_pix=None, do_update=False):
        """Returns array of pixel integer y indexes.

           Parameters

           - par               : int or psana.Event() - integer run number or psana event object.
           - pix_scale_size_um : float - pixel scale size [um] which is used to convert coordinate in index.
           - xy0_off_pix       : list of floats - image (x,y) origin offset in order to make all indexes positively defined.
           - do_update         : bool - force to update cached array.

           Returns

           - np.array - array of pixel y indexes.
        """
        return self._shaped_array_(par, self.pyda.indexes_y(par, pix_scale_size_um, xy0_off_pix, do_update))


    def indexes_xy(self, par, pix_scale_size_um=None, xy0_off_pix=None, do_update=False):
        """Returns two arrays of pixel integer x and y indexes.

           Parameters

           - par               : int or psana.Event() - integer run number or psana event object.
           - pix_scale_size_um : float - pixel scale size [um] which is used to convert coordinate in index.
           - xy0_off_pix       : list of floats - image (x,y) origin offset in order to make all indexes positively defined.
           - do_update         : bool - force to update cached array.

           Returns

           - (np.array, np.array) - list of two arrays of pixel x and y indexes, respectively.
        """
        rnum = self.runnum(par)
        iX, iY = self.pyda.indexes_xy(par, pix_scale_size_um, xy0_off_pix, do_update)
        return self._shaped_array_(rnum, iX), self._shaped_array_(rnum, iY)


    def indexes_xy_at_z(self, par, zplane=None, pix_scale_size_um=None, xy0_off_pix=None, do_update=False):
        """Returns two arrays of pixel integer x and y indexes projected on orthoganal to the beam plane at z.

           Parameters

           - par               : int or psana.Event() - integer run number or psana event object.
           - zplane            : float - z coordinate of the orthoganal to the beam plane for projection
           - pix_scale_size_um : float - pixel scale size [um] which is used to convert coordinate in index.
           - xy0_off_pix       : list of floats - image (x,y) origin offset in order to make all indexes positively defined.
           - do_update         : bool - force to update cached array.

           Returns

           - (np.array, np.array) - list of two arrays of pixel x and y indexes, respectively.
        """
        rnum = self.runnum(par)
        iX_at_Z, iY_at_Z = self.pyda.indexes_xy_at_z(par, zplane, pix_scale_size_um, xy0_off_pix, do_update)
        return self._shaped_array_(rnum, iX_at_Z), self._shaped_array_(rnum, iY_at_Z)


    def point_indexes(self, par, pxy_um=(0,0), pix_scale_size_um=None, xy0_off_pix=None, cframe=gu.CFRAME_PSANA, fract=False):
        """Returns int of float (for fract) (ix, iy) indexes of the point (x,y) specified in [um].

           Parameters

           - par               : int or psana.Event() - integer run number or psana event object.
           - pxy_um            : list of two float values - coordinates of the point in the detector frame, default (0,0)
           - pix_scale_size_um : float - pixel scale size [um] which is used to convert coordinate in index.
           - xy0_off_pix       : list of floats - image (x,y) origin offset in order to make all indexes positively defined.
           - fract             : bool - if True - force return fractional indexes.
           - cframe            : int - coordinate frame 0=psana or 1=LAB frame.

           Returns

           - tuple - (ix, iy) tuple of two indexes associated with input point coordinates.
        """
        ix, iy = self.pyda.point_indexes(par, pxy_um, pix_scale_size_um, xy0_off_pix, cframe, fract)
        return ix, iy


    def pixel_size(self, par):
        """Returns pixel scale size in [um].

           Parameters

           - par : int or psana.Event() - integer run number or psana event object.

           Returns

           - float - pixel size in [um].
        """
        psize = self.pyda.pixel_size(par) # Ex: 109.92 [um]
        return psize if psize != 1 else None


    def move_geo(self, par, dx, dy, dz):
        """Moves detector.

           Parameters

           - par : int or psana.Event() - integer run number or psana event object.
           - dx, dy, dz : float - three coordinate increments [um] of the detector motion.
        """
        self.pyda.move_geo(par, dx, dy, dz)


    def tilt_geo(self, par, dtx, dty, dtz):
        """Tilts detector.

           Parameters

           - par : int or psana.Event() - integer run number or psana event object.
           - dtx, dty, dtz : float - three angular increments [deg] of the detector tilt.
        """
        self.pyda.tilt_geo(par, dtx, dty, dtz)


    def psf(self, par, cframe=gu.CFRAME_LAB):
        """Returns PSF vectors for asics as a tuple psf[<number-of-asics>][3][3].

           Parameters

           - par : int or psana.Event() - integer run number or psana event object.
           - cframe : int - coordinate frame 0=psana or 1=LAB frame.

           Returns

           - tuple of tuples - per-asic psf vectors.
        """
        return self.geometry(par).psf(cframe)


    def data_psf(self, par, data):
        """Converts psana per-panel data to PSF per-asic shaped data array.

           Parameters

           - par : int or psana.Event() - integer run number or psana event object.
           - data : psana-formatted data array.

           Returns

           - np.array - PSF per-asic shaped data array.
        """
        return self.geometry(par).data_psf(data)


    def pixel_coords_psf(self, par, cframe=1):
        return self.geometry(par).pixel_coords_psf(cframe)


    def image_xaxis(self, par, pix_scale_size_um=None, x0_off_pix=None):
        """Returns array of pixel x coordinates associated with image x-y grid.

           Parameters

           - par : int or psana.Event() - integer run number or psana event object.
           - pix_scale_size_um : float - pixel scale size [um] which is used to convert coordinate in index.
           - x0_off_pix        : float - origin x coordinate offset in number of pixels

           Returns

           - np.array - array of pixel x coordinates of image x-y grid.
        """
        return self.pyda.image_xaxis(par, pix_scale_size_um, x0_off_pix)


    def image_yaxis(self, par, pix_scale_size_um=None, y0_off_pix=None):
        """Returns array of pixel x coordinates associated with image x-y grid.

           Parameters

           - par : int or psana.Event() - integer run number or psana event object.
           - pix_scale_size_um : float - pixel scale size [um] which is used to convert coordinate in index.
           - y0_off_pix        : float - origin y coordinate offset in number of pixels

           Returns

           - np.array - array of pixel y coordinates of image x-y grid.
        """
        return self.pyda.image_yaxis(par, pix_scale_size_um, y0_off_pix)


    def image(self, evt, nda_in=None, pix_scale_size_um=None, xy0_off_pix=None, do_update=False):
        """Returns 2-d array of intensities for imaging.

           Parameters

           - evt               : psana.Event() - psana event object.
           - nda_in            : input n-d array which needs to be converted in image; default - use calib methood.
           - pix_scale_size_um : float - pixel scale size [um] which is used to convert coordinate in index.
           - xy0_off_pix       : list of floats - image (x,y) origin offset in order to make all indexes positively defined.
           - do_update         : bool - force to update cached array.

           Returns

           - np.array - 2-d array of intensities for imaging.
        """
        rnum = self.runnum(evt)
        nda = nda_in if nda_in is not None else self.calib(evt)

        if nda is None: return None

        shape = nda.shape
        if self.reshape_to_3d and len(shape)==3 and shape[0]==1: nda.shape = shape[1:]

        if len(nda.shape)==2 and not(self.dettype in (gu.EPIX100A, gu.EPIX10KA, gu.JUNGFRAU)):
            return nda

        if self.is_cspad2x2(): nda = two2x1ToData2x2(nda) # convert to DAQ shape for cspad2x2
        nda_img = np.array(nda, dtype=np.double).flatten()
        return self._nda_or_none_(self.pyda.image(rnum, nda_img, pix_scale_size_um, xy0_off_pix, do_update))


    def ndarray_from_image(self, par, image, pix_scale_size_um=None, xy0_off_pix=None, do_update=False):
        """Returns n-d array of intensities extracted from image using image bin indexes.

           Parameters

           - par               : int or psana.Event() - integer run number or psana event object.
           - image             : np.array - input 2-d array which will be converted to n-d array.
           - pix_scale_size_um : float - pixel scale size [um] which is used to convert coordinate in index.
           - xy0_off_pix       : list of floats - image (x,y) origin offset in order to make all indexes positively defined.
           - do_update         : bool - force to update cached array.

           Returns

           - np.array - n-d array of intensities made from image.
        """
        return self._shaped_array_(par, self.pyda.ndarray_from_image(par, image, pix_scale_size_um, xy0_off_pix, do_update))


    def save_txtnda(self, fname='nda.txt', ndarr=None, cmts=(), fmt='%.1f', verbos=False, addmetad=True):
        """Saves n-d array in the formatted text file with hash-type cumments and metadata.

           Parameters

           - fname    : str - output file name.
           - ndarr    : np.array - array of numerical values to save in text file.
           - cmts     : list of str - list of strings which will be saved as comments in the file header.
           - fmt      : str - format of values in the file.
           - verbose  : bool - True/False = on/off messages from this method (about saved file etc.)
           - addmetad : bool - True/False = on/off saving methadata (data type, and shape info) in file.
        """
        list_cmts = list(cmts)
        list_cmts.append('SOURCE  %s' % gu.string_from_source(self.source))
        # DO NOT ADD metadata for CSPAD and CSPAD2x2
        addmd = False if ndarr.size in (2*185*388, 32*185*388) else addmetad
        self.pyda.save_txtnda(fname, ndarr, list_cmts, fmt, verbos, addmd)


    def save_asdaq(self, fname='nda.txt', ndarr=None, cmts=(), fmt='%.1f', verbos=False, addmetad=True):
        """Saves per-pixel n-d array shaped and ordered as in DAQ.

           The same functionality as in the method save_txtnda(...), but array is shuffled to DAQ order.
           Currently re-shuffle pixels for cspad2x2 only from natural shape=(2,185,388) to daq shape (185,388,2).
           For all other detectors n-d array is saved unchanged.

           Parameters

           - fname    : str - output file name.
           - ndarr    : np.array - array of numerical values to save in text file.
           - cmts     : list of str - list of strings which will be saved as comments in the file header.
           - fmt      : str - format of values in the file.
           - verbose  : bool - True/False = on/off messages from this method (about saved file etc.)
           - addmetad : bool - True/False = on/off saving methadata (data type, and shape info) in file.
        """
        is_cspad2x2_natural = (ndarr.size == 2*185*388 and len(ndarr.shape)>1 and ndarr.shape[-1] == 388)
        nda = two2x1ToData2x2(ndarr) if is_cspad2x2_natural else ndarr
        self.save_txtnda(fname, nda, cmts, fmt, verbos, addmetad)


    def load_txtnda(self, fname):
        """Returns n-d array loaded from specified formatted text file.

           Parameters

           - fname : str - input file name.

           Returns

           - np.array - array with values loaded from file,
                      shaped in accordance with metadata (if available).
                      If metadata is missing, output array will have 2- or 1-d shape;
                      spaces and <next-lene> characters in the text file are used to find the shape of the array.
        """
        return self.pyda.load_txtnda(fname)


    def photons(self, evt, nda_calib=None, mask=None, adu_per_photon=None, thr_fraction=0.9):
        """Returns 2-d or 3-d array of integer number of merged photons - algorithm suggested by Chuck.

           Parameters

           - evt            : psana.Event() - psana event object.
           - nda_calib      : (float, double, int, int16) numpy.array - calibrated data, float number of photons per pixel.
           - mask           : (uint8) numpy.array user defined mask.
           - adu_per_photon : float conversion factor which is applied as nda_calib/adu_per_photon.
           - thr_fraction   : float - fraction of the merged intensity which gets converted to one photon, def=0.9.

           Returns

           - np.array - 2-d or 3-d array of integer number of merged photons.
        """

        if self.alg_photons is None:
            from Detector.AlgoAccess import alg_photons; self.alg_photons = alg_photons

        nda = nda_calib if nda_calib is not None else self.calib(evt)
        if nda is None: return None

        if adu_per_photon is not None and adu_per_photon !=0:
            f = 1./adu_per_photon
            nda *= f

        msk = self.mask(evt, calib=True, status=True, edges=True, central=True, unbond=True, unbondnbrs=True) \
              if mask is None else mask

        return self.alg_photons(nda, msk, thr_fraction)


    def shape_config(self, env):
        return self.pyda.shape_config(env)


if __name__ == "__main__":
    """Self-test method.
       Usage: python <path>/AreaDetector.py <test-number>
    """

    from time import time
    import psana

    ntest = int(sys.argv[1]) if len(sys.argv)>1 else 1
    print('Test # %d' % ntest)
    dsname, src                = 'exp=cxif5315:run=169', psana.Source('DetInfo(CxiDs2.0:Cspad.0)')
    if   ntest==2: dsname, src = 'exp=meca1113:run=376', psana.Source('DetInfo(MecTargetChamber.0:Cspad2x2.1)')
    elif ntest==3: dsname, src = 'exp=amob5114:run=403', psana.Source('DetInfo(Camp.0:pnCCD.0)')
    elif ntest==4: dsname, src = 'exp=xppi0614:run=74',  psana.Source('DetInfo(NoDetector.0:Epix100a.0)')
    print('Example for\n  dataset: %s\n  source: %s' % (dsname, src))

    ds = psana.DataSource(dsname)

    env = ds.env()
    cls = env.calibStore()
    eviter = ds.events()
    evt = next(eviter)
    rnum = evt.run()

    for key in evt.keys(): print(key)

    det = AreaDetector(src, env, pbits=0)

    nda = det.pedestals(rnum)
    print('\nnda:\n', nda)
    print('nda.dtype: %s nda.shape: %s' % (nda.dtype, nda.shape))

    t0_sec = time()
    nda = det.raw(evt)
    print('\nConsumed time to get raw data (sec) =', time()-t0_sec)
    print('\nnda:\n', nda.flatten()[0:10])

    sys.exit ('Self test is done')

# EOF
