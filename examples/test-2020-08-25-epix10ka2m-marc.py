import psana
from Detector.GlobalUtils import print_ndarr

ds  = psana.DataSource('exp=mfxp17318:run=340:smd')
det = psana.Detector('MfxEndstation.0:Epix10ka2M.0')

for i, evt in enumerate(ds.events()):

    if i>10: break
    print 'Event %4d' % i

    raw = det.raw(evt)
    if raw is None:
        print '  raw is None'
        continue
    
    print_ndarr(raw,'  raw data')
