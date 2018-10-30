
from psana import DataSource
ds = DataSource('exp=detdaq17:run=111')
for nevt,evt in enumerate(ds.events()):
    print evt.keys()
    break

