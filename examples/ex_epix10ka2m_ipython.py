
# Example of code for ipython

import psana
#ds = psana.DataSource('exp=mfxx32516:run=377')
ds = psana.DataSource('/reg/g/psdm/detector/data_test/xtc/e0-r0003-s00-c00.xtc')
det = psana.Detector('NoDetector.0:Epix10ka2M.0') # 'Epix10ka2M'
for i, evt in enumerate(ds.events()) :
    if i>100 : break
    raw = det.raw(evt)
    if raw is None:
        print i, 'none'
        continue
    else:
        print i, raw.shape

#------------------------------

import psana
dsname = '/reg/g/psdm/detector/data_test/xtc/e0-r0003-s00-c00.xtc'
s_src = 'NoDetector.0:Epix10ka2M.0'
print 'Example for\n  dataset: %s\n  source : %s' % (dsname, s_src)

src = psana.Source(s_src)
ds  = psana.DataSource(dsname)
env = ds.env()

r = ds.runs().next()
#evt = ds.events().next()

evt=None
for i, evt in enumerate(ds.events()) :    
    if evt is None : print 'Event %4d is None' % i
    else :  
        print 'Event %4d is NOT None' % i 
        o = evt.get(psana.Epix.ArrayV1, src)
        print o.frame().shape # (16, 352, 384)
        break

cfg = env.configStore()
co = cfg.get(psana.Epix.Config10ka2MV1, src)

print 'co.elemCfg(0):', co.elemCfg(0)
print 'co.elemCfg_shape():', co.elemCfg_shape()
print 'co.evr():', co.evr()
print 'co.numberOfAsics():', co.numberOfAsics()
print 'co.numberOfCalibrationRows():', co.numberOfCalibrationRows()
print 'co.numberOfColumns():', co.numberOfColumns()
print 'co.numberOfElements():', co.numberOfElements()
print 'co.numberOfEnvironmentalRows():', co.numberOfEnvironmentalRows()
print 'co.numberOfReadableRows():', co.numberOfReadableRows()
print 'co.numberOfRows():', co.numberOfRows()
print 'co.quad(0):', co.quad(0)
print 'co.quad_shape():', co.quad_shape()
print 'co.TypeId:', co.TypeId
print 'co.Version:', co.Version

for n in range(co.numberOfElements()) :
    print 'Element # %2d' % n
    elem = co.elemCfg(n)
    print '  elem:', elem, '  elem.numberOfAsics():', elem.numberOfAsics(), '  dir(elem):'
    for name in dir(elem) :
        if name[:2]=='__' : continue
        print '    ', name

    print '    len(asicPixelConfigArray): ', len(elem.asicPixelConfigArray())

for n in range(4) :
    print 'Element # %2d' % n
    q = co.quad(n)
    print '  quad:', q

#------------------------------

#det = psana.Detector(s_src, env)
#raw = det.raw(evt)
#raw.shape #Out[8]: ((352, 384)
#raw.dtype #Out[9]: dtype('uint16')

#evt = ds.events().next()
#dato = evt.get(psana.Epix.ElementV3, src)

#------------------------------

