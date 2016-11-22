#--------------------------------------------------------------------------
# File and Version Information:
#  $Id$
#
# Description:
#------------------------------------------------------------------------

"""Class contains a collection of direct python access methods to detector associated information.

Access method to calibration and geometry parameters, raw data, etc.
Low level implementation is done on python.

@see classes
\n  :py:class:`Detector.PyDetector` - factory for different detectors
\n  :py:class:`Detector.DetectorAccess` - c++ access interface to data

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
import numpy as np
import _psana
import Detector.PyDataAccess as pda

#import Detector.GlobalUtils as gu
import PSCalib.GlobalUtils as gu

from PSCalib.CalibParsStore import cps
from PSCalib.CalibFileFinder import CalibFileFinder
from PSCalib.GeometryAccess import GeometryAccess, img_from_pixel_arrays
from PSCalib.NDArrIO import save_txt, load_txt

#from pypdsdata.xtc import TypeId  # types from pdsdata/xtc/TypeId.hh, ex: TypeId.Type.Id_CspadElement

##-----------------------------

##-----------------------------

class PyDetectorAccess :
    """Direct python access to detector data.
    """
    GEO_NOT_LOADED     = 0
    GEO_LOADED_CALIB   = 1
    GEO_LOADED_DEFAULT = 2
    GEO_LOADED_DCS     = 3

##-----------------------------

    def __init__(self, source, env, pbits=0) :
        """Constructor.
           - source - data source, ex: _psana.Source('DetInfo(CxiDs2.0:Cspad.0)')
           - env    - environment
           - pbits  - print control bit-word
        """
        #print 'In c-tor DetPyAccess'

        self.source = source
        self.str_src= gu.string_from_source(source)
        self.env    = env
        self.pbits  = pbits
        self.dettype = gu.det_type_from_source(self.str_src)
        self.do_offset = False # works for camera
        self.correct_time = True # works for acqiris
        self.do_calib_imp = False # works for imp 
        if self.pbits & 1 : self.print_attributes()

        self.cpst = None 
        self.runnum_cps = -1

        self.geo = None 
        self.runnum_geo = -1
        self.mbits      = None

        self.cfg_gain_mask_is_loaded = False
        self.runnum_cfg = -1
        self._gain_mask = None

        self.counter_cspad2x2_msg = 0
        self.reshape_to_3d = False

##-----------------------------

    def cpstore(self, par) : # par = evt or runnum

        runnum = par if isinstance(par, int) else par.run()
        #print 80*'_'
        #print 'cpstore XXX runnum = %d' % runnum
        #print 'cpstore XXX par', par,
        #print 'XXX  isinstance(par, psana.Event)', isinstance(par, _psana.Event)

        # for 1st entry and when runnum is changing:
        if runnum != self.runnum_cps or self.cpst is None :
            self.runnum_cps = runnum
            group = gu.dic_det_type_to_calib_group[self.dettype]
            #self.cpst = cps.Create(self.env.calibDir(), group, self.str_src, runnum, self.pbits)
            self.cpst = cps.CreateForEvtEnv(self.env.calibDir(), group, self.str_src, par, self.env, self.pbits)
            if self.pbits & 1 : print 'PSCalib.CalibParsStore object is created for run %d' % runnum

        return self.cpst

##-----------------------------

    def default_geometry(self) :
        """Returns default geometry object for some of detectors"""
        import CalibManager.AppDataPath as apputils

        if self.dettype == gu.EPIX100A :
            fname = apputils.AppDataPath('Detector/geometry-def-epix100a.data').path()
            if self.pbits : print '%s: Load default geometry from file %s' % (self.__class__.__name__, fname)
            return GeometryAccess(fname, 0377 if self.pbits else 0)

        return None

##-----------------------------

    def geoaccess_dcs(self, evt) :
        #self.geo_load_status = self.GEO_NOT_LOADED
        #self.geo_load_status = self.GEO_LOADED_DCS
        import PSCalib.DCMethods as dcm

        cdir = self.env.calibDir()
        
        #print 'XXX  par is Event:', isinstance(evt, _psana.Event)
        #print 'XXX: cdir, src, pbits, dettype:', cdir, self.str_src, self.pbits, self.dettype

        data = dcm.get_constants(evt, self.env, self.str_src, ctype=gu.GEOMETRY, calibdir=cdir, vers=None, verb=True)

        if data is None : return

        #for s in data : print 'XXX: %s' % s
        #import tempfile
        #fntmp = tempfile.NamedTemporaryFile(mode='r+b',suffix='.data')
        #print 'XXX Save constants in tmp file: %s' % fntmp.name
        #save_txt(fntmp.name, data, cmts='', fmt='%.1f')
        #self.geo = GeometryAccess(fntmp.name, 0377 if self.pbits else 0)

        self.geo = GeometryAccess(pbits=0377 if self.pbits else 0)
        self.geo.load_pars_from_str(data)
        self.geo.print_list_of_geos()

##-----------------------------

    def geoaccess_calib(self, runnum) :

        group = gu.dic_det_type_to_calib_group[self.dettype]
        cff = CalibFileFinder(self.env.calibDir(), group, 0377 if self.pbits else 0)
        fname = cff.findCalibFile(self.str_src, 'geometry', runnum)
        if fname :
            self.geo = GeometryAccess(fname, 0377 if self.pbits else 0)
            if self.pbits & 1 : print 'PSCalib.GeometryAccess object is created for run %d' % runnum
            if self.geo.valid : self.geo_load_status = self.GEO_LOADED_CALIB
        else     :
            self.geo = None
            if self.pbits & 1 : print 'WARNING: PSCalib.GeometryAccess object is NOT created for run %d - geometry file is missing.' % runnum

        if self.geo is None :
            # if geo object is still missing try to load default geometry
            self.geo = self.default_geometry()
            if self.geo is not None : self.geo_load_status = self.GEO_LOADED_DEFAULT

##-----------------------------

    def geoaccess(self, par) : # par = evt or runnum

        runnum = par if isinstance(par, int) else par.run()
        #print 'geoaccess XXX runnum = %d' % runnum

        # for 1st entry and when runnum is changing:
        if  runnum != self.runnum_geo or self.geo is None :

            self.geo_load_status = self.GEO_NOT_LOADED

            self.runnum_geo = runnum
            self.geoaccess_calib(runnum)

            # fallback support from DCS
            if self.geo is None or self.geo_load_status == self.GEO_LOADED_DEFAULT:
                self.geoaccess_dcs(par)

            # arrays for caching
            self.iX             = None 
            self.iY             = None 
            self.coords_x_arr   = None 
            self.coords_y_arr   = None 
            self.coords_z_arr   = None
            self.areas_arr      = None
            self.mask_geo_arr   = None
            self.mbits          = None
            self.pixel_size_val = None

        return self.geo

##-----------------------------

    def print_attributes(self) :
        print 'PyDetectorAccess attributes:\n  source: %s\n  dtype : %d\n  pbits : %d' % \
              (self.source, self.dettype, self.pbits), \
              '\n  do_offset (Camera): %s\n  correct_time (Acqiris): %s\n  do_calib_imp (Imp): %s' % \
              (self.do_offset, self.correct_time, self.do_calib_imp)

##-----------------------------

    def set_env(self, env) :
        self.env = env

##-----------------------------

    def set_source(self, source) :
        self.source = source
        self.str_src = gu.string_from_source(source)

##-----------------------------

    def pedestals(self, par) : # par: evt or runnum(int)
        return self.cpstore(par).pedestals()
    
##-----------------------------

    def pixel_rms(self, par) :
        return self.cpstore(par).pixel_rms()

##-----------------------------

    def pixel_gain(self, par) :
        return self.cpstore(par).pixel_gain()

##-----------------------------

    def pixel_mask(self, par) :
        return self.cpstore(par).pixel_mask()

##-----------------------------

    def pixel_bkgd(self, par) :
        return self.cpstore(par).pixel_bkgd()

##-----------------------------

    def pixel_status(self, par) :
        return self.cpstore(par).pixel_status()

##-----------------------------

    def common_mode(self, par) :
        return self.cpstore(par).common_mode()

##-----------------------------

    def ndim(self, par=0, ctype=gu.PEDESTALS) :
        sh = np.array(self.shape())
        if sh is not None : return sh.size
        return self.cpstore(par).ndim(ctype)

##-----------------------------

    def size(self, par=0, ctype=gu.PEDESTALS) :
        sh = np.array(self.shape())
        if sh is not None : return sh.prod()
        return self.cpstore(par).size(ctype)

##-----------------------------

    def shape_calib(self, par, ctype=gu.PEDESTALS) :
        return self.cpstore(par).shape(ctype)

##-----------------------------

    def status(self, par, ctype=gu.PEDESTALS) :
        return self.cpstore(par).status(ctype)

##-----------------------------
##-----------------------------
##-----------------------------

    def _shaped_geo_array(self, arr) :
        if arr is None : return None
        if self.dettype == gu.EPIX100A : arr.shape = (704, 768)
        #if self.dettype == gu.CSPAD    : arr.shape = (32, 185, 388)
        return arr

##-----------------------------

    def _update_coord_arrays(self, par, do_update=False) :
        """ Returns True if pixel index arrays are available, othervise False.
        """
        if self.geoaccess(par) is None : return False
        else :
            if  self.coords_x_arr is None or do_update :
                self.coords_x_arr, self.coords_y_arr, self.coords_z_arr = self.geo.get_pixel_coords()
            if  self.coords_x_arr is None : return False
        return True

##-----------------------------

    def coords_x(self, par) :
        if not self._update_coord_arrays(par) : return None
        return self._shaped_geo_array(self.coords_x_arr)

##-----------------------------

    def coords_y(self, par) :
        if not self._update_coord_arrays(par) : return None
        return self._shaped_geo_array(self.coords_y_arr)

##-----------------------------

    def coords_z(self, par) :
        if not self._update_coord_arrays(par) : return None
        return self._shaped_geo_array(self.coords_z_arr)

##-----------------------------

    def coords_xy(self, par) :
        if not self._update_coord_arrays(par) : return None
        return self._shaped_geo_array(self.coords_x_arr), self._shaped_geo_array(self.coords_y_arr)

##-----------------------------

    def coords_xyz(self, par) :
        if not self._update_coord_arrays(par) : return None
        return self._shaped_geo_array(self.coords_x_arr),\
               self._shaped_geo_array(self.coords_y_arr),\
               self._shaped_geo_array(self.coords_z_arr)

##-----------------------------

    def areas(self, par) :
        if self.geoaccess(par) is None : return None
        else :
            if  self.areas_arr is None : 
                self.areas_arr = self.geo.get_pixel_areas()
        return  self._shaped_geo_array(self.areas_arr)

##-----------------------------

    # mbits = +1-edges; +2-wide central cols; +4-non-bond; +8/+16-four/eight non-bond neighbors
    def mask_geo(self, par, mbits=15) :

        if mbits != self.mbits : # check if update is required
            self.mbits = mbits
            self.mask_geo_arr = None

        if self.geoaccess(par) is None : return None
        else :
            if  self.mask_geo_arr is None : 
                self.mask_geo_arr = self.geo.get_pixel_mask(mbits=mbits)
        return  self._shaped_geo_array(self.mask_geo_arr)

##-----------------------------

    def _update_index_arrays(self, par, pix_scale_size_um=None, xy0_off_pix=None, do_update=False) :
        """ Returns True if pixel index arrays are available, othervise False.
        """
        if self.geoaccess(par) is None : return False
        else :
            if  self.iX is None or do_update :
                self.iX, self.iY = self.geo.get_pixel_coord_indexes(oname=None, oindex=0,\
                                                       pix_scale_size_um=pix_scale_size_um,\
                                                       xy0_off_pix=xy0_off_pix, do_tilt=True)
            if  self.iX is None : return False
        return True

##-----------------------------

    def indexes_x(self, par, pix_scale_size_um=None, xy0_off_pix=None, do_update=False) :
        """Returns pixel index array iX."""
        if not self._update_index_arrays(par, pix_scale_size_um, xy0_off_pix, do_update) : return None
        return self._shaped_geo_array(self.iX)

##-----------------------------

    def indexes_y(self, par, pix_scale_size_um=None, xy0_off_pix=None, do_update=False) :
        """Returns pixel index array iY."""
        if not self._update_index_arrays(par, pix_scale_size_um, xy0_off_pix, do_update) : return None
        return self._shaped_geo_array(self.iY)

##-----------------------------

    def indexes_xy(self, par, pix_scale_size_um=None, xy0_off_pix=None, do_update=False) :
        """Returns two pixel index arrays iX and iY."""
        if not self._update_index_arrays(par, pix_scale_size_um, xy0_off_pix, do_update) : return None
        if self.iX is None : return None, None # single None is not the same as (None, None) !
        return self._shaped_geo_array(self.iX), self._shaped_geo_array(self.iY)

##-----------------------------

    def point_indexes(self, par, pxy_um=(0,0), pix_scale_size_um=None, xy0_off_pix=None) :
        """Returns ix, iy indexes of the point p_um x,y coordinates in [um]"""
        if self.geoaccess(par) is None : return None, None
        ix, iy = self.geo.point_coord_indexes(p_um=pxy_um, oname=None, oindex=0,\
                                              pix_scale_size_um=pix_scale_size_um,\
                                              xy0_off_pix=xy0_off_pix, do_tilt=True)
        return ix, iy

##-----------------------------

    def pixel_size(self, par) :
        if self.geoaccess(par) is None : return None
        else :
            if  self.pixel_size_val is None : 
                self.pixel_size_val = self.geo.get_pixel_scale_size()
        return  self.pixel_size_val

##-----------------------------

    def move_geo(self, par, dx, dy, dz) :
        if self.geoaccess(par) is None : pass
        else : return self.geo.move_geo(None, 0, dx, dy, dz)

##-----------------------------

    def tilt_geo(self, par, dtx, dty, dtz) :
        if self.geoaccess(par) is None : pass
        else : return self.geo.tilt_geo(None, 0, dtx, dty, dtz)

##-----------------------------

    def image_xaxis(self, par, pix_scale_size_um=None, x0_off_pix=None) :
        pix_size = pix_scale_size_um if pix_scale_size_um is not None else self.pixel_size(par)
        carr = self.coords_x(par)
        if carr is None : return None
        cmin, cmax = carr.min(), carr.max() + 0.5*pix_size
        if x0_off_pix is None :
            return np.arange(cmin, cmax, pix_size)
        else :
            return np.arange(cmin-pix_size*x0_off_pix, cmax, pix_size)

##-----------------------------

    def image_yaxis(self, par, pix_scale_size_um=None, y0_off_pix=None) :
        pix_size = pix_scale_size_um if pix_scale_size_um is not None else self.pixel_size(par)
        carr = self.coords_y(par)
        if carr is None : return None
        cmin, cmax = carr.min(), carr.max() + 0.5*pix_size
        if y0_off_pix is None :
            return np.arange(cmin, cmax, pix_size)
        else :
            return np.arange(cmin-pix_size*y0_off_pix, cmax, pix_size)

##-----------------------------

    def image(self, par, img_nda, pix_scale_size_um=None, xy0_off_pix=None, do_update=False) :
        if not self._update_index_arrays(par, pix_scale_size_um, xy0_off_pix, do_update) : return None
        return img_from_pixel_arrays(self.iX, self.iY, img_nda)

##-----------------------------

    def do_reshape_2d_to_3d(self, flag=False) :
        self.reshape_to_3d = flag

##-----------------------------

    def ndarray_from_image(self, par, image, pix_scale_size_um=None, xy0_off_pix=None, do_update=False) :

        if image is None : return None
        if len(image.shape) != 2 : return None

        # 2016-06-05 return image if reshaping to 3d is requested and geometry is missing
        # !!! there is no check that original array is 2d or specific detector type. 
        if self.reshape_to_3d and self.geoaccess(par) is None : 
            return np.array(image, copy=True)

        if not self._update_index_arrays(par, pix_scale_size_um, xy0_off_pix, do_update) : return None
        return self._shaped_geo_array(np.array([image[r,c] for r,c in zip(self.iX, self.iY)]))

##-----------------------------
##-----------------------------
##-----------------------------
##-----------------------------

    def inst(self) :
        return self.env.instrument()

##-----------------------------

    def print_config(self, evt) :
        print '%s:print_config(evt) - is not implemented in pythonic version' % self.__class__.__name__

##-----------------------------

    def set_print_bits(self, pbits) :
        self.pbits  = pbits

##-----------------------------

    def set_do_offset(self, do_offset=False) :
        """On/off application of offset in raw_data_camera(...)
        """
        self.do_offset = do_offset

##-----------------------------

    def set_correct_acqiris_time(self, correct_time=True) :
        """On/off correction of time for acqiris
        """
        self.correct_time = correct_time

##-----------------------------

    def set_calib_imp(self, do_calib_imp=False) :
        """On/off imp calibration
        """
        self.do_calib_imp = do_calib_imp

##-----------------------------

    def gain_mask(self, par, gain=None) :
        """Returns a gain map extracted from detector configuration data.
           Currently implemented for CSPAD only.
           Returns None for other detectors or missing configuration for CSPAD.
        """
        runnum = par if isinstance(par, int) else par.run()

        if runnum == self.runnum_cfg :
            if self.cfg_gain_mask_is_loaded :
                return self._gain_mask
        else :
            self.runnum_cfg = runnum
            self.cfg_gain_mask_is_loaded = False

        if   self.dettype == gu.CSPAD    : self._gain_mask = self.cspad_gain_mask(gain) 
        elif self.dettype == gu.CSPAD2X2 : self._gain_mask = self.cspad2x2_gain_mask(gain) 
        else :
            self.cfg_gain_mask_is_loaded = True
            self._gain_mask = None
        return self._gain_mask

##-----------------------------

    def gain_mask_non_zero(self, par, gain=None) :
        """The same as gain_mask, but returns None if ALL pixels have high gain"""

        gm = self.gain_mask(par, gain)

        if gm is not None :
            if not gm.any() : return None 

        return gm

##-----------------------------

    def raw_data(self, evt, env) :

        #print 'TypeId.Type.Id_CspadElement: ', TypeId.Type.Id_CspadElement
        #print 'TypeId.Type.Id_CspadConfig: ',  TypeId.Type.Id_CspadConfig

        if   self.dettype == gu.CSPAD      : return self.raw_data_cspad(evt, env)     # 3   ms
        elif self.dettype == gu.CSPAD2X2   : return self.raw_data_cspad2x2(evt, env)  # 0.6 ms
        elif self.dettype == gu.PRINCETON  : return self.raw_data_princeton(evt, env) # 0.7 ms
        elif self.dettype == gu.PNCCD      : return self.raw_data_pnccd(evt, env)     # 0.8 ms
        elif self.dettype == gu.ANDOR      : return self.raw_data_andor(evt, env)     # 0.1 ms
        elif self.dettype == gu.ANDOR3D    : return self.raw_data_andor(evt, env)
        elif self.dettype == gu.FCCD960    : return self.raw_data_fccd960(evt, env)   # 11  ms
        elif self.dettype == gu.EPIX100A   : return self.raw_data_epix(evt, env)      # 0.3 ms
        elif self.dettype == gu.EPIX10K    : return self.raw_data_epix(evt, env)
        elif self.dettype == gu.EPIX       : return self.raw_data_epix(evt, env)
        elif self.dettype == gu.ACQIRIS    : return self.raw_data_acqiris(evt, env)
        elif self.dettype == gu.OPAL1000   : return self.raw_data_camera(evt, env)    # 1 ms
        elif self.dettype == gu.OPAL2000   : return self.raw_data_camera(evt, env)
        elif self.dettype == gu.OPAL4000   : return self.raw_data_camera(evt, env)
        elif self.dettype == gu.OPAL8000   : return self.raw_data_camera(evt, env)
        elif self.dettype == gu.ORCAFL40   : return self.raw_data_camera(evt, env)
        elif self.dettype == gu.TM6740     : return self.raw_data_camera(evt, env)    # 0.24 ms
        elif self.dettype == gu.QUARTZ4A150: return self.raw_data_camera(evt, env)
        elif self.dettype == gu.RAYONIX    : return self.raw_data_camera(evt, env)
        elif self.dettype == gu.IMP        : return self.raw_data_imp(evt, env)
        elif self.dettype == gu.FCCD       : return self.raw_data_camera(evt, env)
        elif self.dettype == gu.TIMEPIX    : return self.raw_data_timepix(evt, env)
        elif self.dettype == gu.FLI        : return self.raw_data_fli(evt, env)
        elif self.dettype == gu.PIMAX      : return self.raw_data_pimax(evt, env)
        else                               : return None

##-----------------------------

    def raw_data_cspad(self, evt, env) :

        # data object
        d = pda.get_cspad_data_object(evt, self.source)        
        if d is None :
            if self.pbits & 1 : print 'cspad data object is not found'
            return None
    
        # configuration from data
        c = pda.get_cspad_config_object(env, self.source)
        if c is None :
            if self.pbits & 1 : print 'cspad config object is not found'
            return None
    
        nquads   = d.quads_shape()[0]
        nquads_c = c.numQuads()

        #print 'd.TypeId: ', d.TypeId
        if self.pbits & 8 : print 'nquads in data: %d and config: %d' % (nquads, nquads_c)

        arr = np.zeros((4,8,185,388), dtype=np.int16) if nquads<4 else np.empty((4,8,185,388), dtype=np.int16)

        for iq in range(nquads) :
            q = d.quads(iq)
            qnum = q.quad()
            qdata = q.data()
            roim = c.roiMask(qnum)
            if self.pbits & 8 : print 'qnum: %d  qdata.shape: %s, mask: %d' % (qnum, str(qdata.shape), roim)
    
            #roim = 0375 # for test only        
            if roim == 0377 :
                arr[qnum,:] = qdata

            else :
                if self.pbits : print 'PyDetectorAccessr: quad configuration has non-complete mask = %d of included 2x1' % roim
                qdata_full = np.zeros((8,185,388), dtype=qdata.dtype)
                i = 0
                for s in range(8) :
                    if roim & (1<<s) :
                        qdata_full[s,:] = qdata[i,:]
                        i += 1
                arr[qnum,:,:] = qdata_full
    
        if self.pbits & 8 : print 'arr.shape: ', arr.shape
        arr.shape = (32,185,388)
        return arr
    
##-----------------------------

    def raw_data_cspad2x2(self, evt, env) :
        # data object
        d = pda.get_cspad2x2_data_object(evt, self.source)
        if d is None : return None

        # configuration object
        c = pda.get_cspad2x2_config_object(env, self.source)
        if c is None :
            if self.pbits and self.counter_cspad2x2_msg <3 :
                print 'WARNING PyDetectorAccess: missing configuration object for source %s' % (self.str_src)
                if self.counter_cspad2x2_msg == 2 : print 'Stop WARNING messages for %s configuration' % self.str_src
                self.counter_cspad2x2_msg += 1
            #return None

        if c.roiMask() != 3 :
            if self.pbits and self.counter_cspad2x2_msg <3 :
                print 'WARNING PyDetectorAccess: configuration of %s has non-complete mask=%d of included 2x1' % (self.str_src, c.roiMask())
                if self.counter_cspad2x2_msg == 2 : print 'Stop WARNING messages for %s configuration' % self.str_src
                self.counter_cspad2x2_msg += 1

        return d.data()

##-----------------------------

    def raw_data_camera(self, evt, env) :
        # data object
        d = pda.get_camera_data_object(evt, self.source)
        if d is None : return None
    
        # configuration object
        #c = pda.get_camera_config_object(env, self.source)
        #if c is None : return None

        #print 'data width: %d, height: %d, depth: %d, offset: %f' % (d.width(), d.height(), d.depth(), d.offset())
        offset = d.offset()
        
        d16 = d.data16()
        if d16 is not None and d16 != [] :
            if self.do_offset : return np.array(d16, dtype=np.int32) - d.offset()        
            else              : return d16
        
        d8 = d.data8()
        if d8 is not None and d8 != [] : 
            if self.do_offset : return np.array(d8, dtype=np.int32) - d.offset() 
            else              : return d8

        return None

##-----------------------------

    def raw_data_fccd960(self, evt, env) :
        # data object
        d = pda.get_camera_data_object(evt, self.source)
        if d is None : return None
    
        # configuration object
        #c = pda.get_camera_config_object(env, self.source)
        #if c is None : return None

        arr = d.data16()
        if arr is None : return None

        arr_c = (arr>>13)&03
        arr_v = arr&017777
        #print 'arr_c:\n', arr_c
        #print 'arr_v:\n', arr_v

        return np.select([arr_c==0, arr_c==1, arr_c==3], \
                         [arr_v,    arr_v<<2, arr_v<<3])

##-----------------------------

    def raw_data_princeton(self, evt, env) :
        # data object
        d = pda.get_princeton_data_object(evt, self.source)
        if d is None : return None

        # configuration object
        #c = pda.get_princeton_config_object(env, self.source)
        #if c is None : return None
        #print 'config: width: %d, height: %d' % (c.width(), c.height())

        nda = d.data()
        return nda if nda is not None else None

##-----------------------------

    def raw_data_pnccd(self, evt, env) :
        # data object
        #print '=== in raw_data_pnccd'
        #d = evt.get(_psana.PNCCD.FullFrameV1, self.source)
        #d = evt.get(_psana.PNCCD.FramesV1, self.source)
        d = pda.get_pnccd_data_object(evt, self.source)
        if d is None : return None

        #c = pda.get_pnccd_config_object(env, self.source)
        #if c is None : return None
        #print 'config: numLinks: %d, payloadSizePerLink: %d' % (d.numLinks(), c.payloadSizePerLink())

        arr = []
        nlinks = d.numLinks()
        for i in range(nlinks) :
            frame = d.frame(i)
            fdata = frame.data()
            arr.append(fdata)
            #print '   data.shape: %s' % (str(fdata.shape))

        nda = np.array(arr)
        #print 'nda.shape: ', nda.shape
        return nda

##-----------------------------

    def raw_data_andor(self, evt, env) :

        d = pda.get_andor_data_object(evt, self.source)
        if d is None : return None

        if self.pbits & 4 :
            print 'Data object:', d
            print 'shotIdStart = ', d.shotIdStart() 
            print 'readoutTime = ', d.readoutTime()
            print 'temperature = ', d.temperature()

        c = pda.get_andor_config_object(env, self.source)                

        if c is not None and self.pbits & 4 :
            print 'Configuration object:', c
            print 'width              = ', c.width()            
            print 'height             = ', c.height()            
            print 'numSensors         = ', c.numSensors()        
            print 'orgX               = ', c.orgX()              
            print 'orgY               = ', c.orgY()              
            print 'binX               = ', c.binX()              
            print 'binY               = ', c.binY()              
            print 'exposureTime       = ', c.exposureTime()      
            print 'coolingTemp        = ', c.coolingTemp ()      
            print 'fanMode            = ', c.fanMode ()          
            print 'baselineClamp      = ', c.baselineClamp()     
            print 'highCapacity       = ', c.highCapacity()      
            print 'gainIndex          = ', c.gainIndex()         
            print 'readoutSpeedIndex  = ', c.readoutSpeedIndex() 
            print 'exposureEventCode  = ', c.exposureEventCode() 
            print 'exposureStartDelay = ', c.exposureStartDelay()
            print 'numDelayShots      = ', c.numDelayShots()     
            print 'frameSize          = ', c.frameSize()         
            print 'numPixelsX         = ', c.numPixelsX()        
            print 'numPixelsY         = ', c.numPixelsY()        
            print 'numPixelsPerSensor = ', c.numPixelsPerSensor()
            print 'numPixels          = ', c.numPixels()         

        nda = d.data()
        return nda if nda is not None else None

##-----------------------------

    def raw_data_epix(self, evt, env) :
        # data object
        d = pda.get_epix_data_object(evt, self.source)
        if d is None : return None

        # configuration object
        #c = pda.get_epix_config_object(env, self.source)
        #if c is None : return None

        #print 'config: rows: %d, cols: %d, asics: %d' % (c.numberOfRows(), c.numberOfColumns(), c.numberOfAsics())
        #print 'config: digitalCardId0: %d, 1: %d' % (c.digitalCardId0(), c.digitalCardId1())
        #print 'config: analogCardId0 : %d, 1: %d' % (c.analogCardId0(),  c.analogCardId1())
        #print 'config: version: %d, asicMask: %d' % (c.version(), c.asicMask())

        nda = d.frame()
        return nda if nda is not None else None

##-----------------------------

    def raw_data_timepix(self, evt, env) :
        # data object
        d = pda.get_timepix_data_object(evt, self.source)
        if d is None : return None

        # configuration object
        #c = pda.get_timepix_config_object(env, self.source)
        #if c is None : return None
        #print 'config: width: %d, height: %d' % (c.width(), c.height())

        nda = d.data()
        return nda if nda is not None else None

##-----------------------------

    def raw_data_fli(self, evt, env) :
        # data object
        d = pda.get_fli_data_object(evt, self.source)
        if d is None : return None

        # configuration object
        #c = pda.get_fli_config_object(env, self.source)
        #if c is None : return None
        #print 'config: width: %d, height: %d' % (c.width(), c.height())

        nda = d.data()
        return nda if nda is not None else None

##-----------------------------

    def raw_data_pimax(self, evt, env) :
        # data object
        d = pda.get_pimax_data_object(evt, self.source)
        if d is None : return None

        # configuration object
        #c = pda.get_pimax_config_object(env, self.source)
        #if c is None : return None
        #print 'config: width: %d, height: %d' % (c.width(), c.height())

        nda = d.data()
        return nda if nda is not None else None

##-----------------------------
##-----------------------------
##-----------------------------
##-----------------------------

    def raw_data_acqiris(self, evt, env) :
        """returns two 2-d ndarrays wf,wt with shape=(nbrChannels, nbrSamples) or None
        """
        # data object
        d = pda.get_acqiris_data_object(evt, self.source)
        if d is None : return None

        # configuration object
        c = pda.get_acqiris_config_object(env, self.source)
        if c is None : return None

        #nchan = d.data_shape()[0]
        nbrChannels = c.nbrChannels()

        h = c.horiz()
        sampInterval = h.sampInterval()
        nbrSamples = h.nbrSamples()

        if self.pbits & 4 : print '  nbrChannels: %d, H-nbrSamples: %d, H-sampInterval: %g' \
           % (nbrChannels, nbrSamples, sampInterval)

        shape = (nbrChannels, nbrSamples)
        wf = np.zeros(shape, dtype=np.float)
        wt = np.zeros(shape, dtype=np.float)

        for chan in range(nbrChannels) :
            elem = d.data(chan)
            vert = c.vert()[chan]

            slope = vert.slope()
            offset= vert.offset()

            nbrSegments     = elem.nbrSegments()
            nbrSamplesInSeg = elem.nbrSamplesInSeg()
            indexFirstPoint = elem.indexFirstPoint()
            tstamps         = elem.timestamp()
            wforms          = elem.waveforms()

            if self.pbits & 4 :
                print '    chan: %d,  nbrSegments: %d,  nbrSamplesInSeg: %d,  indexFirstPoint: %d,' \
                  % (chan, nbrSegments, nbrSamplesInSeg, indexFirstPoint), \
                  '  V-slope: %f,  V-offset: %f,  H-pos[seg=0]: %g' % (slope,  offset, tstamps[0].pos())

            for seg in range(nbrSegments) :
                raw = wforms[seg]
                pos = tstamps[seg].pos()       
                i0_seg = seg * nbrSamplesInSeg + int(pos/sampInterval) if self.correct_time else seg * nbrSamplesInSeg
                size = nbrSamplesInSeg if (i0_seg + nbrSamplesInSeg) <= nbrSamples else nbrSamples - i0_seg

                if self.correct_time :
                    if (indexFirstPoint + size) > nbrSamplesInSeg : size = nbrSamplesInSeg - indexFirstPoint

                    wf[chan, i0_seg:i0_seg+size] = raw[indexFirstPoint:indexFirstPoint+size]*slope - offset
                else :
                    wf[chan, i0_seg:i0_seg+size] = raw[0:size]*slope - offset

                wt[chan, i0_seg:i0_seg+size] = np.arange(size)*sampInterval + pos

        return wf, wt

##-----------------------------

    def raw_data_imp(self, evt, env) :
        """returns ndarray with shape=(4, 1023) or None
        """
        # data object
        d = pda.get_imp_data_object(evt, self.source)
        if d is None : return None

        if self.pbits & 4 :
            # configuration object
            c = pda.get_imp_config_object(env, self.source)
            if c is None : return None

            print "Configuration object for %s" % self.source
            print "  range =",           c.range()
            print "  calRange =",        c.calRange()
            print "  reset =",           c.reset()
            print "  biasData =",        c.biasData()
            print "  calData =",         c.calData()
            print "  biasDacData =",     c.biasDacData()
            print "  calStrobe =",       c.calStrobe()
            print "  numberOfSamples =", c.numberOfSamples()
            print "  trigDelay =",       c.trigDelay()
            print "  adcDelay =",        c.adcDelay()
            
            print "Data object for %s" % self.source
            print "  vc =",          d.vc()
            print "  lane =",        d.lane()
            print "  frameNumber =", d.frameNumber()
            print "  range =",       d.range()
            
            laneStatus = d.laneStatus()
            print "  laneStatus.linkErrCount =",  laneStatus.linkErrCount()
            print "  laneStatus.linkDownCount =", laneStatus.linkDownCount()
            print "  laneStatus.cellErrCount =",  laneStatus.cellErrCount()
            print "  laneStatus.rxCount =",       laneStatus.rxCount()
            print "  laneStatus.locLinked =",     laneStatus.locLinked()
            print "  laneStatus.remLinked =",     laneStatus.remLinked()
            print "  laneStatus.zeros =",         laneStatus.zeros()
            print "  laneStatus.powersOkay =",    laneStatus.powersOkay()

        lst_of_samps = d.samples()
        a = np.array([sample.channels() for sample in lst_of_samps])
        # Transpose converts (1023, 4) to (4, 1023)
        a = np.transpose(a)

        if self.do_calib_imp :
            c = pda.get_imp_config_object(env, self.source)
            if c is None : return None
            bias = c.biasData()
            return np.array(a, dtype=np.int32) - bias

        return a

##-----------------------------

    def cspad_gain_mask(self, gain=None) :
        """ Returns the gain mask of 1/0 for low/high gain pixels as a numpy array of shape=(32,185,388), dtype=uint8.
            If gain is set, method returns a map of (float) gain/1 values for low/high gain pixels, respectively.
            None is returned if configuration data is missing.
        """
        # configuration from data
        c = pda.get_cspad_config_object(self.env, self.source)
        if c is None :
            msg = '%s.cspad_gain_mask - config object is not available' % self.__class__.__name__
            #raise IOError(msg)
            print msg
            return None

        #self.gm = np.empty((32,185,388), dtype=np.uint8)
        self.gm = np.zeros((32,185,388), dtype=np.uint8)
        asic1   = np.ones((185,194), dtype=np.uint8)

        for iquad in range(c.quads_shape()[0]):
            # need in copy to right shift bits
            gm = np.array(c.quads(iquad).gm().gainMap())
            
            for i2x1 in range(8):
                gmasic0 = gm & 1 # take the lowest bit only
                gm = np.right_shift(gm, asic1)
                gm2x1 = np.hstack((gmasic0, gm & 1))
                self.gm[i2x1+iquad*8][:][:] = np.logical_not(gm2x1)
                if i2x1 < 7 : gm = np.right_shift(gm, asic1) # do not shift for last asic

        self.cfg_gain_mask_is_loaded = True

        if gain is None :
            return self.gm
        else :
            f=float(gain-1.)
            return np.array(self.gm,dtype=np.float) * f + 1

##-----------------------------

    def cspad2x2_gain_mask(self, gain=None) :
        """ Returns the gain mask of 1/0 for low/high gain pixels as a numpy array of shape=(2,185,388), dtype=uint8.
            If gain is set, method returns a map of (float) gain/1 values for low/high gain pixels, respectively.
            None is returned if configuration data is missing.
        """
        # configuration from data
        c = pda.get_cspad2x2_config_object(self.env, self.source)
        if c is None :
            msg = '%s.cspad_gain_mask - config object is not available' % self.__class__.__name__
            #raise IOError(msg)
            if self.pbits : print msg
            return None

        #self.gm = np.empty((2,185,388), dtype=np.uint8)
        self.gm = np.zeros((2,185,388), dtype=np.uint8)
        asic1   = np.ones((185,194), dtype=np.uint8)

        gm = np.array(c.quad().gm().gainMap())

        # see the DAQ pdsapp/config/Cspad2x2GainMap.cc:export_() to see that
        # the 4 bits in each element of the gainmap array correspond to the
        # 4 ASICs in the 2x2.  playing around with the DAQ configdb_gui
        # (export/import the text file) shows that the ASICS are numbered
        # like this:
        #   1 3
        #   0 2
        # I am assuming the above corresponds to the 2x2 "natural shape"
        # of [2,185,388] in a natural way.
        for i2x1 in range(2):
            gmasic0 = gm & 1 # take the lowest bit only
            gm = np.right_shift(gm, asic1)
            gm2x1 = np.hstack((gmasic0, gm & 1))
            self.gm[i2x1][:][:] = np.logical_not(gm2x1)
            if i2x1 < 1 : gm = np.right_shift(gm, asic1) # do not shift for last asic

        self.cfg_gain_mask_is_loaded = True

        if gain is None :
            return self.gm
        else :
            f=float(gain-1.)
            return np.array(self.gm,dtype=np.float) * f + 1

##-----------------------------

    def raw_data_cspad_v0(self, evt, env) :

        # data object
        d = pda.get_cspad_data_object(evt, self.source)        
        if d is None :
            if self.pbits & 1 : print 'cspad data object is not found'
            return None
    
        # configuration from data
        c = pda.get_cspad_config_object(env, self.source)
        if c is None :
            if self.pbits & 1 : print 'cspad config object is not found'
            return None
    
        nquads   = d.quads_shape()[0]
        nquads_c = c.numQuads()

        #print 'd.TypeId: ', d.TypeId
        if self.pbits & 8 : print 'nquads in data: %d and config: %d' % (nquads, nquads_c)

        arr = []
        for iq in range(nquads) :
            q = d.quads(iq)
            qnum = q.quad()
            qdata = q.data()
            #n2x1stored = qdata.shape[0]
            roim = c.roiMask(qnum)
            if self.pbits & 8 : print 'qnum: %d  qdata.shape: %s, mask: %d' % (qnum, str(qdata.shape), roim)
            #     '  n2x1stored: %d' % (n2x1stored)
    
            #roim = 0375 # for test only
        
            if roim == 0377 : arr.append(qdata)
            else :
                if self.pbits : print 'PyDetectorAccessr: quad configuration has non-complete mask = %d of included 2x1' % roim
                qdata_full = np.zeros((8,185,388), dtype=qdata.dtype)
                i = 0
                for s in range(8) :
                    if roim & (1<<s) :
                        qdata_full[s,:] = qdata[i,:]
                        i += 1
                arr.append(qdata_full)
    
        nda = np.array(arr)
        if self.pbits & 8 : print 'nda.shape: ', nda.shape
        nda.shape = (32,185,388)
        return nda

##-----------------------------
##-----------------------------

    def shape_config_cspad(self, env) :
        # configuration from data file
        # config object for cspad contains a number of used 2x1-s numSect()
        c = pda.get_cspad_config_object(env, self.source)
        if c is None : return None
        #c.numQuads()
        #return (c.numSect(), 185, 388)
        return (32, 185, 388)

##-----------------------------

    def shape_config_cspad2x2(self, env) :
        c = pda.get_cspad2x2_config_object(env, self.source)
        #c.numAsicsStored(), o.payloadSize()
        return (185, 388, 2) # no other choice

##-----------------------------

    def shape_config_epix100(self, env) :
        c = pda.get_epix_config_object(env, self.source)
        if c is None : return None
        return (c.numberOfRows(), c.numberOfColumns()) 
        #return (704, 768) # no other choice

##-----------------------------

    def shape_config_pnccd(self, env) :
        c = pda.get_pnccd_config_object(env, self.source)
        if c is None : return None
        return (c.numSubmodules(), c.numSubmoduleRows(), c.numSubmoduleChannels())
        #c.numRows(), c.numChannels(), c.numLinks()
        #return (4, 512, 512) # no other choice

##-----------------------------

    def shape_config_princeton(self, env) :
        c = pda.get_princeton_config_object(env, self.source)
        if c is None : return None
        return (c.numPixelsY(), c.numPixelsX())
        #return (c.height()/c.binY(), c.width()/c.binX())
        #return (1300, 1340)

##-----------------------------

    def shape_config_rayonix(self, env) :
        # configuration from data file
        # config object for rayonix has a number of pixel in the bin for both dimansions
        # maximal detector size is 3840x3840, pixel size is 44.5um 
        c = pda.get_rayonix_config_object(env, self.source)
        if c is None : return None
        npix_in_colbin = c.binning_f()
        npix_in_rowbin = c.binning_s()
        if npix_in_rowbin>0 and npix_in_colbin>0 : return (3840/npix_in_rowbin, 3840/npix_in_colbin)
        return None

##-----------------------------

    def shape_config_andor(self, env) :
        # configuration from data file
        c = pda.get_andor_config_object(env, self.source)
        if c is None : return None
        nsegs = None
        try    : nsegs = c.numSensors()
        except : pass
        #npixx = c.numPixelsY() # for Andor3D only
        #npixy = c.numPixelsX() # for Andor3D only
        npixx = c.width() / c.binX()
        npixy = c.height() / c.binY()

        if npixx and npixy :
            return (npixy, npixx) if nsegs is None else (nsegs, npixy, npixx)
        return None

##-----------------------------

    def shape_config_timepix(self, env) :
        # configuration from data file
        #c = pda.get_timepix_config_object(env, self.source)
        # config object does not have shape parameters,
        # (o.height(), o.width()) are available in data object  
        return (512, 512)


    def shape_config_fli(self, env) :
        # configuration from data file
        c = pda.get_fli_config_object(env, self.source)
        if c is None : return None
        return (c.numPixelsY(), c.numPixelsX())
        #return (c.height()/c.binY(), c.width()/c.binX()) # (4096, 4096)


    def shape_config_pimax(self, env) :
        # configuration from data file
        c = pda.get_pimax_config_object(env, self.source)
        if c is None : return None
        return (c.numPixelsY(), c.numPixelsX())
        #return (c.height()/c.binY(), c.width()/c.binX())  # (1024, 1024)


    #def shape_config_imp(self, env) :
    #    #Waveform detector
    #    # configuration from data file
    #    #c = pda.get_imp_config_object(env, self.source)
    #    # config object does not have shape parameters,
    #    return (4, 1023) # ???

##-----------------------------

    def shape_config_camera(self, env) :
        # configuration from data file
        c = None
        if self.dettype in (gu.OPAL1000, gu.OPAL2000, gu.OPAL4000, gu.OPAL8000) :
            c = pda.get_opal1k_config_object(env, self.source)

        elif self.dettype == gu.FCCD :
            c = pda.get_fccd_config_object(env, self.source)     
            #return (c.height(), c.width())

        elif self.dettype == gu.FCCD960 :
            c = pda.get_fccd_config_object(env, self.source)
            #return (c.height(), c.width())

        elif self.dettype == gu.ORCAFL40 :
            c = pda.get_orca_config_object(env, self.source)
            #return (c.height(), c.width())

        elif self.dettype == gu.TM6740 :
            c = pda.get_tm6740_config_object(env, self.source)

        elif self.dettype == gu.QUARTZ4A150 :
            c = pda.get_quartz_config_object(env, self.source) 

        #print c
        if c is None : return None
        return (c.Row_Pixels, c.Column_Pixels)


##-----------------------------

    def shape_data_camera(self, evt) :
        # camera shape from data object
        o = pda.get_camera_data_object(evt, self.source)
        if o is None : return None
        return (o.width(),o.height())

##-----------------------------

    def shape_config(self, env) :

        #print 'TypeId.Type.Id_CspadElement: ', TypeId.Type.Id_CspadElement
        #print 'TypeId.Type.Id_CspadConfig: ',  TypeId.Type.Id_CspadConfig

        if   self.dettype == gu.CSPAD      : return self.shape_config_cspad(env)
        elif self.dettype == gu.CSPAD2X2   : return self.shape_config_cspad2x2(env)
        elif self.dettype == gu.EPIX100A   : return self.shape_config_epix100(env)
        elif self.dettype == gu.PRINCETON  : return self.shape_config_princeton(env)
        elif self.dettype == gu.PNCCD      : return self.shape_config_pnccd(env)
        elif self.dettype == gu.ANDOR      : return self.shape_config_andor(env)
        elif self.dettype == gu.ANDOR3D    : return self.shape_config_andor(env)
        elif self.dettype == gu.RAYONIX    : return self.shape_config_rayonix(env)
        elif self.dettype in (gu.OPAL1000, gu.OPAL2000, gu.OPAL4000, gu.OPAL8000,
                              gu.FCCD, gu.FCCD960, gu.ORCAFL40, gu.TM6740, gu.QUARTZ4A150) \
                                           : return self.shape_config_camera(env)       
        elif self.dettype == gu.TIMEPIX    : return self.shape_config_timepix(env)
        elif self.dettype == gu.FLI        : return self.shape_config_fli(env)
        elif self.dettype == gu.PIMAX      : return self.shape_config_pimax(env)

        # waveform detectors:
        #elif self.dettype == gu.ACQIRIS    : return self.shape_config_acqiris(env)
        #elif self.dettype == gu.IMP        : return self.shape_config_imp(env)
        else                               : return None

##-----------------------------

    def shape(self, par=0) :
        """Returns the detector shape.

        Shape is retrieved from configuration object and
        if it is None, then from calibration file. 
        """
        shc = self.shape_config(self.env)
        return shc if shc is not None else self.shape_calib(par, ctype=gu.PEDESTALS)

##-----------------------------
# Static methods
##-----------------------------

    def save_txtnda(self, fname='nda.txt', ndarr=None, cmts=(), fmt='%.1f', verbos=False, addmetad=True) :
        save_txt(fname, ndarr, cmts, fmt, verbos, addmetad)

##-----------------------------

    def load_txtnda(self, fname) :
        nda = load_txt(fname)
        if len(nda.shape)>2 : return nda
        shape = self.shape()
        if shape is not None : nda.shape = shape
        return nda

##-----------------------------

from time import time

if __name__ == "__main__" :

    ds, src = _psana.DataSource('exp=cxif5315:run=169'), _psana.Source('DetInfo(CxiDs2.0:Cspad.0)')
    #ds, src = _psana.DataSource('exp=xcsi0112:run=15'),  _psana.Source('DetInfo(XcsBeamline.0:Princeton.0)')

    env  = ds.env()
    cls  = env.calibStore()
    evts = ds.events()
    evt  = evts.next()

    for key in evt.keys() : print key

    det = PyDetectorAccess(src, env, pbits=255)

    nda = det.pedestals(evt)
    print '\npedestals nda:', nda
    if nda is not None : print 'nda.dtype: %s nda.shape: %s' % (nda.dtype, nda.shape)

    t0_sec = time()
    nda = det.raw_data(evt, env)
    print '\nPython consumed time to get raw data (sec) =', time()-t0_sec

    print '\nraw_data nda:\n', nda

    sys.exit ('Self test is done')

##-----------------------------
