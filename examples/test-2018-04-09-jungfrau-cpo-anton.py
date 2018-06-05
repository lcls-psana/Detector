from psana import *
ds = DataSource('exp=mfxlr1716:run=134:smd')
det = Detector('Jungfrau1M')
for nevt,evt in enumerate(ds.events()):
   if nevt<500 :
       print nevt, 'skip'
       continue
   calib = det.calib(evt)
   if calib is None:
       print nevt, 'none'
   else:
       print nevt, calib.shape
