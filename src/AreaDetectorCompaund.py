#----------
"""
Class :py:class:`AreaDetectorCompaund` supports list of AreaDetector objects
============================================================================

Usage::

    # import
    import psana

    # retreive parameters from psana etc.
    dsname = 'exp=xpptut15:run=460'
    src = 'XppGon.0:Cspad.0' # or its alias 'cspad'

    ds  = psana.DataSource(dsname)
    env = ds.env()
    evt = ds.events().next()
    runnum = evt.run()


Pages about how to generate class methods dynamically
  - https://stackoverflow.com/questions/8307602/programmatically-generate-methods-for-a-class
  - https://stackoverflow.com/questions/533382/dynamic-runtime-method-creation-code-generation-in-python


See classes
  - :class:`AreaDetector`
  - :class:`DetectorTypes`
  - :class:`GlobalUtils`
  - :class:`PyDataAccess`
  - :class:`PyDetectorAccess`  - Python access interface to data
  - :class:`PyDetector`        - factory for different detectors


This software was developed for the LCLS project.
If you use all or part of it, please give an appropriate acknowledgment.

Created on 2019-04-02 Mikhail Dubrovin
"""
#----------

import sys
import psana
import numpy as np

from PSCalib.GeometryAccess import img_from_pixel_arrays
from Detector.GlobalUtils import info_ndarr, print_ndarr

#----------

class AreaDetectorCompaund(object):
    """Python access to the list of area detectors.
    """
    # List for methods list_raw, list_calib, list_shape, etc.
    WRAP_METHODS_LIST = ['raw', 'calib', 'shape', 'size', 'ndim', 'common_mode', 'geometry']

    # List for methods raw, calib, pedestals, etc.
    WRAP_METHODS_NDA  = ['raw', 'calib', 'pedestals', 'rms', 'gain', 'offset', 'bkgd', 'status', 'mask', 'photons',\
                         'coords_x', 'coords_y', 'coords_z',\
                         'indexes_x', 'indexes_y', 'indexes_z',\
                         'common_mode_correction', 'common_mode_apply',\
                         'mask_geo', 'mask_comb', 'mask_edges', 'mask_neighbors', 'mask_calib',\
                         'datast', 'status_as_mask', 'gain_mask', 'gain_mask_non_zero', 'areas'\
                        ]

    WRAP_METHODS_2NDA  = ['coords_xy', 'indexes_xy', 'indexes_xy_at_z']

    #----------

    def __init__(self, detnames) :
        """Constructor of the class :class:`AreaDetectorCompaund`.
           Parameters
           - detnames : (list of str) - list of detector names, e.g. ['CxiDs2.0:Cspad.0','CxiDs2.0:Cspad.1']
        """
        self.detnames = detnames
        self.list_dets = [psana.Detector(name) for name in detnames]
        for det in self.list_dets : det.do_reshape_2d_to_3d(flag=True)
        #for det in self.list_dets : det.set_print_bits(511)

        self.add_methods()

    #----------

    def add_method_list(self, metname):
        """ Adds to self-class method with specified name like (for metname='raw'):
            def raw(self, *args, **kwargs) :
                return [o.raw(*args, **kwargs) for o in self.list_dets]
        """
        def _prototype(*args, **kwargs) :
            return [getattr(o, metname)(*args, **kwargs) for o in self.list_dets]
        setattr(self, 'list_%s'%metname , _prototype)

    #----------

#    def list_calib(self, *args, **kwargs) :
#        """explicit implementation for debugging
#        """
#        olst = []
#        for det in self.list_dets :
#            print '\nmake calib for %s' % det.name
#            print_ndarr(det.pedestals(*args, **kwargs),    name='  -- list_calib pedestals', first=0, last=5) 
#            print_ndarr(det.gain(*args, **kwargs),         name='  -- list_calib gain     ', first=0, last=5) 
#            print_ndarr(det.offset(*args, **kwargs),       name='  -- list_calib offset   ', first=0, last=5)
#            print_ndarr(det.raw(*args, **kwargs),          name='  -- list_calib raw      ', first=0, last=5) 
#            nda = det.calib(*args, **kwargs)
#            print_ndarr(nda,                               name='  -- list_calib calib    ', first=0, last=5)
#            olst.append(nda)
#        return olst

    #----------

    def add_method_nda(self, metname):
        def _prototype(*args, **kwargs) :
            list_nda=[getattr(o, metname)(*args, **kwargs) for o in self.list_dets]
            #for i,nda in enumerate(list_nda) : print '  XXX add_method_nda det:%d shape = %s' % (i,str(nda.shape))
            # ATTENTION !!! IMPORTANT for Jungfrau, Epix, etc. multi-gain detectors)
            # concatinate for index preceding the 2d shape
            # Ex. for Jungfrau combined of 2 detectors:
            # --- raw          (2, 512, 1024) (+)    (1, 512, 1024) (=)    (3, 512, 1024)
            # --- pedestals (3, 2, 512, 1024) (+) (3, 1, 512, 1024) (=) (3, 3, 512, 1024)
            concaxis = list_nda[0].ndim - 3
            return np.concatenate(list_nda, axis=concaxis) # concatinates for axis=0, other dimensions should be the same...
        setattr(self, metname, _prototype)

    #----------

    def add_method_double_nda(self, metname):
        def _prototype(*args, **kwargs) :
            list_double_nda=[getattr(o, metname)(*args, **kwargs) for o in self.list_dets]
            list_nda0 = [v[0] for v in list_double_nda]
            list_nda1 = [v[1] for v in list_double_nda]
            concaxis = list_nda0[0].ndim - 3
            return np.concatenate(list_nda0, axis=concaxis),  np.concatenate(list_nda1, axis=concaxis)
        setattr(self, metname, _prototype)

    #----------

    def add_methods(self):
        """Generates methods from prototypes with names from WRAP_METHODS_LIST/NDA.
        """
        for name in self.WRAP_METHODS_LIST: self.add_method_list(name)
        for name in self.WRAP_METHODS_NDA:  self.add_method_nda(name)
        for name in self.WRAP_METHODS_2NDA: self.add_method_double_nda(name)

    #----------

    #def image(self, *args, **kwargs) :
    def image(self, evt, nda_in=None, pix_scale_size_um=None, xy0_off_pix=None, do_update=False) :
        """ returns 2d image for compound detector (consisting of two or more regular Detectors).
            NOTICE:
               - xy0_off_pix=(VERT,HORIZ) on regular image
               - do_update=True is required if indexes_x/y were called earlier with different xy0_off_pix
        """ 
        #ix = self.indexes_x(evt, pix_scale_size_um, xy0_off_pix, do_update)
        #iy = self.indexes_y(evt, pix_scale_size_um, xy0_off_pix, do_update)
        ix, iy = self.indexes_xy(evt, pix_scale_size_um, xy0_off_pix, do_update)

        if False :
            el_begin, el_end = 1000, 1005
            print_ndarr(nda_in, name='image nda_in', first=el_begin, last=el_end)
            print_ndarr(ix,     name='image ix    ', first=el_begin, last=el_end)
            print_ndarr(iy,     name='image iy    ', first=el_begin, last=el_end)

        return img_from_pixel_arrays(ix, iy, nda_in)

    #----------

    def image_at_z(self, evt, zplane=None, nda_in=None, pix_scale_size_um=None, xy0_off_pix=None, do_update=False) :
        """ returns 2d image for compound detector projected on plane at z (um).
            NOTICE:
               - xy0_off_pix=(VERT,HORIZ) on regular image
               - do_update=True is required if indexes_x/y were called earlier with different xy0_off_pix
        """ 
        ix, iy = self.indexes_xy_at_z(evt, zplane, pix_scale_size_um, xy0_off_pix, do_update)

        if False :
            el_begin, el_end = 1000, 1005
            print_ndarr(nda_in, name='image nda_in', first=el_begin, last=el_end)
            print_ndarr(ix,     name='image ix    ', first=el_begin, last=el_end)
            print_ndarr(iy,     name='image iy    ', first=el_begin, last=el_end)

        return img_from_pixel_arrays(ix, iy, nda_in)

#----------

if __name__ == "__main__" :
    """
       Self-test
       Usage: python <path>/AreaDetectorCompaund.py <test-number>
    """
    def dsname_and_detectors(ntest) :
       """event_keys -d exp=xppx37817:run=60 -m3 # Epix100a.1
          event_keys -d exp=xpptut15:run=460 -m3 # Cspad2x2.1,2,3 and Princeton.1,2,3

          event_keys -d exp=mfxls4916:run=298 -m3
          EventKey(type=psana.Jungfrau.ElementV2, src='DetInfo(MfxEndstation.0:Jungfrau.0)', alias='Jungfrau1M')
          EventKey(type=psana.Jungfrau.ElementV2, src='DetInfo(MfxEndstation.0:Jungfrau.1)', alias='Jungfrau512k')
       """
       if ntest==1 : 
         #psana.setOption('psana.calib-dir', './calib')
         return\
         'exp=xpptut15:run=460',\
         ['MecTargetChamber.0:Cspad2x2.1',\
          'MecTargetChamber.0:Cspad2x2.2',\
          'MecTargetChamber.0:Cspad2x2.3']

       if ntest==2 : return\
         'exp=mfxls4916:run=298',\
         ['MfxEndstation.0:Jungfrau.0',\
          'MfxEndstation.0:Jungfrau.1']

       if ntest==3 : return\
         'exp=xpptut15:run=460',\
         ['MecTargetChamber.0:Princeton.1',\
          'MecTargetChamber.0:Princeton.2',\
          'MecTargetChamber.0:Princeton.3']

       if ntest==4 : 
         return\
         'exp=xppx37817:run=60',\
         ['XppGon.0:Epix100a.1',\
          'XppGon.0:Epix100a.2']

    #----------

    from time import time

    ntest = int(sys.argv[1]) if len(sys.argv)>1 else 1
    print 'Test # %d' % ntest

    dsname, detnames = dsname_and_detectors(ntest)
    print 'Example for\n  dataset: %s\n  detnames : %s' % (dsname, detnames)

    #psana.Source('DetInfo(CxiDs2.0:Cspad.0)')
    ds = psana.DataSource(dsname)

    env = ds.env()
    cls = env.calibStore()
    eviter = ds.events()
    evt = eviter.next()
    rnum = evt.run()

    #for key in evt.keys() : print key

    t0_sec = time()
    det = AreaDetectorCompaund(detnames)
    print '\nConstructor time = %.6f sec' % (time()-t0_sec)
    print 'det methods - dir(det):\n ', ' '.join([s for s in dir(det) if s[0]!='_'])

    print 'rnum     :', rnum
    print 'calibdir :', str(env.calibDir())
    print 'size     :', str(det.list_size(evt))
    print 'shapes   :', str(det.list_shape(evt))
    print 'ndims    :', str(det.list_ndim(evt))

    t0_sec = time()
    raws = det.list_raw(evt)
    print '\nConsumed time to get raw data %.6f sec' % (time()-t0_sec)
    for nda in raws : print_ndarr(nda, name='    -- per det list_raw', first=0, last=5)

    raw = det.raw(evt)
    print_ndarr(raw, name='raw as nda', first=0, last=5)

    print 'detectors in AreaDetectorCompaund:'
    for o in det.list_dets : print '%24s shape=%s %s' % (o.name, str(o.shape()), str(o))

    calibs = det.list_calib(evt) 
    for nda in calibs :
        print_ndarr(nda, name='    -- per det list_calib', first=0, last=5)

    calib = det.calib(evt)
    print_ndarr(calib,               name='calib    ', first=0, last=5)

    print_ndarr(det.pedestals(rnum), name='pedestals', first=0, last=5)
    print_ndarr(det.gain(rnum),      name='gain     ', first=0, last=5)
    print_ndarr(det.offset(rnum),    name='offset   ', first=0, last=5)

    print_ndarr(det.coords_x(evt),   name='coords_x ', first=0, last=5)
    print_ndarr(det.coords_y(evt),   name='coords_y ', first=0, last=5)

    #print_ndarr(det.indexes_x(evt), name='indexes_x no offset', first=1000, last=1005)
    #print_ndarr(det.indexes_x(evt, xy0_off_pix=(1500,1500)), name='indexes_x, off_pix=(1000,1000)', first=1000, last=1005)

    #img = reshape_to_2d(det.raw(evt))
    
    #_ = det.image(evt, nda_in=calib, pix_scale_size_um=None, xy0_off_pix=None, do_update=False)

    # NOTICE:
    # xy0_off_pix=(VERT,HORIZ)
    # do_update=True is required if indexes_x/y called

    xy0_offset =(550,550) if ntest==1 else (1400,1400)

    img = det.image(evt, nda_in=raw, xy0_off_pix=xy0_offset)
    #img = det.image(evt, nda_in=calib, xy0_off_pix=xy0_offset)
    #img = det.image_at_z(evt, zplane=500000, nda_in=raw, xy0_off_pix=xy0_offset)

    print_ndarr(img, name='img', first=0, last=5)

    if True : # True or False for to plot image or not 
        from pyimgalgos.GlobalUtils import reshape_to_2d
        from pyimgalgos.GlobalGraphics import plotImageLarge, show

        plotImageLarge(img, title='img as %s' % str(img.shape), amp_range=(0,5000)) # for raw(0,5000) for calib (-0.5,1) cspad2x2:(1500,2000)
        show()

    sys.exit('TEST COMPLETED')

#----------
