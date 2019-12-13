from __future__ import print_function

from psana import DataSource
ds = DataSource('exp=detdaq17:run=111')
for nevt,evt in enumerate(ds.events()):
    print(list(evt.keys()))
    break

