from __future__ import print_function

## Run this example:
## python Detector/examples/ex_AreaDetectorCompond.py

#import psana

#----------

def datasource_and_detector(ntest) :

    from psana import DataSource

    if ntest==1 :
        from Detector.AreaDetectorCompound import AreaDetectorCompound
        ds = DataSource('exp=xpptut15:run=460')
        return ds, AreaDetectorCompound(['MecTargetChamber.0:Cspad2x2.1',\
                                         'MecTargetChamber.0:Cspad2x2.2',\
                                         'MecTargetChamber.0:Cspad2x2.3'], ds.env())
    elif ntest==2 :
        from Detector.AreaDetectorCompound import AreaDetectorCompound
        ds = DataSource('exp=xpptut15:run=460')
        return ds, AreaDetectorCompound('compound MecTargetChamber.0:Cspad2x2.1'\
                                                ' MecTargetChamber.0:Cspad2x2.2'\
                                                ' MecTargetChamber.0:Cspad2x2.3', ds.env())
    elif ntest==3 :
        from psana import Detector, DataSource
        ds = DataSource('exp=xpptut15:run=460')
        return ds, Detector('compound MecTargetChamber.0:Cspad2x2.1'\
                                    ' MecTargetChamber.0:Cspad2x2.2'\
                                    ' MecTargetChamber.0:Cspad2x2.3') # , ds.env())
    elif ntest==4 :
        from psana import Detector, DataSource
        ds = DataSource('exp=mfxls4916:run=298')
        return ds, Detector('compound MfxEndstation.0:Jungfrau.0'\
                                    ' MfxEndstation.0:Jungfrau.1')
    else :
        from psana import Detector, DataSource
        ds = DataSource('exp=mfxls4916:run=298')
        return ds, Detector(['MfxEndstation.0:Jungfrau.0',\
                             'MfxEndstation.0:Jungfrau.1'])

#----------

def test_AreaDetectorCompound(ntest) :

    from Detector.GlobalUtils import print_ndarr
 
    ds, det = datasource_and_detector(ntest)

    env = ds.env()
    evt = next(ds.events())
    rnum = evt.run()
 
    print('rnum     :', rnum)
    print('calibdir :', str(env.calibDir()))
    print('size     :', str(det.list_size(evt)))
    print('shapes   :', str(det.list_shape(evt)))
    print('ndims    :', str(det.list_ndim(evt)))
 
    raws = det.list_raw(evt)
    for nda in raws : print_ndarr(nda, name='-- per det list_raw', first=0, last=5)
 
    raw = det.raw(evt)
    print_ndarr(raw, name='raw as nda', first=0, last=5)
 
    calib = det.calib(evt)
    print_ndarr(calib, name='calib', first=0, last=5)

    print_ndarr(det.common_mode(evt), name='common_mode ')
 
    xy0_offset = (550,550) if ntest<4 else (1400,1400)
    img_raw   = det.image(evt, nda_in=raw, xy0_off_pix=xy0_offset)
    #img_calib = det.image(evt, nda_in=calib, xy0_off_pix=xy0_offset)
    #img_at_z  = det.image_at_z(evt, zplane=500000, nda_in=raw, xy0_off_pix=xy0_offset)
 
    if True : # True or False for to plot image or not
        from pyimgalgos.GlobalGraphics import plotImageLarge, show
        img = img_raw
        ave, rms = img.mean(), img.std()
        plotImageLarge(img, title='img as %s' % str(img.shape), amp_range=(ave-rms, ave+2*rms)) #(1000,3000)
        show()

#----------

if __name__ == "__main__" :

    import sys
    ntest = int(sys.argv[1]) if len(sys.argv)>1 else 1
    print('Test # %d' % ntest)

    test_AreaDetectorCompound(ntest)

    sys.exit('END OF TEST %d' % ntest)

#----------
