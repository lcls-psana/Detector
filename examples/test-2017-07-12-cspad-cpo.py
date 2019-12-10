from __future__ import print_function
from psana import *
ds = DataSource('exp=xpptut15:run=54')
det = Detector('cspad')
evt = next(ds.events())
run = evt.run()
print(det.pedestals(run))
