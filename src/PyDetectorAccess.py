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
import numpy as np
import _psana
import Detector.PyDataAccess as pda

#import Detector.GlobalUtils as gu
import PSCalib.GlobalUtils as gu

from PSCalib.CalibParsStore import cps
from PSCalib.CalibFileFinder import CalibFileFinder
from PSCalib.GeometryAccess import GeometryAccess, img_from_pixel_arrays

#from pypdsdata.xtc import TypeId  # types from pdsdata/xtc/TypeId.hh, ex: TypeId.Type.Id_CspadElement

##-----------------------------

class PyDetectorAccess :
    """Direct python access to detector data.

    @see PyDetector
    @see DetectorAccess
    """
##-----------------------------

    def __init__(self, source, env, pbits=0) :
        """Constructor.
        @param source - data source, ex: _psana.Source('DetInfo(CxiDs2.0:Cspad.0)')
        @param env    - environment
        @param pbits  - print control bit-word
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

##-----------------------------

    def cpstore(self, par) : # par = evt or runnum

        runnum = par if isinstance(par, int) else par.run()
        #print 80*'_'
        #print 'cpstore XXX runnum = %d' % runnum

        # for 1st entry and when runnum is changing:
        if runnum != self.runnum_cps or self.cpst is None :
            self.runnum_cps = runnum
            group = gu.dic_det_type_to_calib_group[self.dettype]
            self.cpst = cps.Create(self.env.calibDir(), group, self.str_src, runnum, self.pbits)
            if self.pbits & 1 : print 'PSCalib.CalibParsStore object is created for run %d' % runnum

        return self.cpst

##-----------------------------

    def geoaccess(self, par) : # par = evt or runnum

        runnum = par if isinstance(par, int) else par.run()
        #print 'cpstore XXX runnum = %d' % runnum

        # for 1st entry and when runnum is changing:
        if  runnum != self.runnum_geo or self.geo is None :
            self.runnum_geo = runnum
            group = gu.dic_det_type_to_calib_group[self.dettype]
            cff = CalibFileFinder(self.env.calibDir(), group, 0377 if self.pbits else 0)
            fname = cff.findCalibFile(self.str_src, 'geometry', runnum)
            if fname :
                self.geo = GeometryAccess(fname, 0377 if self.pbits else 0)
                if self.pbits & 1 : print 'PSCalib.GeometryAccess object is created for run %d' % runnum
            else     :
                self.geo = None
                if self.pbits & 1 : print 'WARNING: PSCalib.GeometryAccess object is NOT created for run %d - geometry file is missing.' % runnum

            # arrays for caching
            self.iX = None 
            self.iY = None 

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

    def ndim(self, par, ctype=gu.PEDESTALS) :
        return self.cpstore(par).ndim(ctype)

##-----------------------------

    def size(self, par, ctype=gu.PEDESTALS) :
        return self.cpstore(par).size(ctype)

##-----------------------------

    def shape(self, par, ctype=gu.PEDESTALS) :
        return self.cpstore(par).shape(ctype)

##-----------------------------

    def status(self, par, ctype=gu.PEDESTALS) :
        return self.cpstore(par).status(ctype)

##-----------------------------
##-----------------------------
##-----------------------------
##-----------------------------

    def coords_x(self, par) :
        if self.geoaccess(par) is None : return None
        else : return self.geo.get_pixel_coords()[0] #oname=None, oindex=0, do_tilt=True)

##-----------------------------

    def coords_y(self, par) :
        if self.geoaccess(par) is None : return None
        else : return self.geo.get_pixel_coords()[1] #oname=None, oindex=0, do_tilt=True)

##-----------------------------

    def coords_z(self, par) :
        if self.geoaccess(par) is None : return None
        else : return self.geo.get_pixel_coords()[2] #oname=None, oindex=0, do_tilt=True)

##-----------------------------

    def areas(self, par) :
        if self.geoaccess(par) is None : return None
        else : return self.geo.get_pixel_areas()

##-----------------------------

    # mbits = +1-edges; +2-wide central cols; +4-non-bound; +8-non-bound neighbours
    def mask_geo(self, par, mbits=15) :
        if self.geoaccess(par) is None : return None
        else : return self.geo.get_pixel_mask(mbits=mbits)

##-----------------------------

    def update_index_arrays(self, par, pix_scale_size_um=None, xy0_off_pix=None, do_update=False) :
        """ Returns True if pixel index arrays are available, othervise False.
        """
        if self.geoaccess(par) is None : return False
        else :
            if do_update or self.iX is None :
                self.iX, self.iY = self.geo.get_pixel_coord_indexes(oname=None, oindex=0,\
                                                       pix_scale_size_um=pix_scale_size_um,\
                                                       xy0_off_pix=xy0_off_pix, do_tilt=True)
            if self.iX is None : return False
        return True

##-----------------------------

    def indexes_x(self, par, pix_scale_size_um=None, xy0_off_pix=None, do_update=False) :
        """Returns pixel index array iX."""
        if not self.update_index_arrays(par, pix_scale_size_um, xy0_off_pix, do_update) : return None
        return self.iX

##-----------------------------

    def indexes_y(self, par, pix_scale_size_um=None, xy0_off_pix=None, do_update=False) :
        """Returns pixel index array iY."""
        if not self.update_index_arrays(par, pix_scale_size_um, xy0_off_pix, do_update) : return None
        return self.iY

##-----------------------------

    def indexes_xy(self, par, pix_scale_size_um=None, xy0_off_pix=None, do_update=False) :
        """Returns two pixel index arrays iX and iY."""
        if not self.update_index_arrays(par, pix_scale_size_um, xy0_off_pix, do_update) : return None
        if self.iX is None : return None, None # single None is not the same as (None, None) !
        return self.iX, self.iY 

##-----------------------------

    def pixel_size(self, par) :
        if self.geoaccess(par) is None : return None
        else : return self.geo.get_pixel_scale_size()

##-----------------------------

    def move_geo(self, par, dx, dy, dz) :
        if self.geoaccess(par) is None : pass
        else : return self.geo.move_geo(None, 0, dx, dy, dz)

##-----------------------------

    def tilt_geo(self, par, dtx, dty, dtz) :
        if self.geoaccess(par) is None : pass
        else : return self.geo.tilt_geo(None, 0, dtx, dty, dtz)

##-----------------------------

    def image(self, par, img_nda, pix_scale_size_um=None, xy0_off_pix=None, do_update=False) :
        if not self.update_index_arrays(par, pix_scale_size_um, xy0_off_pix, do_update) : return None
        return img_from_pixel_arrays(self.iX, self.iY, img_nda)

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

    def gain_map(self, gain=None) :
        """Returns a gain map extracted from detector configuration data.
           Currently implemented for CSPAD only.
           Returns None for other detectors or missing configuration for CSPAD.
        """
        if self.dettype == gu.CSPAD : return self.cspad_gain_map(gain) 
        else                        : return None

##-----------------------------

    def raw_data(self, evt, env) :

        #print 'TypeId.Type.Id_CspadElement: ', TypeId.Type.Id_CspadElement
        #print 'TypeId.Type.Id_CspadConfig: ',  TypeId.Type.Id_CspadConfig

        if   self.dettype == gu.CSPAD      : return self.raw_data_cspad(evt, env)     # 3   ms
        elif self.dettype == gu.CSPAD2X2   : return self.raw_data_cspad2x2(evt, env)  # 0.6 ms
        elif self.dettype == gu.PRINCETON  : return self.raw_data_princeton(evt, env) # 0.7 ms
        elif self.dettype == gu.PNCCD      : return self.raw_data_pnccd(evt, env)     # 0.8 ms
        elif self.dettype == gu.ANDOR      : return self.raw_data_andor(evt, env)     # 0.1 ms
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
            print 'cspad data object is not found'
            return None
    
        # configuration from data
        c = pda.get_cspad_config_object(env, self.source)
        if c is None :
            print 'cspad config object is not found'
            return None
    
        nquads   = d.quads_shape()[0]
        nquads_c = c.numQuads()

        #print 'd.TypeId: ', d.TypeId
        #print 'nquads in data: %d and config: %d' % (nquads, nquads_c)

        arr = []
        for iq in range(nquads) :
            q = d.quads(iq)
            qnum = q.quad()
            qdata = q.data()
            #n2x1stored = qdata.shape[0]
            roim = c.roiMask(qnum)
            #print 'qnum: %d  qdata.shape: %s, mask: %d' % (qnum, str(qdata.shape), roim)
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
        #print 'nda.shape: ', nda.shape
        nda.shape = (32,185,388)
        return nda
    
##-----------------------------

    def raw_data_cspad2x2(self, evt, env) :

        # data object
        d = pda.get_cspad2x2_data_object(evt, self.source)
        if d is None : return None
    
        # configuration object
        c = pda.get_cspad2x2_config_object(env, self.source)
        if c is None : return None

        #print 'd.TypeId: ', d.TypeId
        #print 'common mode 0: %f   1: %f', (d.common_mode(0), d.common_mode(1))
        #print 'roiMask: ', c.roiMask(), '  numAsicsStored: ', c.numAsicsStored()

        if c.roiMask() != 3 :
            if self.pbits : print 'PyDetectorAccess: CSPAD2x2 configuration has non-complete mask = %d of included 2x1' % c.roiMask()
            return None

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

    def raw_data_andor(self, evt, env) :
        d = evt.get(_psana.Andor.FrameV1, self.source)
        if d is None : return None

        #c = env.configStore().get(_psana.Andor.ConfigV1, self.source)
        #if c is None : return None
        #print 'config: width: %d, height: %d' % (c.width(), c.height())

        nda = d.data()
        return nda if nda is not None else None

##-----------------------------

    def raw_data_pnccd(self, evt, env) :
        #print '=== in raw_data_pnccd'
        #d = evt.get(_psana.PNCCD.FullFrameV1, self.source)
        d = evt.get(_psana.PNCCD.FramesV1, self.source)
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

    def cspad_gain_map(self, gain=None) :
        """ Returns the gain map of low/high gain pixels (numpy array of shape=(32,185,388), dtype=float).
            If gain is None, method returns a map of (uint16) 0/1 for low/high gain pixels, respectively.
            None is returned if configuration data is missing.
        """
        # configuration from data
        c = pda.get_cspad_config_object(self.env, self.source)
        if c is None :
            msg = '%s.cspad_gain_map - config object is not available' % self.__class__.__name__
            #raise IOError(msg)
            print msg
            return None

        self.gm = np.empty((32,185,388), dtype=np.uint16)
        asic1   = np.ones((185,194), dtype=np.uint16)

        for iquad in range(c.quads_shape()[0]):
            # need in copy to right shift bits
            gm = np.array(c.quads(iquad).gm().gainMap())
            
            for i2x1 in range(8):
                gmasic0 = gm & 1 # take the lowest bit only
                gm = np.right_shift(gm, asic1)
                gm2x1 = np.hstack((gmasic0, gm & 1))
                self.gm[i2x1+iquad*8][:][:] = gm2x1
                if i2x1 < 7 : gm = np.right_shift(gm, asic1) # do not shift for last asic

        if gain is None :
            return self.gm
        else :
            return np.ones((32,185,388), dtype=np.float) + self.gm * (gain-1)

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
