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
import psana
import Detector.GlobalUtils  as gu
import Detector.PyDataAccess as pda

from pypdsdata.xtc import TypeId  # types from pdsdata/xtc/TypeId.hh, ex: TypeId.Type.Id_CspadElement

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
        self.dettype = gu.det_type_from_source(source)
        self.do_offset = False # works for camera
        self.correct_time = True # works for acqiris
        if self.pbits & 1 : self.print_attributes()

##-----------------------------

    def print_attributes(self) :
        print 'PyDetectorAccess attributes:\n  source: %s\n  dtype : %d\n  pbits : %d' % \
              (self.source, self.dettype, self.pbits), \
              '\n  do_offset (Camera): %s\n  correct_time (Acqiris): %s' % \
              (self.do_offset, self.correct_time)

##-----------------------------

    def set_env(self, env) :
        self.env = env

##-----------------------------

    def set_source(self, source) :
        self.source = source

##-----------------------------

    def pedestals(self, evt) :
        return None
    
##-----------------------------

    def pixel_rms(self, evt) :
        return None

##-----------------------------

    def pixel_gain(self, evt) :
        return None

##-----------------------------

    def pixel_mask(self, evt) :
        return None

##-----------------------------

    def pixel_bkgd(self, evt) :
        return None

##-----------------------------

    def pixel_status(self, evt) :
        return None

##-----------------------------

    def common_mode(self, evt) :
        return None

##-----------------------------

    def inst(self) :
        return None

##-----------------------------

    def print_config(self, evt) :
        pass

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

    def raw_data(self, evt, env) :

        #print 'TypeId.Type.Id_CspadElement: ', TypeId.Type.Id_CspadElement
        #print 'TypeId.Type.Id_CspadConfig: ',  TypeId.Type.Id_CspadConfig

        if   self.dettype == gu.CSPAD     : return self.raw_data_cspad(evt, env)     # 3   ms
        elif self.dettype == gu.CSPAD2X2  : return self.raw_data_cspad2x2(evt, env)  # 0.6 ms
        elif self.dettype == gu.PRINCETON : return self.raw_data_princeton(evt, env) # 0.7 ms
        elif self.dettype == gu.PNCCD     : return self.raw_data_pnccd(evt, env)     # 0.8 ms
        elif self.dettype == gu.ANDOR     : return self.raw_data_andor(evt, env)     # 0.1 ms
        elif self.dettype == gu.FCCD960   : return self.raw_data_fccd960(evt, env)   # 11  ms
        elif self.dettype == gu.EPIX100A  : return self.raw_data_epix(evt, env)      # 0.3 ms
        elif self.dettype == gu.EPIX10K   : return self.raw_data_epix(evt, env)
        elif self.dettype == gu.EPIX      : return self.raw_data_epix(evt, env)
        elif self.dettype == gu.ACQIRIS   : return self.raw_data_acqiris(evt, env)
        elif self.dettype == gu.OPAL1000  : return self.raw_data_camera(evt, env)    # 1 ms
        elif self.dettype == gu.OPAL2000  : return self.raw_data_camera(evt, env)
        elif self.dettype == gu.OPAL4000  : return self.raw_data_camera(evt, env)
        elif self.dettype == gu.OPAL8000  : return self.raw_data_camera(evt, env)
        elif self.dettype == gu.ORCAFL40  : return self.raw_data_camera(evt, env)
        elif self.dettype == gu.TM6740    : return self.raw_data_camera(evt, env)    # 0.24 ms
        else                              : return None

##-----------------------------

    def raw_data_cspad(self, evt, env) :

        # data object
        d = pda.get_cspad_data_object(evt, self.source)
        if d is None : return None
    
        # configuration from data
        c = pda.get_cspad_config_object(env, self.source)
        if c is None : return None
    
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
        if d16 is not None :
            if self.do_offset : return np.array(d16, dtype=np.int32) - d.offset()        
            else              : return d16
        
        d8 = d.data8()
        if d8 is not None : 
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
        d = evt.get(psana.Andor.FrameV1, self.source)
        if d is None : return None

        #c = env.configStore().get(psana.Andor.ConfigV1, self.source)
        #if c is None : return None
        #print 'config: width: %d, height: %d' % (c.width(), c.height())

        nda = d.data()
        return nda if nda is not None else None

##-----------------------------

    def raw_data_pnccd(self, evt, env) :
        #print '=== in raw_data_pnccd'
        #d = evt.get(psana.PNCCD.FullFrameV1, self.source)
        d = evt.get(psana.PNCCD.FramesV1, self.source)
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
        c = pda.get_epix_config_object(env, self.source)
        if c is None : return None
        #print 'config: rows: %d, cols: %d, asics: %d' % (c.numberOfRows(), c.numberOfColumns(), c.numberOfAsics())
        #print 'config: digitalCardId0: %d, 1: %d' % (c.digitalCardId0(), c.digitalCardId1())
        #print 'config: analogCardId0 : %d, 1: %d' % (c.analogCardId0(),  c.analogCardId1())
        #print 'config: version: %d, asicMask: %d' % (c.version(), c.asicMask())

        nda = d.frame()
        return nda if nda is not None else None

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

from time import time

if __name__ == "__main__" :

    ds, src = psana.DataSource('exp=cxif5315:run=169'), psana.Source('DetInfo(CxiDs2.0:Cspad.0)')
    #ds, src = psana.DataSource('exp=xcsi0112:run=15'),  psana.Source('DetInfo(XcsBeamline.0:Princeton.0)')

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
