
## Run this example:
## python Detector/examples/ex_AreaDetectorCompond.py

from Detector.AreaDetectorCompound import AreaDetectorCompound
import psana
from Detector.GlobalUtils import print_ndarr
 
ds = psana.DataSource('exp=xpptut15:run=460')
det = AreaDetectorCompound(['MecTargetChamber.0:Cspad2x2.1',\
                            'MecTargetChamber.0:Cspad2x2.2',\
                            'MecTargetChamber.0:Cspad2x2.3'])
 
env = ds.env()
evt = ds.events().next()
rnum = evt.run()
 
if True :
    print 'rnum     :', rnum
    print 'calibdir :', str(env.calibDir())
    print 'size     :', str(det.list_size(evt))
    print 'shapes   :', str(det.list_shape(evt))
    print 'ndims    :', str(det.list_ndim(evt))
 
    raws = det.list_raw(evt)
    for nda in raws : print_ndarr(nda, name='-- per det list_raw', first=0, last=5)
 
    raw = det.raw(evt)
    print_ndarr(raw, name='raw as nda', first=0, last=5)
 
    calib = det.calib(evt)
    print_ndarr(calib, name='calib', first=0, last=5)
 
    xy0_offset = (550,550)
    img_raw   = det.image(evt, nda_in=raw, xy0_off_pix=xy0_offset)
    #img_calib = det.image(evt, nda_in=calib, xy0_off_pix=xy0_offset)
    #img_at_z  = det.image_at_z(evt, zplane=500000, nda_in=raw, xy0_off_pix=xy0_offset)
 
    if True : # True or False for to plot image or not
        from pyimgalgos.GlobalGraphics import plotImageLarge, show
        img = img_raw
        plotImageLarge(img, title='img as %s' % str(img.shape), amp_range=(0,5000))
        show()
