from __future__ import print_function

# Example of code for ipython

from pyimgalgos.GlobalUtils import print_ndarr
import psana
ds = psana.DataSource('/reg/g/psdm/detector/data_test/types/0032-NoDetector.0-Epix10kaQuad.0.xtc')
det = psana.Detector('NoDetector.0:Epix10kaQuad.0') # epix10kaquad
#det = psana.Detector('NoDetector.0:Epix10ka2M.0') # 'Epix10ka2M'
#psana.setOption('psana.calib-dir', '/reg/g/psdm/detector/alignment/cspad2x2/calib-cspad2x2-01-2013-02-13/calib')

evt=None
for i, evt in enumerate(ds.events()) :
    if i>100 : break
    raw = det.raw(evt)
    if raw is None:
        print(i, 'none')
        continue
    else:
        print_ndarr(raw, name='raw ', first=0, last=5)

runnum = 10
print_ndarr(det.pedestals(runnum), name='pedestals', first=0, last=5)

evt=next(ds.events())

#------------------------------

import psana
src = psana.Source('NoDetector.0:Epix10kaQuad.0')
ds = psana.DataSource('/reg/g/psdm/detector/data_test/types/0032-NoDetector.0-Epix10kaQuad.0.xtc')
env = ds.env()
r = next(ds.runs())
#evt = ds.events().next()

evt=None
for i, evt in enumerate(ds.events()) :
    if evt is None : print('Event %4d is None' % i)
    else :  
        print('Event %4d is NOT None' % i) 
        o = evt.get(psana.Epix.ArrayV1, src)
        print(o.frame().shape) # (4, 352, 384)
        break

cfg = env.configStore()
co = cfg.get(psana.Epix.Config10kaQuadV1, src)
#co = cfg.get(psana.Epix.Config10ka2MV1, src)

print('co.elemCfg(0):', co.elemCfg(0))
print('co.elemCfg_shape():', co.elemCfg_shape())
print('co.evr():', co.evr())
print('co.numberOfAsics():', co.numberOfAsics())
print('co.numberOfCalibrationRows():', co.numberOfCalibrationRows())
print('co.numberOfColumns():', co.numberOfColumns())
print('co.numberOfElements():', co.numberOfElements())
print('co.numberOfEnvironmentalRows():', co.numberOfEnvironmentalRows())
print('co.numberOfReadableRows():', co.numberOfReadableRows())
print('co.numberOfRows():', co.numberOfRows())
#print 'co.quad(0):', co.quad(0)
#print 'co.quad_shape():', co.quad_shape()
print('co.TypeId:', co.TypeId) # 120
print('co.Version:', co.Version)

for n in range(co.numberOfElements()) :
    print('Element # %2d' % n)
    elem = co.elemCfg(n)
    print('  elem:', elem, '  elem.numberOfAsics():', elem.numberOfAsics(), '  dir(elem):')
    for name in dir(elem) :
        if name[:2]=='__' : continue
        print('    ', name)

#------------------------------

    print('    len(asicPixelConfigArray): ', len(elem.asicPixelConfigArray()))

#------------------------------

asic00 = co.elemCfg(0).asics(0)
for name in dir(asic00) :
    if name[:2]=='__' : continue
    print('    ', name)

print('    ASIC chipID', asic00.chipID())
print('    ASIC trbit', asic00.trbit())

#------------------------------
