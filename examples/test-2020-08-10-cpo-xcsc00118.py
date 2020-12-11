from psana import *
ds = DataSource('exp=xcsc00118:run=56')
det = Detector('XcsEndstation.0:Epix10ka2M.0') #epix10k2M')
det.set_print_bits(0o377)

# /reg/d/psdm/xcs/xcsc00118/calib/Epix10ka2M::CalibV1/XcsEndstation.0:Epix10ka2M.0/pedestals/52-end.data
#EventKey(type=psana.Epix.ArrayV1, src='DetInfo(XcsEndstation.0:Epix10ka2M.0)', alias='epix10k2M')

for nevent,evt in enumerate(ds.events()):
    raw = det.raw(evt)
    if raw is None:
        print 'none'
        continue
    else:
        print raw.shape
    
    calib = det.calib(evt)
