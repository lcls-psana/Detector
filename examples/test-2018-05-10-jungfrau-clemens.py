from psana import *
#ds = DataSource('exp=mfxlr1716:run=134:smd')
#det = Detector('Jungfrau1M')
ds = DataSource('exp=mfxls4916:run=223:smd')
det = Detector('Jungfrau512k')

for nevt,evt in enumerate(ds.events()):
   if nevt>1000 : break

   calib = det.calib(evt)
   image = det.image(evt)

   if calib is None: print nevt, 'calib is None'
   else:             print nevt, 'calib.shape:', calib.shape

   if image is None: print nevt, 'image is None'
   else:             print nevt, 'image.shape:', image.shape
