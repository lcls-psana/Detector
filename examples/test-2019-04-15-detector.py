

from psana import DataSource, Detector
#import psana

#psana.setOption('psana.calib-dir', './calib')


#event_keys -d exp=xpptut15:run=460 -m3
#event_keys -d exp=mfxls4916:run=298 -m3


dsname = 'exp=mfxls4916:run=298' # '/reg/d/psdm/xpp/xpptut15/xtc/*'
#dsname = '/reg/g/psdm/detector/data_test/types/0028-NoDetector.0-Epix10ka2M.0.xtc'
#dsname = '/reg/g/psdm/data_test/types/Epix_ElementV3.xtc'
ds = DataSource(dsname)
evt = ds.events().next()
env = ds.env()

for key in evt.keys() : print key

#print 'env.epicsStore().names()', env.epicsStore().names() # epics.names()


ss = 'compound Jungfrau1M Jungfrau512k'

#amap = env.aliasMap()
#ss = 'Jungfrau1M'
#ss = 'Jungfrau512k'
#print ' amap', amap
#print ' amap.src(...)', amap.src(ss)

#det = Detector('Epix10ka2M') # src='DetInfo(NoDetector.0:Epix10ka2M.0)'
#det = Detector('XppGon.0:Cspad2x2.4') # src='DetInfo(NoDetector.0:Epix10ka2M.0)'

from Detector.PyDetector import map_alias_to_source, dettype


source_string = map_alias_to_source(ss, env)
print 'map_alias_to_source(ss, env)', source_string


dtype = dettype(source_string, env)
print 'dettype(source_string, env)', dtype
