import psana
from pyimgalgos.GlobalUtils import print_ndarr

#ds = psana.DataSource('exp=mfxlt3017:run=3')  #Chuck's
#ds = psana.DataSource('exp=mfxls4916:run=22') #Asmit
ds = psana.DataSource('exp=mfxx33117:run=1')   #Dan
det = psana.Detector('Rayonix')
#det = psana.Detector('MfxEndstation.0:Rayonix.0')

env = ds.env()
#evt = ds.events().next()
# Chucks c.deviceID: MX340-HS:125 See PyDetectorAccess.py shape=(7680,7680)
# /reg/d/psdm/mfx/mfxlt3017/calib/Camera::CalibV1/MfxEndstation.0:Rayonix.0/geometry/43-end.data 

# /reg/d/psdm/mfx/mfxls4916/calib/Camera::CalibV1/MfxEndstation.0:Rayonix.0/

EVENTS = 100
evt = None
raw = None
for nev,evt in enumerate(ds.events()):    
    if nev > EVENTS : break
    print '%s\nEvent %4d' % (50*'_', nev)
    if evt is None : continue
    raw = det.raw(evt)
    if raw is not None : break

print_ndarr(det.raw(evt), name='raw', first=0, last=5)

print 'raw.shape          :', raw.shape
print 'det.shape_config   :', det.shape_config(env)
print 'det.pixel_size(evt):', det.pixel_size(evt)

#from Detector.PyDataAccess import get_rayonix_config_object
#c = get_rayonix_config_object(env, det.source)

c = env.configStore().get(psana.Rayonix.ConfigV2, det.source)
print 'c.deviceID:', c.deviceID(), "See PyDetectorAccess.py shape=(7680,7680) if 'MX340' in c.deviceID() else (3840,3840)"  


print 'NEW STUFF IN Rayonix.ConfigV2:'
print 'width()      :', c.width()
print 'height()     :', c.height()
print 'maxWidth()   :', c.maxWidth()
print 'maxHeight()  :', c.maxHeight()
print 'binning_f()  :', c.binning_f()
print 'binning_s()  :', c.binning_s()
print 'deviceID()   :', c.deviceID()
print 'pixelWidth() :', c.pixelWidth()
print 'pixelHeight():', c.pixelHeight()

