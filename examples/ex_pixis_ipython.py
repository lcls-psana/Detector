from __future__ import print_function

#event_keys -d /reg/g/psdm/detector/data_test/xtc/mecdaq115-e993-r0174-s00-c00.xtc
#EventKey(type=psana.Pixis.FrameV1, src='DetInfo(MecTargetChamber.0:Pixis.1)', alias='pixis1')
#event_keys -d /reg/g/psdm/detector/data_test/xtc/mecdaq115-e993-r0174-s00-c00.xtc -m2
#EventKey(type=None, src='DetInfo(MecTargetChamber.0:Pixis.1)', alias='pixis1')
#EventKey(type=psana.Pixis.ConfigV1, src='DetInfo(MecTargetChamber.0:Pixis.1)', alias='pixis1')

import psana
dsname = '/reg/g/psdm/detector/data_test/xtc/mecdaq115-e993-r0174-s00-c00.xtc'
s_src = 'MecTargetChamber.0:Pixis.1'
print('Example for\n  dataset: %s\n  source : %s' % (dsname, s_src))

src = psana.Source(s_src)
ds  = psana.DataSource(dsname)
env = ds.env()
cfg = env.configStore()
co = cfg.get(psana.Pixis.ConfigV1, src)

print('dir(co)', dir(co))

print('co.height', co.height())
print('co.width ', co.width())
print('co.numPixelsX', co.numPixelsX())
print('co.numPixelsY', co.numPixelsY())


#r = ds.runs().next()
evt = next(ds.events())

evt=None
for i, evt in enumerate(ds.events()) :    
    if evt is None : print('Event %4d is None' % i)
    else :  
        print('Event %4d is NOT None' % i) 
        break


o = evt.get(psana.Pixis.FrameV1, src)

data = o.data()

#raw = det.raw(evt)
