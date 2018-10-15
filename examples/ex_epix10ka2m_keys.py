
from psana import DataSource
ds = DataSource('/reg/g/psdm/detector/data_test/xtc/e0-r0003-s00-c00.xtc')
print '\n\nevt.keys():'
for nev, evt in enumerate(ds.events()): 
    if nev > 2 : break
    print 'Event #%2d' % nev
    for k in evt.keys() : print k

print '\n\nds.env().configStore().keys():'
for k in ds.env().configStore().keys() : print k

print ds.env().aliasMap().srcs()
