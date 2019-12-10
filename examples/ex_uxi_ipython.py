from __future__ import print_function


from psana import DataSource
ds = DataSource('exp=detdaq17:run=111')
for nevt,evt in enumerate(ds.events()):
    print(evt.keys())
    break

import psana
dsname = 'exp=detdaq17:run=111'
s_src = 'DetLab.0:Uxi.0'
print('Example for\n  dataset: %s\n  source : %s' % (dsname, s_src))

src = psana.Source(s_src)
ds  = psana.DataSource(dsname)
env = ds.env()
cfg = env.configStore()
co = cfg.get(psana.Uxi.ConfigV1, src)

print('dir(co)', dir(co))
print('co.width  ', co.width())
print('co.height ', co.height())
print('co.numberOfFrames', co.numberOfFrames())
print('co.delay', co.delay())
print('co.frameSize', co.frameSize())
print('co.numberOFBytesPerPixel', co.numberOFBytesPerPixel())
print('co.NumberOfPots', co.NumberOfPots)
print('co.NumberOfSides', co.NumberOfSides)
print('co.numPixels', co.numPixels())
print('co.numPixelsPerFrame', co.numPixelsPerFrame())
print('co.potIsReadOnly ', co.potIsReadOnly(0))
print('co.pots', co.pots())
print('co.readOnlyPots', co.readOnlyPots())
print('co.sensorType', co.sensorType())
print('co.timeOff', co.timeOff())
print('co.timeOn', co.timeOn())
print('co.TypeId', co.TypeId)

#r = ds.runs().next()
evt = next(ds.events())

evt=None
for i, evt in enumerate(ds.events()) :    
    if evt is None : print('Event %4d is None' % i)
    else :  
        print('Event %4d is NOT None' % i) 
        break


o = evt.get(psana.Uxi.FrameV1, src)

data = o.frames()

#raw = det.raw(evt)
