#!/usr/bin/env python

from psana import *

#ds = DataSource('exp=cxi01516:run=21:smd') # Z=0  D.2:MMS.0 -3.918
#ds = DataSource('exp=cxi02416:run=8:smd') # Z=-400  D.2:MMS.0 -400.0022
#ds = DataSource('exp=cxic0915:run=45:smd') # Z=0  D.2:MMS.0 0.0
#epics_var = Detector('CXI:DS2:MMS:06.RBV')

ds = DataSource('/reg/g/psdm/detector/data_test/types/0003-CxiDs2.0-Cspad.0-fiber-data.xtc')
epics_var = Detector('CXI:DS1:MMS:06.RBV')

for nevent,evt in enumerate(ds.events()):
    print epics_var.name, epics_var() # prints D.1:MMS.0 -466.0022
    break
